from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# 1. Load configuration from the secret .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# 2. Build the main communication pipe to the database
engine = create_engine(DATABASE_URL)

# 3. Create a factory for individual database conversations
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 4. Create the base blueprint class for our future tables
Base = declarative_base()

# 5. Manage database traffic opening and closing safely
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()