from doctest import Example
import email
from tokenize import String
import databases
import datetime
import uuid
import sqlalchemy
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from typing import List


DATABASE_URL = "postgresql://usertest:usertest222@127.0.0.1:5432/dbtest"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

users = sqlalchemy.Table(
    "py_users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("email", sqlalchemy.String),
    sqlalchemy.Column("password", sqlalchemy.String)
)

engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)


class UserList(BaseModel):
    id: int
    email: str
    password: str


class UserEntry(BaseModel):
    email: str = Field(..., example="abc@gmail.com")
    password: str = Field(..., example="abc123")


class UserUpdate(BaseModel):
    id: int = Field(..., example="Enter your id")
    email: str = Field(..., example="abc@gmail.com")
    password: str = Field(..., example="abc123")


class UserDelete(BaseModel):
    id: int = Field(..., example="Enter your id")


tags_metadata = [
    {
        "name": "users",
        "description": "Operations with users. The **login** logic is also here.",
    },
    {
        "name": "items",
        "description": "Manage items. So _fancy_ they have their own docs.",
        "externalDocs": {
            "description": "Items external docs",
            "url": "https://localhost:8000/",
        },
    },
]

app = FastAPI()


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/", tags=["items"])
async def root():
    query = users.select()
    return await database.fetch_all(query)


@app.get("/users", response_model=List[UserList], tags=["items"])
async def find_all_users():
    query = users.select()
    return await database.fetch_all(query)


@app.post("/users", response_model=UserList)
async def register_user(user: UserEntry):
    gID = str(uuid.uuid1())
    gDate = str(datetime.datetime.now())
    query = users.insert().values(
        email=user.email,
        password=user.password
    )
    await database.execute(query)
    return {
        "id": gID, **user.dict(),
    }


@app.get("/users/{user_id}", response_model=UserList)
async def find_user_by_id(userId: int):
    query = users.select().where(users.c.id == userId)
    return await database.fetch_one(query)


@app.put("/users", response_model=UserList)
async def update_user(user: UserUpdate):
    query = users.update().\
        where(users.c.id == user.id).\
        values(
            email=user.email,
            password=user.password
    )
    await database.execute(query)

    return await find_user_by_id(user.id)


# @app.delete("users/{user_id}")
# async def delete_user(user: UserDelete):
#     query = users.delete().where(users.c.id == int(user.id))
#     await database.execute(query)
#     return {
#         "status": True,
#         "message": "This user has been deleted successfully"
#     }
