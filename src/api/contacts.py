from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.database.models import Contact, User
from src.schemas.contacts import ContactCreate, ContactResponse, ContactUpdate
from src.services.auth import get_current_user

router = APIRouter(prefix="/contacts", tags=["contacts"])

@router.get("/", response_model=List[ContactResponse])
async def get_contacts(limit: int = 10, offset: int = 0,
                       db: Session = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    contacts = db.query(Contact).filter(Contact.user_id == current_user.id).offset(offset).limit(limit).all()
    return contacts

@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int,
                      db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user.id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactCreate,
                         db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    contact = Contact(**body.dict(), user_id=current_user.id)
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact

@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(contact_id: int,
                         body: ContactUpdate,
                         db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user.id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    for field, value in body.dict().items():
        setattr(contact, field, value)
    db.commit()
    db.refresh(contact)
    return contact

@router.delete("/{contact_id}", response_model=ContactResponse)
async def delete_contact(contact_id: int,
                         db: Session = Depends(get_db),
                         current_user: User = Depends(get_current_user)):
    contact = db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user.id).first()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    db.delete(contact)
    db.commit()
    return contact
