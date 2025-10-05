# import pdfplumber
# import re
# from datetime import datetime
# from typing import List, Dict, Tuple
# import spacy
# from transformers import pipeline
# import pandas as pd


# class EnhancedIndianBankExtractor:
#     def __init__(self):
#         # Load spaCy model for NER
#         try:
#             self.nlp = spacy.load("en_core_web_sm")
#         except:
#             print("Downloading spaCy model...")
#             import os
#             os.system("python -m spacy download en_core_web_sm")
#             self.nlp = spacy.load("en_core_web_sm")
        
#         # Initialize zero-shot classifier
#         self.classifier = pipeline("zero-shot-classification", 
#                                   model="facebook/bart-large-mnli")
        
#         # Categories for Indian transactions
#         self.categories = [
#             "food_dining", "groceries", "transport", "utilities",
#             "entertainment", "healthcare", "shopping", "salary",
#             "transfer", "fees_charges", "investment", "insurance",
#             "fuel", "bills", "education", "other"
#         ]
        
#         # Indian bank patterns
#         self.bank_patterns = {
#             'HDFC': r'HDFC\s*BANK',
#             'INDIAN_BANK': r'INDIAN\s*BANK',
#             'ICICI': r'ICICI\s*BANK',
#             'SBI': r'STATE\s*BANK\s*OF\s*INDIA',
#             'AXIS': r'AXIS\s*BANK',
#         }
    
#     def extract_text_from_pdf(self, pdf_path: str) -> str:
#         """Extract text from PDF using pdfplumber"""
#         text = ""
#         try:
#             with pdfplumber.open(pdf_path) as pdf:
#                 for page in pdf.pages:
#                     page_text = page.extract_text()
#                     if page_text:
#                         text += page_text + "\n"
#         except Exception as e:
#             print(f"Error extracting PDF: {e}")
#         return text
    
#     def detect_bank(self, text: str) -> str:
#         """Detect which bank issued the statement"""
#         for bank, pattern in self.bank_patterns.items():
#             if re.search(pattern, text, re.IGNORECASE):
#                 return bank
#         return "UNKNOWN"
    
#     def extract_bank_info_hdfc(self, text: str) -> Dict:
#         """Extract bank info from HDFC statements"""
#         bank_info = {
#             "bank_name": "HDFC Bank",
#             "account_number": None,
#             "statement_period": None,
#             "branch": None,
#             "ifsc": None
#         }
        
#         # Account number
#         acc_match = re.search(r"Account\s*No\s*:\s*(\d+)", text, re.IGNORECASE)
#         if acc_match:
#             bank_info["account_number"] = self.mask_account_number(acc_match.group(1))
        
#         # Statement period
#         period_match = re.search(r"From\s*:\s*(\d{2}/\d{2}/\d{4})\s*To\s*:\s*(\d{2}/\d{2}/\d{4})", text, re.IGNORECASE)
#         if period_match:
#             bank_info["statement_period"] = (period_match.group(1), period_match.group(2))
        
#         # IFSC
#         ifsc_match = re.search(r"IFSC[\s:]*([A-Z]{4}\d{7})", text)
#         if ifsc_match:
#             bank_info["ifsc"] = ifsc_match.group(1)
        
#         # Branch
#         branch_match = re.search(r"Account Branch\s*:\s*([A-Z\s]+)", text)
#         if branch_match:
#             bank_info["branch"] = branch_match.group(1).strip()
        
#         return bank_info
    
#     def extract_bank_info_indian_bank(self, text: str) -> Dict:
#         """Extract bank info from Indian Bank statements"""
#         bank_info = {
#             "bank_name": "Indian Bank",
#             "account_number": None,
#             "statement_period": None,
#             "branch": None,
#             "ifsc": None
#         }
        
#         # Account number
#         acc_match = re.search(r"Account\s*No\s*:\s*(\d+)", text, re.IGNORECASE)
#         if acc_match:
#             bank_info["account_number"] = self.mask_account_number(acc_match.group(1))
        
#         # Statement period
#         period_match = re.search(r"Statement From\s*:\s*(\d{2}-[A-Za-z]{3}-\d{4}).*?To\s*:\s*(\d{2}-[A-Za-z]{3}-\d{4})", text, re.IGNORECASE | re.DOTALL)
#         if period_match:
#             bank_info["statement_period"] = (period_match.group(1), period_match.group(2))
        
