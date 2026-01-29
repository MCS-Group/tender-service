from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv
import os


load_dotenv()


def get_cola_sqlalchemy_repository():
    conn_str = os.getenv("DATABASE_URI", "sqlite:///products.db")
    engine = create_engine(conn_str)
    # Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)