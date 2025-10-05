from enhanced_extractor import EnhancedIndianBankExtractor
import sys

pdf_path = "data/sample_pdfs/hdfc-demo.pdf"

print("=" * 60)
print("DEBUG TEST")
print("=" * 60)

try:
    print(f"\n1. Initializing extractor...")
    extractor = EnhancedIndianBankExtractor()
    print("   ✓ Extractor initialized")
    
    print(f"\n2. Reading PDF: {pdf_path}")
    text = extractor.extract_text_from_pdf(pdf_path)
    print(f"   ✓ Extracted {len(text)} characters")
    print(f"   First 200 chars: {text[:200]}")
    
    print(f"\n3. Detecting bank...")
    bank_type = extractor.detect_bank(text)
    print(f"   ✓ Bank type: {bank_type}")
    
    print(f"\n4. Extracting transactions...")
    if bank_type == "HDFC":
        transactions = extractor.extract_transactions_hdfc(text)
    else:
        transactions = []
    
    print(f"   ✓ Found {len(transactions)} transactions")
    
    if transactions:
        print(f"\n5. First transaction:")
        print(f"   {transactions[0]}")
    else:
        print(f"\n5. NO TRANSACTIONS FOUND!")
        print(f"\nShowing first 10 lines of PDF:")
        for i, line in enumerate(text.split('\n')[:10], 1):
            print(f"   {i}: {line}")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()