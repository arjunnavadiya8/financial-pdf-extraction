# api_service.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, BackgroundTasks, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import shutil
from pydantic import BaseModel

# Import your modules
from enhanced_extractor import EnhancedIndianBankExtractor
from init_db import init_database, get_session
from db_models import User, BankStatement, Transaction, ExtractionLog, StatementStatus

# Initialize FastAPI
app = FastAPI(title="Financial Data Extraction API", version="1.0.0")

# Configuration
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize PDF extractor
extractor = EnhancedIndianBankExtractor()

# Initialize database at startup
init_database()

# --------------------------
# Pydantic models
# --------------------------
class UserCreate(BaseModel):
    username: str
    email: str

class TransactionQuery(BaseModel):
    user_id: Optional[int] = None
    statement_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    category: Optional[str] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None

class TransactionResponse(BaseModel):
    id: int
    transaction_date: datetime
    description: str
    debit_amount: Optional[float]
    credit_amount: Optional[float]
    balance: Optional[float]
    category: Optional[str]
    merchant: Optional[str]

    class Config:
        orm_mode = True

class StatementResponse(BaseModel):
    id: int
    filename: str
    bank_name: Optional[str]
    account_number: Optional[str]
    status: str
    transaction_count: int
    uploaded_at: datetime

    class Config:
        orm_mode = True

# --------------------------
# Database Dependency
# --------------------------
def get_db():
    return next(get_session())

# --------------------------
# Background PDF Processing
# --------------------------
def process_pdf_background(file_path: str, statement_id: int, db: Session):
    """Background task to process PDF asynchronously"""
    try:
        statement = db.query(BankStatement).filter(BankStatement.id == statement_id).first()
        statement.status = StatementStatus.PROCESSING
        db.commit()

        extracted_data = extractor.process_pdf(file_path)

        if "error" in extracted_data:
            statement.status = StatementStatus.FAILED
            statement.error_message = extracted_data["error"]
            db.commit()
            return

        # Update bank statement info
        bank_info = extracted_data["bank_info"]
        statement.bank_name = bank_info.get("bank_name")
        statement.account_number = bank_info.get("account_number")

        balances = extracted_data["balances"]
        statement.opening_balance = balances.get("opening_balance")
        statement.closing_balance = balances.get("closing_balance")

        # Save transactions
        for txn_data in extracted_data["transactions"]:
            transaction = Transaction(
                statement_id=statement_id,
                transaction_date=txn_data["transaction_date"],
                description=txn_data["description"],
                debit_amount=txn_data.get("debit_amount"),
                credit_amount=txn_data.get("credit_amount"),
                balance=txn_data.get("balance"),
                transaction_type=txn_data.get("transaction_type"),
                category=txn_data.get("category"),
                merchant=txn_data.get("merchant"),
                confidence_score=txn_data.get("confidence_score")
            )
            db.add(transaction)

        statement.status = StatementStatus.COMPLETED
        statement.processed_at = datetime.utcnow()
        db.commit()

        # Log success
        log = ExtractionLog(
            statement_id=statement_id,
            log_type="info",
            message=f"Successfully extracted {len(extracted_data['transactions'])} transactions"
        )
        db.add(log)
        db.commit()

    except Exception as e:
        statement = db.query(BankStatement).filter(BankStatement.id == statement_id).first()
        statement.status = StatementStatus.FAILED
        statement.error_message = str(e)
        db.commit()

        log = ExtractionLog(
            statement_id=statement_id,
            log_type="error",
            message=str(e)
        )
        db.add(log)
        db.commit()

# --------------------------
# API Endpoints
# --------------------------
@app.post("/api/users/", response_model=dict)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")
    new_user = User(username=user.username, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "username": new_user.username, "email": new_user.email}