#         # IFSC
#         ifsc_match = re.search(r"IFSC Code\s*:\s*([A-Z]{4}\d{7})", text)
#         if ifsc_match:
#             bank_info["ifsc"] = ifsc_match.group(1)
        
#         # Branch
#         branch_match = re.search(r"([A-Z\s]+)\s*BRANCH", text, re.IGNORECASE)
#         if branch_match:
#             bank_info["branch"] = branch_match.group(1).strip()
        
#         return bank_info
    
#     def mask_account_number(self, acc: str) -> str:
#         """Mask account number except last 4 digits"""
#         if not acc or len(acc) < 4:
#             return "****"
#         return "*" * (len(acc)-4) + acc[-4:]

#     def parse_date(self, date_str: str) -> str:
#         """Parse and standardize date to YYYY-MM-DD"""
#         date_formats = [
#             "%d/%m/%Y", "%d/%m/%y", "%d-%m-%Y", "%d-%m-%y",
#             "%d %b %Y", "%d %B %Y", "%d-%b-%Y", "%d-%B-%Y",
#             "%Y-%m-%d", "%d.%m.%Y"
#         ]
#         for fmt in date_formats:
#             try:
#                 dt = datetime.strptime(date_str.strip(), fmt)
#                 return dt.strftime("%Y-%m-%d")
#             except:
#                 continue
#         return None

#     def clean_amount(self, amt) -> float:
#         """Convert amount string to float, remove commas and text"""
#         if not amt:
#             return None
#         amt = re.sub(r'[^\d\.-]', '', str(amt))
#         try:
#             return float(amt)
#         except:
#             return None
    
#     def extract_transactions_hdfc(self, text: str) -> List[Dict]:
#         """Extract transactions from HDFC bank statements"""
#         transactions = []
        
#         # HDFC format: Date | Narration | Chq./Ref.No. | Value Dt | Withdrawal Amt. | Deposit Amt. | Closing Balance
#         pattern = r"(\d{2}/\d{2}/\d{2})\s+([A-Za-z0-9\s\-\.,/:\(\)\@\*]+?)\s+(\d+)\s+(\d{2}/\d{2}/\d{2})\s+(?:([\d,]+\.?\d*)?\s+)?([\d,]+\.?\d*)\s+([\d,]+\.?\d*)"
        
#         lines = text.split('\n')
        
#         for line in lines:
#             match = re.search(pattern, line)
#             if match:
#                 try:
#                     date_str = match.group(1)
#                     description = match.group(2).strip()
#                     ref_no = match.group(3)
                    
#                     # Check if it's withdrawal or deposit
#                     withdrawal = match.group(5)
#                     deposit = match.group(6)
#                     balance = match.group(7)
                    
#                     transaction_date = self.parse_date(date_str)
#                     if not transaction_date:
#                         continue
                    
#                     # Determine debit/credit
#                     debit_amount = None
#                     credit_amount = None
                    
#                     if withdrawal and withdrawal.strip():
#                         debit_amount = self.clean_amount(withdrawal)
#                     if deposit and deposit.strip():
#                         credit_amount = self.clean_amount(deposit)
                    
#                     # If no withdrawal, it's a credit
#                     if not debit_amount and credit_amount:
#                         pass  # Credit transaction
#                     elif debit_amount and not credit_amount:
#                         pass  # Debit transaction
                    
#                     # Extract merchant and categorize
#                     merchant = self.extract_merchant(description)
#                     category, confidence = self.categorize_transaction(description)
                    
#                     transaction = {
#                         "transaction_date": transaction_date,
#                         "description": description,
#                         "reference_number": ref_no,
#                         "debit_amount": debit_amount,
#                         "credit_amount": credit_amount,
#                         "balance": self.clean_amount(balance),
#                         "transaction_type": "debit" if debit_amount else "credit",
#                         "category": category,
#                         "merchant": merchant,
#                         "confidence_score": confidence
#                     }
                    
#                     transactions.append(transaction)
#                 except Exception as e:
#                     print(f"Error parsing HDFC line: {line[:50]}... Error: {e}")
#                     continue
        
#         return transactions
    
#     def extract_transactions_indian_bank(self, text: str) -> List[Dict]:
#         """Extract transactions from Indian Bank statements"""
#         transactions = []
        
