from sqlmodel import create_engine, SQLModel


SQLITE_DATABASE_URL = "sqlite:///bot.db"
engine = create_engine(SQLITE_DATABASE_URL, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)