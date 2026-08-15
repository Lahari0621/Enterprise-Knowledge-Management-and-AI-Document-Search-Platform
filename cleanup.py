from pathlib import Path
from database.database import SessionLocal
from backend.models.models import Document

# -----------------------------------------
# SETTINGS
# -----------------------------------------

UPLOAD_DIR = Path("./uploads")

db = SessionLocal()

try:
    print("\n========== DOCUMENT CLEANUP ==========\n")

    # Get all documents
    documents = (
        db.query(Document)
        .order_by(Document.created_at.desc())
        .all()
    )

    print(f"Documents currently in database: {len(documents)}")

    # -----------------------------------------
    # 1. REMOVE DUPLICATE DATABASE RECORDS
    # -----------------------------------------

    seen = set()
    deleted_documents = []

    for document in documents:

        key = (
            document.filename.lower(),
            document.uploaded_by
        )

        if key in seen:
            print(
                f"Deleting duplicate database record: "
                f"{document.filename} "
                f"(ID: {document.id})"
            )

            # Delete physical file belonging to duplicate
            file_path = UPLOAD_DIR / document.stored_name

            if file_path.exists():
                file_path.unlink()
                print(f"  Deleted file: {file_path.name}")

            db.delete(document)
            deleted_documents.append(document.id)

        else:
            seen.add(key)

    db.commit()

    # -----------------------------------------
    # 2. FIND FILES ACTUALLY USED BY DATABASE
    # -----------------------------------------

    remaining_documents = db.query(Document).all()

    used_files = {
        document.stored_name
        for document in remaining_documents
    }

    # -----------------------------------------
    # 3. DELETE ORPHAN FILES
    # -----------------------------------------

    orphan_count = 0

    if UPLOAD_DIR.exists():

        for file_path in UPLOAD_DIR.iterdir():

            if file_path.is_file():

                if file_path.name not in used_files:

                    print(
                        f"Deleting unused upload: "
                        f"{file_path.name}"
                    )

                    file_path.unlink()
                    orphan_count += 1

    # -----------------------------------------
    # 4. FINAL RESULT
    # -----------------------------------------

    print("\n========== CLEANUP COMPLETE ==========")

    print(
        f"Remaining database documents: "
        f"{len(remaining_documents)}"
    )

    print(
        f"Deleted duplicate records: "
        f"{len(deleted_documents)}"
    )

    print(
        f"Deleted unused files: "
        f"{orphan_count}"
    )

    print("\nYour database and uploads folder are now synchronized.")

finally:
    db.close()