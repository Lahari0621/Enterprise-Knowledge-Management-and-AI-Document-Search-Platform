from backend.services.auth_service import hash_password, verify_password, create_token
from backend.models.models import User

def register_user(data,db):
    if db.query(User).filter(User.email==data['email']).first(): return None,'Email already registered'
    u=User(name=data['name'],email=data['email'],password_hash=hash_password(data['password']),role=data.get('role','Employee')); db.add(u); db.commit(); db.refresh(u); return u,None

def login_user(data,db):
    u=db.query(User).filter(User.email==data['email']).first()
    if not u or not verify_password(data['password'],u.password_hash): return None,'Invalid email or password'
    return {'access_token':create_token(u.id),'user':{'id':u.id,'name':u.name,'email':u.email,'role':u.role}},None