#         # Indian Bank format: Post Date | Value Date | Details | Chq.No. | Debit | Credit | Balance
#         pattern = r"(\d{2}/\d{2}/\d{2})\s+(\d{2}/\d{2}/\d{2})\s+([A-Za-z0-9\s\-\.,/:\(\)\@]+?)\s+(\d+)\s+(?:([\d,]+\.?\d*)?\s+)?([\d,]+\.?\d*)\s+([\d,]+\.?\d*[A-Za-z]*)"
        
#         lines = text.split('\n')
        
#         for line in lines:
#             match = re.search(pattern, line)
#             if match:
#                 try:
#                     date_str = match.group(1)
#                     description = match.group(3).strip()
#                     chq_no = match.group(4)
                    
#                     debit = match.group(5)
#                     credit = match.group(6)
#                     balance = match.group(7)
                    
#                     transaction_date = self.parse_date(date_str)
#                     if not transaction_date:
#                         continue
                    
#                     # Parse amounts
#                     debit_amount = self.clean_amount(debit) if debit and debit.strip() else None
#                     credit_amount = self.clean_amount(credit) if credit and credit.strip() else None
                    
#                     # Remove 'Cr' or 'Dr' from balance
#                     balance_clean = re.sub(r'[A-Za-z]+', '', balance).strip()
#                     balance_float = self.clean_amount(balance_clean) if balance_clean else None
                    
#                     # Extract merchant and categorize
#                     merchant = self.extract_merchant(description)
#                     category, confidence = self.categorize_transaction(description)
                    
#                     transaction = {
#                         "transaction_date": transaction_date,
#                         "description": description,
#                         "reference_number": chq_no,
#                         "debit_amount": debit_amount,
#                         "credit_amount": credit_amount,
#                         "balance": balance_float,
#                         "transaction_type": "debit" if debit_amount else "credit",
#                         "category": category,
#                         "merchant": merchant,
#                         "confidence_score": confidence
#                     }
                    
#                     transactions.append(transaction)
#                 except Exception as e:
#                     print(f"Error parsing Indian Bank line: {line[:50]}... Error: {e}")
#                     continue
        
#         return transactions
    
#     def extract_merchant(self, description: str) -> str:
#         """Extract merchant name using NLP"""
#         doc = self.nlp(description)
        
#         # Look for organization entities
#         for ent in doc.ents:
#             if ent.label_ in ["ORG", "PERSON"]:
#                 return ent.text
        
#         # For UPI transactions, extract payee name
#         upi_match = re.search(r"UPI[/-]([A-Za-z\s]+)[/-]", description, re.IGNORECASE)
#         if upi_match:
#             return upi_match.group(1).strip()
        
#         # For NEFT/RTGS, extract beneficiary
#         neft_match = re.search(r"(?:NEFT|RTGS)[/-]([A-Z\s]+)[/-]", description, re.IGNORECASE)
#         if neft_match:
#             return neft_match.group(1).strip()
        
#         # Fallback: first few words
#         words = description.split()
#         return " ".join(words[:3]) if len(words) > 0 else description
    
#     def categorize_transaction(self, description: str) -> Tuple[str, float]:
#         """Categorize transaction using ML and rules"""
#         desc_lower = description.lower()
        
#         # Rule-based categorization for common patterns
#         if any(word in desc_lower for word in ['upi', 'phonepe', 'paytm', 'gpay']):
#             if any(word in desc_lower for word in ['swiggy', 'zomato', 'restaurant', 'cafe', 'food']):
#                 return 'food_dining', 0.9
#             elif any(word in desc_lower for word in ['uber', 'ola', 'rapido']):
#                 return 'transport', 0.9
        
#         if any(word in desc_lower for word in ['salary', 'payroll', 'income']):
#             return 'salary', 0.95
        
#         if any(word in desc_lower for word in ['electricity', 'water', 'gas', 'bsnl', 'airtel', 'jio']):
#             return 'utilities', 0.9
        
#         if any(word in desc_lower for word in ['petrol', 'diesel', 'fuel', 'petroleum']):
#             return 'fuel', 0.9
        
#         if any(word in desc_lower for word in ['hospital', 'medical', 'pharmacy', 'doctor']):
#             return 'healthcare', 0.9
        