@app.post("/api/upload-statement/")
async def upload_statement(
    user_id: int,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    file_path = os.path.join(UPLOAD_DIR, f"{user_id}_{datetime.now().timestamp()}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    statement = BankStatement(
        user_id=user_id,
        filename=file.filename,
        file_path=file_path,
        status=StatementStatus.PENDING
    )
    db.add(statement)
    db.commit()
    db.refresh(statement)

    background_tasks.add_task(process_pdf_background, file_path, statement.id, db)
    return {"message": "File uploaded successfully. Processing started.", "statement_id": statement.id, "status": "pending"}

@app.get("/api/statements/{statement_id}", response_model=StatementResponse)
async def get_statement(statement_id: int, db: Session = Depends(get_db)):
    statement = db.query(BankStatement).filter(BankStatement.id == statement_id).first()
    if not statement:
        raise HTTPException(status_code=404, detail="Statement not found")
    txn_count = db.query(Transaction).filter(Transaction.statement_id == statement_id).count()
    return StatementResponse(
        id=statement.id,
        filename=statement.filename,
        bank_name=statement.bank_name,
        account_number=statement.account_number,
        status=statement.status.value,
        transaction_count=txn_count,
        uploaded_at=statement.uploaded_at
    )

@app.post("/api/transactions/query", response_model=List[TransactionResponse])
async def query_transactions(query: TransactionQuery, db: Session = Depends(get_db)):
    q = db.query(Transaction)
    if query.statement_id:
        q = q.filter(Transaction.statement_id == query.statement_id)
    if query.user_id:
        q = q.join(BankStatement).filter(BankStatement.user_id == query.user_id)
    if query.start_date:
        q = q.filter(Transaction.transaction_date >= query.start_date)
    if query.end_date:
        q = q.filter(Transaction.transaction_date <= query.end_date)
    if query.category:
        q = q.filter(Transaction.category == query.category)
    if query.min_amount:
        q = q.filter((Transaction.debit_amount >= query.min_amount) | (Transaction.credit_amount >= query.min_amount))
    if query.max_amount:
        q = q.filter((Transaction.debit_amount <= query.max_amount) | (Transaction.credit_amount <= query.max_amount))
    transactions = q.order_by(Transaction.transaction_date.desc()).all()
    return [TransactionResponse.from_orm(t) for t in transactions]

@app.get("/api/users/{user_id}/statements", response_model=List[StatementResponse])
async def get_user_statements(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    statements = db.query(BankStatement).filter(BankStatement.user_id == user_id).all()
    result = []
    for stmt in statements:
        txn_count = db.query(Transaction).filter(Transaction.statement_id == stmt.id).count()
        result.append(StatementResponse(
            id=stmt.id,
            filename=stmt.filename,
            bank_name=stmt.bank_name,
            account_number=stmt.account_number,
            status=stmt.status.value,
            transaction_count=txn_count,
            uploaded_at=stmt.uploaded_at
        ))
    return result

@app.get("/api/analytics/spending-by-category/{user_id}")
async def get_spending_by_category(user_id: int, db: Session = Depends(get_db)):
    transactions = db.query(Transaction).join(BankStatement).filter(
        BankStatement.user_id == user_id,
        Transaction.debit_amount.isnot(None)
    ).all()
    category_totals = {}
    for txn in transactions:
        category = txn.category or "other"
        category_totals[category] = category_totals.get(category, 0) + txn.debit_amount
    return {"user_id": user_id, "spending_by_category": category_totals, "total_spending": sum(category_totals.values())}

@app.get("/api/transactions/by-month/", response_model=List[TransactionResponse])
async def list_transactions_by_month(
    user_id: int,
    year: int = Query(..., description="Year, e.g. 2025"),
    month: int = Query(..., description="Month (1-12)"),
    db: Session = Depends(get_db)
):
    """List transactions for a given user and month."""
    start = datetime(year, month, 1)
    if month == 12:
        end = datetime(year + 1, 1, 1)
    else:
        end = datetime(year, month + 1, 1)
    q = db.query(Transaction).join(BankStatement).filter(
        BankStatement.user_id == user_id,
        Transaction.transaction_date >= start,
        Transaction.transaction_date < end
    )
    transactions = q.order_by(Transaction.transaction_date.desc()).all()
    return [TransactionResponse.from_orm(t) for t in transactions]

@app.get("/api/transactions/by-category/", response_model=List[TransactionResponse])
async def list_transactions_by_category(
    user_id: int,
    category: str,
    db: Session = Depends(get_db)
):
    """Filter transactions by category for a user."""
    q = db.query(Transaction).join(BankStatement).filter(
        BankStatement.user_id == user_id,
        Transaction.category == category
    )
    transactions = q.order_by(Transaction.transaction_date.desc()).all()
    return [TransactionResponse.from_orm(t) for t in transactions]

@app.get("/api/transactions/total-credit-debit/")
async def get_total_credit_debit(
    user_id: int,
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db)
):
    """Get total credit and debit for a user in a time period."""
    q = db.query(Transaction).join(BankStatement).filter(
        BankStatement.user_id == user_id,
        Transaction.transaction_date >= start_date,
        Transaction.transaction_date <= end_date
    )
    total_credit = 0.0
    total_debit = 0.0
    for txn in q:
        if txn.credit_amount:
            total_credit += txn.credit_amount
        if txn.debit_amount:
            total_debit += txn.debit_amount
    return {
        "user_id": user_id,
        "start_date": start_date,
        "end_date": end_date,
        "total_credit": total_credit,
        "total_debit": total_debit
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
