from datetime import datetime

from models import Document, User
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session


##############
#  Users
##############
def hash_password(password: str) -> str:
    '''A fake password hashing function'''
    return password + '-fake-hash'


def create_user(db: Session, username: str, password: str) -> User:
    db_user = User(
        username=username,
        hashed_password=hash_password(password),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow())

    try:
        db.add(db_user)
        db.commit()
    except IntegrityError:
        db.rollback()
        return False, None, "User already exists"

    db.refresh(db_user)
    return True, db_user, "OK"


def login(db: Session, username: str, password: str) -> [bool, User]:
    '''Returns a tuple of (success, user, message)'''
    db_user = db.query(User).filter(User.username == username).first()
    if db_user is None:
        return False, None, "User does not exist"
    if db_user.hashed_password != hash_password(password):
        return False, None, "Incorrect password"
    return True, db_user, "OK"


def get_user(db: Session, user_id: int) -> User:
    return db.get(User, user_id)


def list_users(db: Session) -> list[User]:
    return db.query(User).all()


##############
#  Documents
##############
def create_document(
        db: Session, title: str, bucket_id: str, blob_id: str, owner_id: int) -> Document:

    db_document = Document(
        title=title,
        bucket_id=bucket_id,
        blob_id=blob_id,
        owner_id=owner_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


def list_documents(db: Session, owner_id: int) -> list[Document]:
    return db.query(Document).filter(Document.owner_id == owner_id).all()


def delete_document(db: Session, document_id: int) -> bool:
    db_document = db.query(Document).filter(Document.id == document_id).first()
    if db_document is None:
        return False
    db.delete(db_document)
    db.commit()
    return True


def get_document(db: Session, document_id: int) -> Document:
    return db.query(Document).filter(Document.id == document_id).first()

def update_document(db: Session, document_id: int, **kwargs):
    db_document = db.query(Document).filter(Document.id == document_id).first()
    if db_document is None:
        return False
    for key, value in kwargs.items():
        setattr(db_document, key, value)
    db_document.updated_at = datetime.utcnow()
    db.commit()
    return True


if __name__ == '__main__':
    from database import SessionLocal
    db = SessionLocal()
    print(list_users(db))
