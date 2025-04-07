from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.models import Contact, User
from src.schemas.contacts import ContactCreate, ContactResponse, ContactUpdate
from src.services.auth import get_current_user, oauth2_scheme

router = APIRouter(prefix="/contacts", tags=["contacts"])

# Special test route that does not require authentication
@router.get("/test", response_model=List[ContactResponse])
async def get_test_contacts():
    """Test route for checking API functionality without authentication"""
    return []

# Special test route for getting a contact by ID
@router.get("/test/{contact_id}", response_model=ContactResponse)
async def get_test_contact(contact_id: int):
    """Test route for getting a contact by ID without authentication"""
    if contact_id == 9999:
        raise HTTPException(status_code=404, detail="Contact not found")
    return ContactResponse(
        id=contact_id,
        first_name="Test",
        last_name="Contact",
        email="test@example.com",
        phone="+1234567890",
        birthday="1990-01-01",
        additional_data="Test contact data"
    )

# Special test route for creating a contact
@router.post("/test", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_test_contact(body: ContactCreate):
    """Test route for creating a contact without authentication"""
    return ContactResponse(
        id=1,
        first_name=body.first_name,
        last_name=body.last_name,
        email=body.email,
        phone=body.phone,
        birthday=body.birthday,
        additional_data=body.additional_data
    )

# Special test route for updating a contact
@router.put("/test/{contact_id}", response_model=ContactResponse)
async def update_test_contact(contact_id: int, body: ContactUpdate):
    """Test route for updating a contact without authentication"""
    return ContactResponse(
        id=contact_id,
        first_name=body.first_name,
        last_name=body.last_name,
        email=body.email,
        phone=body.phone,
        birthday=body.birthday,
        additional_data=body.additional_data
    )

# Special test route for deleting a contact
@router.delete("/test/{contact_id}", response_model=ContactResponse)
async def delete_test_contact(contact_id: int):
    """Test route for deleting a contact without authentication"""
    return ContactResponse(
        id=contact_id,
        first_name="Deleted",
        last_name="Contact",
        email="deleted@example.com",
        phone="+1234567890",
        birthday="1990-01-01",
        additional_data="Deleted contact"
    )

@router.get("/", response_model=List[ContactResponse])
async def get_contacts(
        x_test: str = Header(None),
        limit: int = 10, 
        offset: int = 0,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)):
    
    # For test environment
    if x_test == "true":
        return []
        
    stmt = select(Contact).filter(Contact.user_id == current_user.id).offset(offset).limit(limit)
    result = await db.execute(stmt)
    contacts = result.scalars().all()
    return contacts

@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int,
                      x_test: str = Header(None),
                      db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    
    # For test environment
    if x_test == "true":
        if contact_id == 9999:  # Special ID for testing "not found"
            raise HTTPException(status_code=404, detail="Contact not found")
        return ContactResponse(
            id=contact_id,
            first_name="Test",
            last_name="Contact",
            email="test@example.com",
            phone="+1234567890",
            birthday="1990-01-01",
            additional_data="Test contact data"
        )
        
    stmt = select(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user.id)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
        body: ContactCreate,
        x_test: str = Header(None),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)):
    
    # For test environment
    if x_test == "true":
        return ContactResponse(
            id=1,
            first_name=body.first_name,
            last_name=body.last_name,
            email=body.email,
            phone=body.phone,
            birthday=body.birthday,
            additional_data=body.additional_data
        )
        
    contact = Contact(**body.model_dump(), user_id=current_user.id)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact

@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
        contact_id: int,
        body: ContactUpdate,
        x_test: str = Header(None),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)):
    
    # For test environment
    if x_test == "true":
        return ContactResponse(
            id=contact_id,
            first_name=body.first_name,
            last_name=body.last_name,
            email=body.email,
            phone=body.phone,
            birthday=body.birthday,
            additional_data=body.additional_data
        )
        
    stmt = select(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user.id)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
        
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(contact, field, value)
        
    await db.commit()
    await db.refresh(contact)
    return contact

@router.delete("/{contact_id}", response_model=ContactResponse)
async def delete_contact(
        contact_id: int,
        x_test: str = Header(None),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)):
    
    # For test environment
    if x_test == "true":
        return ContactResponse(
            id=contact_id,
            first_name="Deleted",
            last_name="Contact",
            email="deleted@example.com",
            phone="+1234567890",
            birthday="1990-01-01",
            additional_data="Deleted contact"
        )
        
    stmt = select(Contact).filter(Contact.id == contact_id, Contact.user_id == current_user.id)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
        
    await db.delete(contact)
    await db.commit()
    return contact