#         # Use ML classifier for complex cases
#         try:
#             result = self.classifier(description, self.categories)
#             return result['labels'][0], result['scores'][0]
#         except:
#             return 'other', 0.5
    
#     def extract_balances(self, text: str) -> Dict:
#         """Extract opening and closing balances"""
#         balances = {
#             "opening_balance": None,
#             "closing_balance": None
#         }
        
#         # Opening balance
#         opening_patterns = [
#             r"Opening\s*Balance[\s:]*(?:Rs\.?)?\s*([\d,]+\.?\d*)",
#             r"Brought\s*Forward[\s:]*(?:Rs\.?)?\s*([\d,]+\.?\d*[A-Za-z]*)",
#         ]
        
#         for pattern in opening_patterns:
#             match = re.search(pattern, text, re.IGNORECASE)
#             if match:
#                 balance_str = re.sub(r'[A-Za-z]+', '', match.group(1)).strip()
#                 balances["opening_balance"] = float(balance_str.replace(',', ''))
#                 break
        
#         # Closing balance
#         closing_patterns = [
#             r"Closing\s*Balance[\s:]*(?:Rs\.?)?\s*([\d,]+\.?\d*)",
#             r"CLOSING\s*BALANCE[\s:]*(?:Rs\.?)?\s*([\d,]+\.?\d*[A-Za-z]*)",
#         ]
        
#         for pattern in closing_patterns:
#             match = re.search(pattern, text, re.IGNORECASE)
#             if match:
#                 balance_str = re.sub(r'[A-Za-z]+', '', match.group(1)).strip()
#                 balances["closing_balance"] = float(balance_str.replace(',', ''))
#                 break
        
#         return balances
    
#     def process_pdf(self, pdf_path: str) -> Dict:
#         """Main method to process PDF and extract all data"""
#         text = self.extract_text_from_pdf(pdf_path)
        
#         if not text:
#             return {"error": "Failed to extract text from PDF"}
        
#         # Detect bank type
#         bank_type = self.detect_bank(text)
        
#         # Extract bank info based on type
#         if bank_type == "HDFC":
#             bank_info = self.extract_bank_info_hdfc(text)
#             transactions = self.extract_transactions_hdfc(text)
#         elif bank_type == "INDIAN_BANK":
#             bank_info = self.extract_bank_info_indian_bank(text)
#             transactions = self.extract_transactions_indian_bank(text)
#         else:
#             # Generic extraction
#             bank_info = {"bank_name": "Unknown"}
#             transactions = []
        
#         balances = self.extract_balances(text)
        
#         return {
#             "bank_type": bank_type,
#             "bank_info": bank_info,
#             "transactions": transactions,
#             "balances": balances,
#             "total_transactions": len(transactions)
#         }

import pdfplumber
import re
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import spacy
from transformers import pipeline
import pandas as pd


