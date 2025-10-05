
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import enum

Base = declarative_base()

class StatementStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    bank_statements = relationship("BankStatement", back_populates="user", cascade="all, delete-orphan")

class BankStatement(Base):
    __tablename__ = 'bank_statements'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    bank_name = Column(String(100))
    account_number = Column(String(50))
    statement_period_start = Column(DateTime)
    statement_period_end = Column(DateTime)
    opening_balance = Column(Float)
    closing_balance = Column(Float)
    status = Column(Enum(StatementStatus), default=StatementStatus.PENDING)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    error_message = Column(Text)
    
    # Relationships
    user = relationship("User", back_populates="bank_statements")
    transactions = relationship("Transaction", back_populates="statement", cascade="all, delete-orphan")

class Transaction(Base):
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True)
    statement_id = Column(Integer, ForeignKey('bank_statements.id'), nullable=False)
    transaction_date = Column(DateTime, nullable=False)
    description = Column(Text, nullable=False)
    debit_amount = Column(Float)
    credit_amount = Column(Float)
    balance = Column(Float)
    transaction_type = Column(String(50))  # debit, credit, transfer, fee, etc.
    category = Column(String(100))  # food, transport, salary, etc.
    merchant = Column(String(255))
    reference_number = Column(String(100))
    extracted_at = Column(DateTime, default=datetime.utcnow)
    confidence_score = Column(Float)  # ML confidence score
    
    # Relationships
    statement = relationship("BankStatement", back_populates="transactions")

class ExtractionLog(Base):
    __tablename__ = 'extraction_logs'
    
    id = Column(Integer, primary_key=True)
    statement_id = Column(Integer, ForeignKey('bank_statements.id'))
    log_type = Column(String(50))  # info, warning, error
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

# Database initialization
def init_db(database_url="mysql+pymysql://root:password@localhost:3306/financedb"):
    engine = create_engine(database_url, echo=True, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    return engine

def get_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()

# Create database if not exists
def create_database():
    from sqlalchemy import create_engine, text
    engine = create_engine("mysql+pymysql://financeuser:SecurePassword123!@localhost:3306/financedb", echo=True)
    with engine.connect() as conn:
        conn.execute(text("CREATE DATABASE IF NOT EXISTS financedb"))
        conn.commit()