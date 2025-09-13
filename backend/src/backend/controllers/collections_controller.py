from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from backend.config.database import get_session
from backend.models.models import Collection
from backend.models.dtos.collection import CollectionDTO
from typing import List

router = APIRouter(prefix="/collections", tags=["collections"])

@router.get("/", response_model=List[CollectionDTO])
def list_collections(session: Session = Depends(get_session)):
    collections = session.exec(select(Collection)).all()
    return [CollectionDTO(id=str(collection.id), name=collection.name) for collection in collections]

@router.post("/", response_model=CollectionDTO)
def create_collection(collection: CollectionDTO, session: Session = Depends(get_session)):
    db_collection = Collection(name=collection.name)
    session.add(db_collection)
    session.commit()
    session.refresh(db_collection)
    return CollectionDTO(id=str(db_collection.id), name=db_collection.name)

@router.put("/{collection_id}", response_model=CollectionDTO)
def update_collection(collection_id: str, collection: CollectionDTO, session: Session = Depends(get_session)):
    db_collection = session.get(Collection, collection_id)
    if not db_collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    db_collection.name = collection.name
    session.add(db_collection)
    session.commit()
    session.refresh(db_collection)
    return CollectionDTO(id=str(db_collection.id), name=db_collection.name)

@router.delete("/{collection_id}", response_model=dict)
def delete_collection(collection_id: str, session: Session = Depends(get_session)):
    db_collection = session.get(Collection, collection_id)
    if not db_collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    session.delete(db_collection)
    session.commit()
    return {"detail": "Collection deleted"}
