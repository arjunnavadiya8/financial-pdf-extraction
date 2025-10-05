# Financial PDF Data Extraction System

AI-powered system for extracting structured transaction data from Indian bank statement PDFs using Machine Learning, Natural Language Processing, and MySQL database.

## Features

- **Multi-Bank Support**: HDFC Bank, Indian Bank, and generic format extraction
- **AI-Powered Extraction**: Uses spaCy NER and Transformers for intelligent parsing
- **Automatic Categorization**: ML-based transaction classification into 16 categories
- **RESTful API**: FastAPI backend with Swagger documentation
- **MySQL Database**: Structured storage with user isolation
- **Background Processing**: Asynchronous PDF processing for better performance
- **Transaction Analytics**: Spending analysis by category, merchant, and date range

## Tech Stack

- **Backend**: Python 3.9+, FastAPI 0.104.1
- **Database**: MySQL 8.0 with SQLAlchemy ORM
- **PDF Processing**: pdfplumber 0.10.3
- **ML/NLP**: spaCy 3.7.2, Transformers 4.35.2
- **API Documentation**: Swagger UI (auto-generated)

## Project Structure

```
financial-pdf-extraction/
│
├── data/
│   └── sample_pdfs/              # Sample bank statements
│       ├── IndianBank.pdf
│       ├── hdfc-demo.pdf
│       └── icici.pdf
│
├── uploads/                      # Uploaded PDFs (auto-created)
├── extracted/                    # JSON outputs (auto-created)
├── logs/                         # Application logs
│
├── enhanced_extractor.py         # PDF extraction engine with ML/NLP
├── db_models.py                  # SQLAlchemy database models
├── api_service.py                # FastAPI application
├── init_db.py                    # Database initialization script
├── test_extraction.py            # PDF extraction testing tool
│
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables
├── .gitignore                    # Git ignore rules
├── README.md                     # This file
└── extracted_transaction.json       # API testing collection
```

## Installation

### Prerequisites

- Python 3.8 or higher
- MySQL 8.0 or higher
- pip package manager

### Step 1: Clone & Setup

```bash
# Create project directory
mkdir financial-pdf-extraction
cd financial-pdf-extraction

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt

# Download spaCy language model
python -m spacy download en_core_web_sm
```

### Step 3: Setup MySQL Database

```bash
# Start MySQL
# Windows: Start MySQL service from Services
# Linux: sudo systemctl start mysql

# Login to MySQL
mysql -u root -p
```

Run these SQL commands:

```sql
CREATE DATABASE financedb CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'financeuser'@'localhost' IDENTIFIED BY 'SecurePassword123!';
GRANT ALL PRIVILEGES ON financedb.* TO 'financeuser'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Step 4: Configure Environment

Create `.env` file in project root:

```env
DATABASE_URL=mysql+pymysql://financeuser:SecurePassword123!@localhost:3306/financedb
SECRET_KEY=your-secret-key-change-in-production
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=pdf
```

### Step 5: Initialize Database

```bash
python init_db.py
```

You should see:
```
✓ Database created/verified
✓ All tables created successfully
✓ Created tables: users, bank_statements, transactions, extraction_logs
Database initialization completed successfully!
```

## Usage

### Test PDF Extraction (Standalone)

```bash
# Test on sample PDFs
python test_extraction.py --pdf "data/sample_pdfs/hdfc-demo.pdf"
python test_extraction.py --pdf "data/sample_pdfs/IndianBank.pdf"
```

**Output:**
```
✓ Bank Type: HDFC
✓ Account Number: 00392820000014
✓ Total Transactions Extracted: 139

Transaction Summary:
   Total Debits:  ₹16,263,444.72
   Total Credits: ₹15,195,644.75

Category Breakdown:
   fuel          : 42 txns | Dr: ₹12,850,000.00
   transfer      : 35 txns | Cr: ₹3,456,789.00
   ...
```

### Start API Server

```bash
uvicorn api_service:app --reload --host 0.0.0.0 --port 8000
```

Server starts at: `http://0.0.0.0:8000`

API Documentation: `/docs`

### API Usage Examples

#### Create User

```bash
curl -X POST "http://0.0.0.0:8000/api/users/" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"john_doe\",\"email\":\"john@example.com\"}"
```

**Response:**
```json
{"id": 1, "username": "john_doe", "email": "john@example.com"}
```

#### Upload Bank Statement

```bash
curl -X POST "http://0.0.0.0:8000/api/upload-statement/?user_id=1" \
  -F "file=@data/sample_pdfs/hdfc-demo.pdf"
```

**Response:**
```json
{
  "message": "File uploaded successfully. Processing started.",
  "statement_id": 1,
  "status": "pending"
}
```

