"""
Data Parser for BOC (Bill-on-Chain) PostgreSQL Dump
Extracts bill_extraction data into a clean pandas DataFrame.
"""

import re
import json
import pandas as pd
import os


def parse_boc_dump(filepath: str) -> pd.DataFrame:
    """Parse the PostgreSQL dump file and extract bill_extraction records."""
    
    records = []
    in_bill_extraction = False
    
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.rstrip('\n').rstrip('\r')
            
            # Detect start of bill_extraction COPY block
            if 'bill_extraction' in line and 'COPY' in line and 'FROM stdin' in line:
                in_bill_extraction = True
                continue
            
            # End of COPY block
            if in_bill_extraction and line.strip() == '\\.':
                in_bill_extraction = False
                continue
            
            if in_bill_extraction and line.strip():
                try:
                    parts = line.split('\t')
                    if len(parts) >= 15:
                        raw_json_str = parts[13] if len(parts) > 13 else '{}'
                        
                        # Parse line items from the array-like string
                        line_items_str = parts[12] if len(parts) > 12 else '[]'
                        try:
                            if line_items_str.startswith('['):
                                line_items = json.loads(line_items_str.replace("'", '"'))
                            else:
                                line_items = []
                        except:
                            line_items = []
                        
                        # Parse raw JSON response for additional details
                        raw_data = {}
                        try:
                            if raw_json_str and raw_json_str != '\\N':
                                raw_data = json.loads(raw_json_str)
                        except:
                            raw_data = {}
                        
                        total_amount = None
                        try:
                            val = parts[6]
                            if val and val != '\\N':
                                total_amount = float(val)
                        except:
                            pass
                        
                        tax_amount = None
                        try:
                            val = parts[7]
                            if val and val != '\\N':
                                tax_amount = float(val)
                        except:
                            pass
                        
                        invoice_date = None
                        try:
                            date_str = parts[4]
                            if date_str and date_str != '\\N':
                                invoice_date = pd.to_datetime(date_str)
                        except:
                            pass
                        
                        record = {
                            'extraction_id': parts[0],
                            'bill_id': parts[1],
                            'merchant_name': parts[2] if parts[2] != '\\N' else None,
                            'invoice_number': parts[3] if parts[3] != '\\N' else None,
                            'invoice_date': invoice_date,
                            'currency': parts[5] if parts[5] != '\\N' else None,
                            'total_amount': total_amount,
                            'tax_amount': tax_amount,
                            'category': parts[8] if parts[8] != '\\N' else 'other',
                            'tax_reg_number': parts[9] if len(parts) > 9 and parts[9] != '\\N' else None,
                            'line_items': line_items,
                            'line_items_count': len(line_items) if line_items else 0,
                            'model_used': parts[14] if len(parts) > 14 and parts[14] != '\\N' else None,
                            'created_at': pd.to_datetime(parts[-1]) if parts[-1] and parts[-1] != '\\N' else None,
                        }
                        
                        records.append(record)
                except Exception as e:
                    continue
    
    df = pd.DataFrame(records)
    
    if not df.empty:
        # Data cleaning
        df['category'] = df['category'].fillna('other').str.lower().str.strip()
        df['merchant_name'] = df['merchant_name'].fillna('Unknown Vendor')
        df['currency'] = df['currency'].fillna('USD')
        
        # Extract month/year for time series
        if 'invoice_date' in df.columns:
            df['invoice_month'] = df['invoice_date'].dt.to_period('M').astype(str)
            df['invoice_year'] = df['invoice_date'].dt.year
            df['invoice_month_name'] = df['invoice_date'].dt.strftime('%b %Y')
            df['invoice_day'] = df['invoice_date'].dt.day
            df['invoice_weekday'] = df['invoice_date'].dt.day_name()
        
        # Standardize category names
        category_map = {
            'food': 'Food & Groceries',
            'transport': 'Transportation',
            'utilities': 'Utilities',
            'healthcare': 'Healthcare',
            'entertainment': 'Entertainment',
            'shopping': 'Shopping',
            'travel': 'Travel',
            'education': 'Education',
            'subscriptions': 'Subscriptions',
            'tech': 'Technology',
            'other': 'Other',
            'miscellaneous': 'Miscellaneous'
        }
        df['category_display'] = df['category'].map(category_map).fillna('Other')
        
        # Create vendor shortname
        df['vendor_short'] = df['merchant_name'].apply(
            lambda x: x[:30] + '...' if isinstance(x, str) and len(x) > 30 else x
        )
    
    return df


