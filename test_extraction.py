# """
# Test script for PDF extraction
# Usage: python test_extraction.py --pdf path/to/statement.pdf
# """

# import argparse
# import json
# from enhanced_extractor import EnhancedIndianBankExtractor
# from datetime import datetime

# def test_extraction(pdf_path: str):
#     """Test PDF extraction on a sample file"""
#     print(f"\n{'='*60}")
#     print(f"Testing PDF Extraction: {pdf_path}")
#     print(f"{'='*60}\n")
    
#     # Initialize extractor
#     extractor = EnhancedIndianBankExtractor()
    
#     # Process PDF
#     print("Processing PDF...")
#     result = extractor.process_pdf(pdf_path)
    
#     if "error" in result:
#         print(f"❌ Error: {result['error']}")
#         return
    
#     # Display results
#     print(f"\n✓ Bank Type: {result['bank_type']}")
#     bank_info = result['bank_info']
#     print(f"✓ Bank Name: {bank_info.get('bank_name', 'N/A')}")
#     print(f"✓ Account Number: {bank_info.get('account_number', 'N/A')}")
#     print(f"✓ IFSC Code: {bank_info.get('ifsc', 'N/A')}")
#     print(f"✓ Branch: {bank_info.get('branch', 'N/A')}")
    
#     if bank_info.get('statement_period'):
#         period = bank_info['statement_period']
#         print(f"✓ Statement Period: {period[0]} to {period[1]}")
    
#     print(f"\n✓ Opening Balance: ₹{result['balances'].get('opening_balance') or 0:,.2f}")
#     print(f"✓ Closing Balance: ₹{result['balances'].get('closing_balance') or 0:,.2f}")
#     print(f"\n✓ Total Transactions Extracted: {result['total_transactions']}")
    
#     # Transaction statistics
#     transactions = result['transactions']
#     if transactions:
#         total_debits = sum(t['debit_amount'] for t in transactions if t.get('debit_amount'))
#         total_credits = sum(t['credit_amount'] for t in transactions if t.get('credit_amount'))
        
#         print(f"\n💰 Transaction Summary:")
#         print(f"   Total Debits:  ₹{total_debits:,.2f}")
#         print(f"   Total Credits: ₹{total_credits:,.2f}")
#         print(f"   Net Flow:      ₹{(total_credits - total_debits):,.2f}")
        
#         # Category breakdown
#         categories = {}
#         for t in transactions:
#             cat = t.get('category', 'other')
#             if cat not in categories:
#                 categories[cat] = {'count': 0, 'amount': 0}
#             categories[cat]['count'] += 1
#             if t.get('debit_amount'):
#                 categories[cat]['amount'] += t['debit_amount']
        
#         print(f"\n📊 Category Breakdown:")
#         for cat, data in sorted(categories.items(), key=lambda x: x[1]['amount'], reverse=True):
#             print(f"   {cat:20s}: {data['count']:3d} transactions, ₹{data['amount']:10,.2f}")
        
#         # Sample transactions
#         print(f"\n📝 Sample Transactions (first 5):")
#         for i, txn in enumerate(transactions[:5], 1):
#             date = txn['transaction_date'].strftime('%d-%b-%Y') if isinstance(txn['transaction_date'], datetime) else str(txn['transaction_date'])
#             desc = txn.get('description', '')[:50]
#             debit = txn.get('debit_amount')
#             credit = txn.get('credit_amount')
#             txn_type = "Debit" if debit else ("Credit" if credit else "N/A")
#             amount = debit if debit else (credit if credit else 0)
#             print(f"   {i}. {date} | {desc:50s} | {txn_type:6s} ₹{amount:,.2f}")
    
#     # Save to JSON
#     output_file = f"extracted_transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
#     # Convert datetime objects to strings for JSON serialization
#     json_result = result.copy()
#     for txn in json_result['transactions']:
#         if isinstance(txn['transaction_date'], datetime):
#             txn['transaction_date'] = txn['transaction_date'].isoformat()
    
#     with open(output_file, 'w', encoding='utf-8') as f:
#         json.dump(json_result, f, indent=2, ensure_ascii=False)
    
#     print(f"\n✓ Extracted data saved to: {output_file}")
#     print(f"\n{'='*60}\n")

# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description='Test PDF extraction')
#     parser.add_argument('--pdf', required=True, help='Path to PDF bank statement')
    
#     args = parser.parse_args()
#     test_extraction(args.pdf)

