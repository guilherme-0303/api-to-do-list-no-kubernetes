from sqlalchemy import create_engine
from sqlalchemy.orm import registry, sessionmaker, Session, declarative_base
from app.core.settings import Settings


settings = Settings()

user = settings.POSTGRES_USER
password = settings.POSTGRES_PASSWORD
host = settings.POSTGRES_HOST
db = settings.POSTGRES_DB
port = 5432
dialect = "postgresql+psycopg"

DATABASE_URL = f"{dialect}://{user}:{password}@{host}:{port}/{db}"

engine = create_engine(DATABASE_URL)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_session():
    with Session() as session:
        yield session
