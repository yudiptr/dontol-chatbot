from sqlalchemy.orm import Session
from models import InternalDoc

def get_all_docs(db: Session):
    return db.query(InternalDoc).all()