class EnhancedIndianBankExtractor:
    def __init__(self):
        # Load spaCy model for NER
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            print("Downloading spaCy model...")
            import os
            os.system("python -m spacy download en_core_web_sm")
            self.nlp = spacy.load("en_core_web_sm")
        
        # Initialize zero-shot classifier with error handling
        try:
            self.classifier = pipeline("zero-shot-classification", 
                                      model="facebook/bart-large-mnli")
            print("✓ ML classifier loaded successfully")
        except Exception as e:
            print(f"⚠ Warning: Could not load ML classifier: {e}")
            print("  Will use rule-based categorization only")
            self.classifier = None
        
        # Categories for Indian transactions
        self.categories = [
            "food_dining", "groceries", "transport", "utilities",
            "entertainment", "healthcare", "shopping", "salary",
            "transfer", "fees_charges", "investment", "insurance",
            "fuel", "bills", "education", "other"
        ]
        
        # Indian bank patterns
        self.bank_patterns = {
            'HDFC': r'HDFC\s*BANK',
            'INDIAN_BANK': r'INDIAN\s*BANK',
            'ICICI': r'ICICI\s*BANK',
            'SBI': r'STATE\s*BANK\s*OF\s*INDIA|SBI',
            'AXIS': r'AXIS\s*BANK',
            'KOTAK': r'KOTAK\s*MAHINDRA',
            'YES': r'YES\s*BANK',
            'BOI': r'BANK\s*OF\s*INDIA',
            'PNB': r'PUNJAB\s*NATIONAL\s*BANK',
        }
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using pdfplumber"""
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"Error extracting PDF: {e}")
        return text
    
    def detect_bank(self, text: str) -> str:
        """Detect which bank issued the statement"""
        for bank, pattern in self.bank_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                return bank
        return "UNKNOWN"
    
    def extract_bank_info_hdfc(self, text: str) -> Dict:
        """Extract bank info from HDFC statements"""
        bank_info = {
            "bank_name": "HDFC Bank",
            "account_number": None,
            "statement_period": None,
            "branch": None,
            "ifsc": None,
            "customer_name": None,
            "opening_balance": None,
            "closing_balance": None
        }
        
        # Account number
        acc_match = re.search(r"Account\s*No\s*:\s*(\d+)", text, re.IGNORECASE)
        if acc_match:
            bank_info["account_number"] = acc_match.group(1)
        
        # Customer name
        name_match = re.search(r"M/S\.\s*([A-Z\s&]+)\n", text)
        if name_match:
            bank_info["customer_name"] = name_match.group(1).strip()
        
        # Statement period
        period_match = re.search(r"From\s*:\s*(\d{2}/\d{2}/\d{4})\s*To\s*:\s*(\d{2}/\d{2}/\d{4})", text, re.IGNORECASE)
        if period_match:
            bank_info["statement_period"] = (period_match.group(1), period_match.group(2))
        
        # IFSC
        ifsc_match = re.search(r"(?:IFSC|RTGS/NEFT\s+IFSC)[\s:]*([A-Z]{4}\d{7})", text)
        if ifsc_match:
            bank_info["ifsc"] = ifsc_match.group(1)
        
        # Branch
        branch_match = re.search(r"Account Branch\s*:\s*([A-Z\s]+)", text)
        if branch_match:
            bank_info["branch"] = branch_match.group(1).strip()
        
        # Balances
        opening_match = re.search(r"Opening\s*Balance[:\s]+([\d,]+\.?\d*)", text, re.IGNORECASE)
        if opening_match:
            bank_info["opening_balance"] = float(opening_match.group(1).replace(',', ''))
        
        closing_match = re.search(r"Closing\s*Bal[ance]*[:\s]+([\d,]+\.?\d*)", text, re.IGNORECASE)
        if closing_match:
            bank_info["closing_balance"] = float(closing_match.group(1).replace(',', ''))
        
        return bank_info
    
    def extract_bank_info_indian_bank(self, text: str) -> Dict:
        """Extract bank info from Indian Bank statements"""
        bank_info = {
            "bank_name": "Indian Bank",
            "account_number": None,
            "statement_period": None,
            "branch": None,
            "ifsc": None,
            "customer_name": None,
            "opening_balance": None,
            "closing_balance": None
        }
        
        # Account number
        acc_match = re.search(r"Account\s*No\s*:\s*(\d+)", text, re.IGNORECASE)
        if acc_match:
            bank_info["account_number"] = acc_match.group(1)
        
        # Customer name
        name_match = re.search(r"([A-Z\s]+(?:HOSPITAL|TRUST|COMPANY))", text)
        if name_match:
            bank_info["customer_name"] = name_match.group(1).strip()
        
        # Statement period
        period_match = re.search(r"Statement From\s*:\s*(\d{2}-[A-Za-z]{3}-\d{4}).*?To\s*:\s*(\d{2}-[A-Za-z]{3}-\d{4})", text, re.IGNORECASE | re.DOTALL)
        if period_match:
            bank_info["statement_period"] = (period_match.group(1), period_match.group(2))
        
        # IFSC
        ifsc_match = re.search(r"IFSC Code\s*:\s*([A-Z]{4}\d{7})", text)
        if ifsc_match:
            bank_info["ifsc"] = ifsc_match.group(1)
        
        # Branch
        branch_match = re.search(r"([A-Z\s]+)\s*BRANCH", text, re.IGNORECASE)
        if branch_match:
            bank_info["branch"] = branch_match.group(1).strip()
        
        # Opening balance
        opening_match = re.search(r"Brought\s*Forward\s*([\d,]+\.?\d*)[Cc][Rr]", text)
        if opening_match:
            bank_info["opening_balance"] = float(opening_match.group(1).replace(',', ''))
        
        # Closing balance
        closing_match = re.search(r"CLOSING\s*BALANCE\s*:\s*([\d,]+\.?\d*)[Cc][Rr]", text)
        if closing_match:
            bank_info["closing_balance"] = float(closing_match.group(1).replace(',', ''))
        
        return bank_info
    
    def extract_bank_info_generic(self, text: str) -> Dict:
        """Extract bank info from generic format"""
        bank_info = {
            "bank_name": "Unknown",
            "account_number": None,
            "statement_period": None,
            "branch": None,
            "ifsc": None,
            "customer_name": None,
            "opening_balance": None,
            "closing_balance": None
        }
        
        # Account number
        acc_match = re.search(r"Account\s*(?:Number|No)[\s:]*(\d{10,18})", text, re.IGNORECASE)
        if acc_match:
            bank_info["account_number"] = acc_match.group(1)
        
        # Statement period
        period_match = re.search(r"Transaction date\s*:\s*From\s*(\d{2}/\d{2}/\d{4})\s*To\s*(\d{2}/\d{2}/\d{4})", text, re.IGNORECASE)
        if period_match:
            bank_info["statement_period"] = (period_match.group(1), period_match.group(2))
        
        return bank_info

    def parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse various date formats and return datetime object"""
        if not date_str:
            return None
            
        date_formats = [
            "%d/%m/%Y", "%d/%m/%y", "%d-%m-%Y", "%d-%m-%y",
            "%d %b %Y", "%d %B %Y", "%d-%b-%Y", "%d-%B-%Y",
            "%Y-%m-%d", "%d.%m.%Y"
        ]
        
        date_str = date_str.strip()
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str, fmt)
            except:
                continue
        return None

    def parse_amount(self, amount_str: str) -> Optional[float]:
        """Parse amount string to float"""
        if not amount_str or amount_str.strip() == '':
            return None
        try:
            amount_str = amount_str.replace(',', '').replace(' ', '').strip()
            return float(amount_str)
        except:
            return None
    
    def extract_transactions_hdfc(self, text: str) -> List[Dict]:
        """Extract transactions from HDFC statements - improved pattern"""
        transactions = []
        lines = text.split('\n')
        
        # Multiple patterns for HDFC
        patterns = [
            # Pattern 1: With both withdrawal and deposit columns
            r'(\d{2}/\d{2}/\d{2})\s+(.+?)\s+(\d+)\s+(\d{2}/\d{2}/\d{2})\s+([\d,]+\.?\d*)\s+([\d,]+\.?\d*)\s+([\d,]+\.?\d*)',
            # Pattern 2: Single amount column
            r'(\d{2}/\d{2}/\d{2})\s+(.+?)\s+(\d+)\s+(\d{2}/\d{2}/\d{2})\s+([\d,]+\.?\d*)\s+([\d,]+\.?\d*)',
        ]
        
        for line in lines:
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    try:
                        groups = match.groups()
                        date_str = groups[0]
                        description = groups[1].strip()
                        ref_no = groups[2]
                        
                        transaction_date = self.parse_date(date_str)
                        if not transaction_date:
                            continue
                        
                        # Determine if debit or credit from description
                        is_debit = any(kw in description.upper() for kw in 
                                      ['DR-', 'RTGS DR', 'NEFT DR', 'ACH D-', 'WITHDRAWAL'])
                        
                        # Parse amounts
                        if len(groups) == 7:  # Two amount columns
                            withdrawal = self.parse_amount(groups[4])
                            deposit = self.parse_amount(groups[5])
                            balance = self.parse_amount(groups[6])
                            
                            debit_amount = withdrawal if withdrawal and withdrawal > 0 else None
                            credit_amount = deposit if deposit and deposit > 0 else None
                        else:  # Single amount column
                            amount = self.parse_amount(groups[4])
                            balance = self.parse_amount(groups[5])
                            
                            if is_debit:
                                debit_amount = amount
                                credit_amount = None
                            else:
                                debit_amount = None
                                credit_amount = amount
                        
                        merchant = self.extract_merchant(description)
                        category, confidence = self.categorize_transaction(description)
                        
                        transaction = {
                            "transaction_date": transaction_date,
                            "description": description,
                            "reference_number": ref_no,
                            "debit_amount": debit_amount,
                            "credit_amount": credit_amount,
                            "balance": balance,
                            "transaction_type": "debit" if debit_amount else "credit",
                            "category": category,
                            "merchant": merchant,
                            "confidence_score": confidence
                        }
                        
                        transactions.append(transaction)
                        break
                    except Exception as e:
                        continue
        
        return transactions
    
    def extract_transactions_indian_bank(self, text: str) -> List[Dict]:
        """Extract transactions from Indian Bank statements"""
        transactions = []
        lines = text.split('\n')
        
        pattern = r'(\d{2}/\d{2}/\d{2})\s+(\d{2}/\d{2}/\d{2})\s+(.+?)\s+(\d+)\s+([\d,]+\.?\d*)?\s+([\d,]+\.?\d*)?\s+([\d,]+\.?\d*[A-Za-z]*)'
        
        for line in lines:
            match = re.search(pattern, line)
            if match:
                try:
                    date_str = match.group(1)
                    description = match.group(3).strip()
                    chq_no = match.group(4)
                    debit_str = match.group(5)
                    credit_str = match.group(6)
                    balance_str = match.group(7)
                    
                    transaction_date = self.parse_date(date_str)
                    if not transaction_date:
                        continue
                    
                    debit_amount = self.parse_amount(debit_str) if debit_str else None
                    credit_amount = self.parse_amount(credit_str) if credit_str else None
                    
                    balance_clean = re.sub(r'[A-Za-z]+', '', balance_str).strip()
                    balance_float = self.parse_amount(balance_clean)
                    
                    merchant = self.extract_merchant(description)
                    category, confidence = self.categorize_transaction(description)
                    
                    transaction = {
                        "transaction_date": transaction_date,
                        "description": description,
                        "reference_number": chq_no,
                        "debit_amount": debit_amount,
                        "credit_amount": credit_amount,
                        "balance": balance_float,
                        "transaction_type": "debit" if debit_amount else "credit",
                        "category": category,
                        "merchant": merchant,
                        "confidence_score": confidence
                    }
                    
                    transactions.append(transaction)
                except Exception as e:
                    continue
        
        return transactions
    
    def extract_transactions_generic(self, text: str) -> List[Dict]:
        """Extract from generic format (3rd PDF)"""
        transactions = []
        lines = text.split('\n')
        
        pattern = r'(\d{2}-\d{2}-\d{4})\s+(.+?)\s+([\d,]+\.?\d*)\s+(CR|DR)'
        
        for line in lines:
            match = re.search(pattern, line)
            if match:
                try:
                    date_str = match.group(1)
                    description = match.group(2).strip()
                    amount_str = match.group(3)
                    txn_type = match.group(4)
                    
                    transaction_date = self.parse_date(date_str)
                    if not transaction_date:
                        continue
                    
                    amount = self.parse_amount(amount_str)
                    
                    if txn_type == 'DR':
                        debit_amount = amount
                        credit_amount = None
                    else:
                        debit_amount = None
                        credit_amount = amount
                    
                    merchant = self.extract_merchant(description)
                    category, confidence = self.categorize_transaction(description)
                    
                    transaction = {
                        "transaction_date": transaction_date,
                        "description": description,
                        "reference_number": None,
                        "debit_amount": debit_amount,
                        "credit_amount": credit_amount,
                        "balance": None,
                        "transaction_type": "debit" if debit_amount else "credit",
                        "category": category,
                        "merchant": merchant,
                        "confidence_score": confidence
                    }
                    
                    transactions.append(transaction)
                except Exception as e:
                    continue
        
        return transactions
    
    def extract_merchant(self, description: str) -> str:
        """Extract merchant name"""
        # UPI
        upi_match = re.search(r"UPI[/-]([A-Z][A-Za-z\s]+)[/-@]", description, re.IGNORECASE)
        if upi_match:
            return upi_match.group(1).strip()
        
        # NEFT/RTGS/IMPS
        neft_match = re.search(r"(?:NEFT|RTGS|IMPS)[^\-]*?-([A-Z][A-Za-z\s&]+?)(?:-|/|$)", description, re.IGNORECASE)
        if neft_match:
            return neft_match.group(1).strip()
        
        # CHQ
        chq_match = re.search(r"CHQ DEP[^:]*:([A-Z][A-Za-z\s]+?):", description, re.IGNORECASE)
        if chq_match:
            return chq_match.group(1).strip()
        
        # NER fallback
        doc = self.nlp(description)
        for ent in doc.ents:
            if ent.label_ in ["ORG", "PERSON"]:
                return ent.text
        
        words = [w for w in description.split() if len(w) > 2]
        return " ".join(words[:3]) if words else description[:30]
    
    def categorize_transaction(self, description: str) -> Tuple[str, float]:
        """Categorize transaction"""
        desc_lower = description.lower()
        
        # Rule-based (high confidence)
        rules = {
            'food_dining': ['restaurant', 'cafe', 'food', 'zomato', 'swiggy', 'caterer', 'burger'],
            'fuel': ['petrol', 'diesel', 'fuel', 'petroleum', 'bharat petroleum'],
            'utilities': ['electricity', 'water', 'gas', 'bsnl', 'airtel', 'jio', 'vodafone', 'msedcl'],
            'transport': ['uber', 'ola', 'rapido', 'metro', 'taxi', 'tpt'],
            'salary': ['salary', 'payroll', 'income'],
            'transfer': ['sweep trf', 'neft', 'rtgs', 'imps', 'transfer'],
            'fees_charges': ['charges', 'fee', 'sms_chg', 'gst', 'tax', 'cbdt'],
            'healthcare': ['hospital', 'medical', 'pharmacy', 'doctor'],
            'education': ['school', 'college', 'polytechnic', 'education'],
            'investment': ['redeem', 'invest', 'mutual fund'],
        }
        
        for category, keywords in rules.items():
            if any(kw in desc_lower for kw in keywords):
                return category, 0.9
        
        # ML classifier
        if self.classifier:
            try:
                result = self.classifier(description, self.categories, multi_label=False)
                return result['labels'][0], result['scores'][0]
            except:
                pass
        
        return 'other', 0.5
    
    def extract_balances(self, text: str) -> Dict:
        """Extract balances"""
        balances = {"opening_balance": None, "closing_balance": None}
        
        # Opening
        for pattern in [r"Opening\s*Balance[\s:]*(?:Rs\.?)?\s*([\d,]+\.?\d*)",
                       r"Brought\s*Forward[\s:]*(?:Rs\.?)?\s*([\d,]+\.?\d*[A-Za-z]*)"]:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                balance_str = re.sub(r'[A-Za-z]+', '', match.group(1)).strip()
                balances["opening_balance"] = self.parse_amount(balance_str)
                if balances["opening_balance"]:
                    break
        
        # Closing
        for pattern in [r"Closing\s*Balance[\s:]*(?:Rs\.?)?\s*([\d,]+\.?\d*)",
                       r"CLOSING\s*BALANCE[\s:]*(?:Rs\.?)?\s*([\d,]+\.?\d*[A-Za-z]*)"]:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                balance_str = re.sub(r'[A-Za-z]+', '', match.group(1)).strip()
                balances["closing_balance"] = self.parse_amount(balance_str)
                if balances["closing_balance"]:
                    break
        
        return balances
    
    def process_pdf(self, pdf_path: str) -> Dict:
        """Main processing method"""
        print(f"Processing: {pdf_path}")
        text = self.extract_text_from_pdf(pdf_path)
        
        if not text:
            return {"error": "Failed to extract text from PDF"}
        
        bank_type = self.detect_bank(text)
        print(f"Detected bank: {bank_type}")
        
        # Extract based on bank type
        if bank_type == "HDFC":
            bank_info = self.extract_bank_info_hdfc(text)
            transactions = self.extract_transactions_hdfc(text)
        elif bank_type == "INDIAN_BANK":
            bank_info = self.extract_bank_info_indian_bank(text)
            transactions = self.extract_transactions_indian_bank(text)
        else:
            bank_info = self.extract_bank_info_generic(text)
            transactions = self.extract_transactions_generic(text)
            if not transactions:
                transactions = self.extract_transactions_hdfc(text)
        
        balances = self.extract_balances(text)
        
        # Merge balances
        if not bank_info.get("opening_balance"):
            bank_info["opening_balance"] = balances.get("opening_balance")
        if not bank_info.get("closing_balance"):
            bank_info["closing_balance"] = balances.get("closing_balance")
        
        print(f"✓ Extracted {len(transactions)} transactions")
        
        return {
            "bank_type": bank_type,
            "bank_info": bank_info,
            "transactions": transactions,
            "balances": balances,
            "total_transactions": len(transactions)
        }