"""
Test script for PDF extraction
Usage: python test_extraction.py --pdf path/to/statement.pdf
"""

import argparse
import json
from enhanced_extractor import EnhancedIndianBankExtractor
from datetime import datetime
import sys

def test_extraction(pdf_path: str):
    """Test PDF extraction on a sample file"""
    print(f"\n{'='*60}")
    print(f"Testing PDF Extraction: {pdf_path}")
    print(f"{'='*60}\n")
    
    try:
        # Initialize extractor
        print("Initializing extractor...")
        extractor = EnhancedIndianBankExtractor()
        print("✓ Extractor initialized\n")
        
        # Process PDF
        print("Processing PDF...")
        result = extractor.process_pdf(pdf_path)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return
        
        # Display results
        print(f"\n✓ Bank Type: {result['bank_type']}")
        bank_info = result.get('bank_info', {})
        print(f"✓ Bank Name: {bank_info.get('bank_name', 'N/A')}")
        print(f"✓ Account Number: {bank_info.get('account_number', 'N/A')}")
        print(f"✓ IFSC Code: {bank_info.get('ifsc', 'N/A')}")
        print(f"✓ Branch: {bank_info.get('branch', 'N/A')}")
        
        if bank_info.get('statement_period'):
            period = bank_info['statement_period']
            print(f"✓ Statement Period: {period[0]} to {period[1]}")
        
        balances = result.get('balances', {})
        opening = balances.get('opening_balance') or bank_info.get('opening_balance') or 0
        closing = balances.get('closing_balance') or bank_info.get('closing_balance') or 0
        
        print(f"\n✓ Opening Balance: ₹{opening:,.2f}")
        print(f"✓ Closing Balance: ₹{closing:,.2f}")
        print(f"\n✓ Total Transactions Extracted: {result['total_transactions']}")
        
        # Transaction statistics
        transactions = result.get('transactions', [])
        if transactions:
            total_debits = sum(t.get('debit_amount', 0) or 0 for t in transactions)
            total_credits = sum(t.get('credit_amount', 0) or 0 for t in transactions)
            
            print(f"\n💰 Transaction Summary:")
            print(f"   Total Debits:  ₹{total_debits:,.2f}")
            print(f"   Total Credits: ₹{total_credits:,.2f}")
            print(f"   Net Flow:      ₹{(total_credits - total_debits):,.2f}")
            
            # Category breakdown
            categories = {}
            for t in transactions:
                cat = t.get('category', 'other')
                if cat not in categories:
                    categories[cat] = {'count': 0, 'debit': 0, 'credit': 0}
                categories[cat]['count'] += 1
                if t.get('debit_amount'):
                    categories[cat]['debit'] += t['debit_amount']
                if t.get('credit_amount'):
                    categories[cat]['credit'] += t['credit_amount']
            
            print(f"\n📊 Category Breakdown:")
            for cat, data in sorted(categories.items(), key=lambda x: x[1]['debit'], reverse=True):
                print(f"   {cat:20s}: {data['count']:3d} txns | "
                      f"Dr: ₹{data['debit']:10,.2f} | Cr: ₹{data['credit']:10,.2f}")
            
            # Sample transactions
            print(f"\n📝 Sample Transactions (first 10):")
            for i, txn in enumerate(transactions[:10], 1):
                date = txn['transaction_date'].strftime('%d-%b-%Y') if isinstance(txn['transaction_date'], datetime) else str(txn['transaction_date'])
                desc = txn.get('description', '')[:50]
                debit = txn.get('debit_amount')
                credit = txn.get('credit_amount')
                
                if debit:
                    print(f"   {i:2d}. {date} | {desc:50s} | Debit  ₹{debit:10,.2f}")
                elif credit:
                    print(f"   {i:2d}. {date} | {desc:50s} | Credit ₹{credit:10,.2f}")
        
        # Save to JSON
        output_file = f"extracted_transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert datetime objects to strings for JSON serialization
        json_result = result.copy()
        for txn in json_result.get('transactions', []):
            if isinstance(txn.get('transaction_date'), datetime):
                txn['transaction_date'] = txn['transaction_date'].isoformat()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_result, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Extracted data saved to: {output_file}")
        print(f"\n{'='*60}\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Test PDF extraction')
    parser.add_argument('--pdf', required=True, help='Path to PDF bank statement')
    
    args = parser.parse_args()
    test_extraction(args.pdf)