#### Check Processing Status

```thunder client
GET "http://0.0.0.0:8000/api/statements/1"
```

**Response:**
```json
{
  "id": 1,
  "filename": "hdfc-demo.pdf",
  "bank_name": "HDFC Bank",
  "account_number": "00392820000014",
  "status": "completed",
  "transaction_count": 139,
  "uploaded_at": "2025-04-10T14:30:00"
}
```

#### Query Transactions

```bash
# All transactions for user
curl -X POST "http://0.0.0.0:8000/api/transactions/query" \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1}'

# Filter by date range
curl -X POST "http://0.0.0.0:8000/api/transactions/query" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "start_date": "2025-03-01",
    "end_date": "2025-03-31"
  }'



#### Get Spending Analytics

```bash
curl "http://0.0.0.0:8000/api/analytics/spending-by-category/1"
```

**Response:**
```json
{
  "user_id": 1,
  "spending_by_category": {
    "fuel": 12850000.00,
    "food_dining": 125432.00,
    "utilities": 23456.00
  },
  "total_spending": 12998888.00
}
```

## Database Schema

### Users Table
- `id`: Primary key
- `username`: Unique username
- `email`: Unique email
- `created_at`: Timestamp

### Bank Statements Table
- `id`: Primary key
- `user_id`: Foreign key to users
- `filename`: Original PDF filename
- `file_path`: Server file path
- `bank_name`: Detected bank name
- `account_number`: Account number
- `statement_period_start/end`: Statement date range
- `opening_balance/closing_balance`: Account balances
- `status`: pending/processing/completed/failed
- `uploaded_at`, `processed_at`: Timestamps

### Transactions Table
- `id`: Primary key
- `statement_id`: Foreign key to bank_statements
- `transaction_date`: Transaction date
- `description`: Full transaction description
- `reference_number`: Check/reference number
- `debit_amount`: Debit amount (if applicable)
- `credit_amount`: Credit amount (if applicable)
- `balance`: Balance after transaction
- `transaction_type`: debit or credit
- `category`: ML-classified category
- `merchant`: Extracted merchant name
- `confidence_score`: ML confidence (0-1)

## Transaction Categories

The system automatically categorizes transactions into:

- `food_dining`: Restaurants, food delivery (Swiggy, Zomato)
- `groceries`: Supermarkets
- `transport`: Uber, Ola, public transport
- `utilities`: Electricity, water, gas, phone bills
- `entertainment`: Movies, streaming services
- `healthcare`: Hospitals, medical expenses
- `shopping`: Retail purchases
- `salary`: Income, payroll
- `transfer`: NEFT, RTGS, IMPS, UPI transfers
- `fees_charges`: Bank fees, taxes, GST
- `investment`: Mutual funds, stocks
- `insurance`: Policy payments
- `fuel`: Petrol, diesel (Bharat Petroleum, etc.)
- `bills`: Phone recharge, DTH, broadband
- `education`: School, college fees
- `other`: Uncategorized transactions

### Adding New Banks:

To add support for a new bank, update `enhanced_extractor.py`:

1. Add bank pattern to `self.bank_patterns`
2. Create `extract_bank_info_<bankname>()` method
3. Create `extract_transactions_<bankname>()` method
4. Update `process_pdf()` method

## ML/NLP Features

### Named Entity Recognition (NER)
- Model: spaCy `en_core_web_sm`
- Purpose: Extract merchant/organization names
- Entities: ORG, PERSON, GPE

### Pattern Matching
- Regex patterns for transaction line identification
- Multiple date format parsing
- Amount extraction with currency handling

## Testing

### Unit Tests

```bash
# Run all tests
pytest tests/ -v

# Test specific module
pytest tests/test_extraction.py -v
```

### Manual Testing with Thunder Clinet

Update base URL to `http://0.0.0.0:8000`
Run collection tests

## Troubleshooting

### Common Issues

**Transformer Model Loading Slow**
First time loading takes 5-10 minutes. The model is cached for subsequent runs.

**No Transactions Extracted**
- Verify PDF format matches HDFC/Indian Bank
- Check if PDF is encrypted
- Ensure PDF has selectable text (not scanned image)
- Run debug test: `python debug_test.py`



## API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/users/` | POST | Create new user |
| `/api/upload-statement/` | POST | Upload PDF statement |
| `/api/statements/{id}` | GET | Get statement details |
| `/api/users/{id}/statements` | GET | List user's statements |
| `/api/transactions/query` | POST | Query transactions with filters |
| `/api/analytics/spending-by-category/{user_id}` | GET | Get spending by category |


## Acknowledgments

- spaCy for NLP capabilities
- Hugging Face for transformer models
- FastAPI for the web framework
- SQLAlchemy for database ORM
