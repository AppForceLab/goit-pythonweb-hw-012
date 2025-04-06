from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.database.models import Contact
from src.schemas.contacts import ContactCreate, ContactUpdate


async def create_contact(contact: ContactCreate, db: AsyncSession):
    db_contact = Contact(**contact.model_dump())
    db.add(db_contact)
    await db.commit()
    await db.refresh(db_contact)
    return db_contact

async def get_contact(contact_id: int, db: AsyncSession):
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    return result.scalar_one_or_none()

async def get_contacts(skip: int, limit: int, search: str, db: AsyncSession):
    query = select(Contact)
    if search:
        query = query.filter(
            (Contact.first_name.ilike(f"%{search}%")) |
            (Contact.last_name.ilike(f"%{search}%")) |
            (Contact.email.ilike(f"%{search}%"))
        )
    result = await db.execute(query.offset(skip).limit(limit))
    return result.scalars().all()

async def update_contact(contact_id: int, contact: ContactUpdate, db: AsyncSession):
    db_contact = await get_contact(contact_id, db)
    if db_contact:
        for key, value in contact.model_dump().items():
            setattr(db_contact, key, value)
        await db.commit()
        await db.refresh(db_contact)
    return db_contact

async def delete_contact(contact_id: int, db: AsyncSession):
    db_contact = await get_contact(contact_id, db)
    if db_contact:
        await db.delete(db_contact)
        await db.commit()
    return db_contact

async def get_upcoming_birthdays(db: AsyncSession):
    today = date.today()
    next_week = today + timedelta(days=7)
    query = select(Contact).where(Contact.birthday.between(today, next_week))
    result = await db.execute(query)
    return result.scalars().all()
