from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .database import get_db
from . import models, schemas, auth
from datetime import timedelta

router = APIRouter()


@router.post("/register", response_model=schemas.ClientResponse)
async def register(client: schemas.ClientCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Client).filter(models.Client.email == client.email))
    db_client = result.scalars().first()

    if db_client:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = auth.get_password_hash(client.password)
    new_client = models.Client(person_name=client.person_name, company_name=client.company_name, email=client.email,
                               hashed_password=hashed_password)
    db.add(new_client)

    await db.commit()
    await db.refresh(new_client)

    return new_client


@router.post("/login", response_model=schemas.Token)
async def login(form_data: schemas.ClientLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Client).filter(models.Client.email == form_data.email))
    user = result.scalars().first()

    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/profile", response_model=schemas.ClientBase)
async def read_users_me(payload: dict = Depends(auth.get_current_user), db: AsyncSession = Depends(get_db)):
    user_email = payload.get("sub")

    if user_email is None:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    result = await db.execute(select(models.Client).filter(models.Client.email == user_email))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return schemas.ClientBase(email=user.email, person_name=user.person_name, company_name=user.company_name)
