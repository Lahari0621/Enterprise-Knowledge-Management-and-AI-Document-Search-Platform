import os
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Header
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database.database import Base, engine, get_db
from backend.models.models import User, Document
from backend.services.auth_service import hash_password, verify_password, create_token, decode_user_id
from backend.services.document_service import extract_text
from ai.search_engine.search import rank_documents
import uuid
from fastapi.responses import FileResponse


Base.metadata.create_all(bind=engine)
UPLOAD_DIR=Path(os.getenv('UPLOAD_DIR','./uploads')); UPLOAD_DIR.mkdir(parents=True,exist_ok=True)
app=FastAPI(
    title='Enterprise Knowledge Management and AI Document Search Platform',
    version='1.0.0',
    description='Backend API for enterprise document management and AI-powered search.'
)
app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])

def user_from_header(authorization,db):
    if not authorization or not authorization.startswith('Bearer '): raise HTTPException(401,'Login required')
    uid=decode_user_id(authorization.split(' ',1)[1]); user=db.get(User,uid) if uid else None
    if not user: raise HTTPException(401,'Invalid token')
    return user

@app.get('/health')
def health(): return {'status':'ok'}

@app.post('/api/auth/register')
def register(data:dict,db:Session=Depends(get_db)):
    if db.query(User).filter(User.email==data['email']).first(): raise HTTPException(409,'Email already registered')
    roles={'Employee','Administrator','Knowledge Manager','Department Manager','IT Team'}
    role=data.get('role','Employee') if data.get('role','Employee') in roles else 'Employee'
    u=User(name=data['name'],email=data['email'],password_hash=hash_password(data['password']),role=role); db.add(u); db.commit(); db.refresh(u)
    return {'message':'Registration successful','user_id':u.id}

@app.post('/api/auth/login')
def login(data:dict,db:Session=Depends(get_db)):
    u=db.query(User).filter(User.email==data['email']).first()
    if not u or not verify_password(data['password'],u.password_hash): raise HTTPException(401,'Invalid email or password')
    return {'access_token':create_token(u.id),'token_type':'bearer','user':{'id':u.id,'name':u.name,'email':u.email,'role':u.role}}

@app.get('/api/me')
def me(authorization:str|None=Header(default=None),db:Session=Depends(get_db)):
    u=user_from_header(authorization,db); return {'id':u.id,'name':u.name,'email':u.email,'role':u.role}

@app.post('/api/documents/upload')
def upload(
    file: UploadFile = File(...),
    category: str = 'General',
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db)
):
    u = user_from_header(authorization, db)

    original = file.filename or 'document.txt'
    suffix = Path(original).suffix.lower()

    if suffix not in {'.txt', '.pdf', '.docx'}:
        raise HTTPException(
            400,
            'Supported file types: TXT, PDF, DOCX'
        )

    # Prevent duplicate filenames
    existing = db.query(Document).filter(
        Document.filename == original
    ).first()

    if existing:
        raise HTTPException(
            409,
            f'{original} already exists. Delete the existing document before uploading it again.'
        )

    # Read uploaded file
    file_bytes = file.file.read()

    # Generate unique storage name
    stored = uuid.uuid4().hex + suffix

    path = UPLOAD_DIR / stored

    # Save physical file
    path.write_bytes(file_bytes)

    # Extract text
    content = extract_text(
        str(path),
        original
    )

    # Save database record
    d = Document(
        title=Path(original).stem,
        filename=original,
        stored_name=stored,
        content=content,
        uploaded_by=u.id,
        category=category or 'General'
    )

    db.add(d)
    db.commit()
    db.refresh(d)

    return {
        'message': 'Document uploaded successfully',
        'document_id': d.id
    }

@app.get('/api/documents')
def documents(authorization:str|None=Header(default=None),db:Session=Depends(get_db)):
    user_from_header(authorization,db); ds=db.query(Document).order_by(Document.created_at.desc()).all()
    return [{'id':d.id,'title':d.title,'filename':d.filename,'category':d.category,'created_at':d.created_at.isoformat() if d.created_at else ''} for d in ds]

@app.get('/api/documents/{document_id}/download')
def download(
    document_id: int,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db)
):
    from fastapi.responses import FileResponse

    # Check login
    user_from_header(authorization, db)

    # Find document in database
    d = db.get(Document, document_id)

    if not d:
        raise HTTPException(status_code=404, detail="Document not found")

    # IMPORTANT: database column is stored_name
    path = UPLOAD_DIR / d.stored_name

    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Stored file not found: {path}"
        )

    return FileResponse(
        path=str(path),
        filename=d.filename,
        media_type="application/octet-stream"
    )

@app.delete('/api/documents/{document_id}')
def delete_document(
    document_id: int,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db)
):
    user_from_header(authorization, db)

    d = db.get(Document, document_id)

    if not d:
        raise HTTPException(404, 'Document not found')

    # Delete physical file
    path = UPLOAD_DIR / d.stored_name

    if path.exists():
        path.unlink()

    # Delete database record
    db.delete(d)
    db.commit()

    return {
        'message': 'Document deleted successfully'
    }

@app.get('/api/search')
def search(q:str,authorization:str|None=Header(default=None),db:Session=Depends(get_db)):
    user_from_header(authorization,db); ranked=rank_documents(q,db.query(Document).all())
    return [{'id':d.id,'title':d.title,'filename':d.filename,'category':d.category,'score':round(score*100,2)} for d,score in ranked]



"""
 cd frontend
  python -m http.server 5500
  http://localhost:5500/
    cd backend
    venv\Scripts\activate
    uvicorn backend.main:app --reload
    jenkins= http://localhost:8080

"""