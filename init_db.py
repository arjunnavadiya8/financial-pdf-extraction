# init_db.py
"""
Database Initialization Script
Run this to create tables and setup the database
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from db_models import Base, create_database
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv(
    'DATABASE_URL', 
    'mysql+pymysql://financeuser:SecurePassword123!@localhost:3306/financedb'
)

# Create SQLAlchemy engine and session
engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

def init_database():
    """Initialize the database and tables"""
    print("Starting database initialization...")
    try:
        create_database()  # create DB if not exists
        print("✓ Database created/verified")

        print("Creating tables...")
        Base.metadata.create_all(engine)
        print("✓ All tables created successfully")

        # Verify tables
        with engine.connect() as conn:
            result = conn.execute(text("SHOW TABLES"))
            tables = [row[0] for row in result]
            print(f"\n✓ Created tables: {', '.join(tables)}")

        print("\n✅ Database initialization completed successfully!")

    except Exception as e:
        print(f"\n❌ Error during initialization: {e}")

# Function to get DB session
def get_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Run only if executed directly
if __name__ == "__main__":
    init_database()
