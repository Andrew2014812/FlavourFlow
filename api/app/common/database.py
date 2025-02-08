from typing import Annotated

import api.app.users.models  # noqa
from fastapi import Depends
from sqlmodel import create_engine, SQLModel, Session

from application.config import db_name, db_user, db_password, db_host, db_port

SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
)

engine = create_engine(SQLALCHEMY_DATABASE_URL)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Session:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