def parse_bill_table(filepath: str) -> pd.DataFrame:
    """Parse the bill table for status and metadata."""
    records = []
    in_bill = False
    
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.rstrip('\n').rstrip('\r')
            
            if 'COPY public.bill ' in line and 'FROM stdin' in line:
                in_bill = True
                continue
            
            if in_bill and line.strip() == '\\.':
                in_bill = False
                continue
            
            if in_bill and line.strip():
                try:
                    parts = line.split('\t')
                    if len(parts) >= 10:
                        record = {
                            'bill_id': parts[0],
                            'user_id': parts[1],
                            'original_filename': parts[3] if len(parts) > 3 else None,
                            'content_type': parts[4] if len(parts) > 4 else None,
                            'file_size_bytes': int(parts[5]) if len(parts) > 5 and parts[5] != '\\N' else 0,
                            'category_bill': parts[7] if len(parts) > 7 and parts[7] != '\\N' else None,
                            'status': parts[8] if len(parts) > 8 and parts[8] != '\\N' else None,
                            'bill_created_at': pd.to_datetime(parts[-2]) if len(parts) > 1 and parts[-2] != '\\N' else None,
                        }
                        records.append(record)
                except:
                    continue
    
    return pd.DataFrame(records)


def parse_fraud_check(filepath: str) -> pd.DataFrame:
    """Parse fraud_check table for fraud analytics."""
    records = []
    in_fraud = False
    
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            line = line.rstrip('\n').rstrip('\r')
            
            if 'fraud_check' in line and 'COPY' in line and 'FROM stdin' in line:
                in_fraud = True
                continue
            
            if in_fraud and line.strip() == '\\.':
                in_fraud = False
                continue
            
            if in_fraud and line.strip():
                try:
                    parts = line.split('\t')
                    if len(parts) >= 7:
                        score = None
                        try:
                            if parts[4] != '\\N':
                                score = float(parts[4])
                        except:
                            pass
                        
                        record = {
                            'fraud_id': parts[0],
                            'bill_id': parts[1],
                            'fraud_vendor': parts[2],
                            'fraud_score': score,
                            'fraud_result': parts[5] if parts[5] != '\\N' else None,
                            'fraud_decision': parts[6] if parts[6] != '\\N' else None,
                        }
                        records.append(record)
                except:
                    continue
    
    return pd.DataFrame(records)


def get_data_quality_report(df: pd.DataFrame) -> dict:
    """Generate data quality insights."""
    report = {
        'total_records': len(df),
        'total_columns': len(df.columns),
        'missing_values': df.isnull().sum().to_dict(),
        'missing_pct': (df.isnull().sum() / len(df) * 100).round(2).to_dict(),
        'duplicate_records': df.duplicated(subset=['bill_id']).sum() if 'bill_id' in df.columns else 0,
        'data_types': df.dtypes.astype(str).to_dict(),
        'date_range': {
            'min': str(df['invoice_date'].min()) if 'invoice_date' in df.columns else 'N/A',
            'max': str(df['invoice_date'].max()) if 'invoice_date' in df.columns else 'N/A',
        },
        'unique_vendors': df['merchant_name'].nunique() if 'merchant_name' in df.columns else 0,
        'unique_categories': df['category'].nunique() if 'category' in df.columns else 0,
        'currencies': df['currency'].unique().tolist() if 'currency' in df.columns else [],
        'total_spend': df['total_amount'].sum() if 'total_amount' in df.columns else 0,
        'avg_invoice_value': df['total_amount'].mean() if 'total_amount' in df.columns else 0,
    }
    return report


if __name__ == '__main__':
    filepath = r"C:\Users\meghanar\Downloads\bocdata 1"
    print("Parsing bill_extraction data...")
    df = parse_boc_dump(filepath)
    print(f"Parsed {len(df)} records")
    print(f"Columns: {df.columns.tolist()}")
    print(f"\nSample data:")
    print(df.head())
    print(f"\nData Quality Report:")
    report = get_data_quality_report(df)
    for k, v in report.items():
        print(f"  {k}: {v}")
