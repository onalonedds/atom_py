from fastapi import FastAPI
from sqlalchemy.sql.ddl import CreateTable
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from . import models, routes

app = FastAPI()


async def create_tables(engine, metadata):
    async with engine.begin() as conn:
        for table in metadata.tables.values():
            create_expr = CreateTable(table)
            await conn.execute(create_expr)


# @app.on_event("startup")
# async def startup_event():
#     await create_tables(engine, models.Base.metadata)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Adjust this to the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routes.router)
