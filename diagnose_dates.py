"""
Diagnostic script: Investigate date anomalies in the BOC dataset.
"""
import pandas as pd
import sys
sys.path.insert(0, '.')
from data_parser import parse_boc_dump

filepath = r"C:\Users\meghanar\Downloads\bocdata 1"

print("=" * 60)
print("1. DATASET SOURCE VERIFICATION")
print("=" * 60)
print(f"  File being loaded: {filepath}")

import os
if os.path.exists(filepath):
    size = os.path.getsize(filepath)
    print(f"  File exists: YES")
    print(f"  File size: {size:,} bytes ({size/1024/1024:.1f} MB)")
else:
    print(f"  File exists: NO — THIS IS THE PROBLEM")
    sys.exit(1)

print("\n  Parsing data...")
df = parse_boc_dump(filepath)

print(f"  Total records loaded: {len(df)}")

print("\n" + "=" * 60)
print("2. DATE COLUMN ANALYSIS")
print("=" * 60)
print(f"  invoice_date dtype: {df['invoice_date'].dtype}")
print(f"  Non-null dates: {df['invoice_date'].notna().sum()}")
print(f"  Null dates: {df['invoice_date'].isna().sum()}")
print(f"\n  df['invoice_date'].min() = {df['invoice_date'].min()}")
print(f"  df['invoice_date'].max() = {df['invoice_date'].max()}")
print(f"\n  df['invoice_date'].describe():")
print(df['invoice_date'].describe())

print("\n" + "=" * 60)
print("3. DATE DISTRIBUTION BY YEAR")
print("=" * 60)
valid_dates = df.dropna(subset=['invoice_date'])
valid_dates_yr = valid_dates['invoice_date'].dt.year.value_counts().sort_index()
print(valid_dates_yr.to_string())

print("\n" + "=" * 60)
print("4. RECORDS BEFORE 2025 (SUSPECT)")
print("=" * 60)
before_2025 = df[df['invoice_date'] < '2025-01-01']
print(f"  Count: {len(before_2025)}")
if not before_2025.empty:
    print(f"\n  Sample rows with dates BEFORE 2025:")
    cols = ['bill_id', 'merchant_name', 'invoice_date', 'total_amount', 'currency', 'category']
    cols = [c for c in cols if c in before_2025.columns]
    print(before_2025[cols].head(20).to_string(index=False))

today = pd.Timestamp.now()
print("\n" + "=" * 60)
print("5. RECORDS AFTER TODAY ({})".format(today.strftime('%Y-%m-%d')))
print("=" * 60)
after_today = df[df['invoice_date'] > today]
print(f"  Count: {len(after_today)}")
if not after_today.empty:
    print(f"\n  Sample rows with dates AFTER today:")
    cols = ['bill_id', 'merchant_name', 'invoice_date', 'total_amount', 'currency', 'category']
    cols = [c for c in cols if c in after_today.columns]
    print(after_today[cols].head(20).to_string(index=False))

print("\n" + "=" * 60)
print("6. CHECKING FOR DUMMY/SYNTHETIC DATA SOURCES")
print("=" * 60)

# Check if any file in cwd generates or contains dummy data
import glob
py_files = glob.glob("*.py")
for f in py_files:
    with open(f, 'r', encoding='utf-8', errors='replace') as fh:
        content = fh.read().lower()
        has_random = 'random' in content and ('date' in content or 'sample' in content)
        has_dummy = 'dummy' in content or 'fake' in content or 'synthetic' in content
        has_generate = 'generate' in content and 'data' in content
        if has_random or has_dummy or has_generate:
            print(f"  ⚠️  {f}: may contain dummy/synthetic data generation code")
        else:
            print(f"  ✅  {f}: no dummy data generation found")

# Check if app.py has any fallback DataFrame creation
with open('app.py', 'r', encoding='utf-8', errors='replace') as fh:
    app_content = fh.read()
    if 'pd.DataFrame({' in app_content or 'pd.DataFrame([' in app_content:
        print(f"\n  ⚠️  app.py: contains inline DataFrame creation (possible fallback)")
    else:
        print(f"\n  ✅  app.py: no inline fallback DataFrames")

print("\n" + "=" * 60)
print("7. RAW DATE STRINGS FROM THE DUMP FILE (first 10 bill_extraction rows)")
print("=" * 60)
# Read raw date strings from the dump to see what's being parsed
import re
with open(filepath, 'r', encoding='utf-8', errors='replace') as fh:
    in_be = False
    count = 0
    for line in fh:
        line = line.rstrip('\n').rstrip('\r')
        if 'bill_extraction' in line and 'COPY' in line and 'FROM stdin' in line:
            in_be = True
            print(f"  COPY header: {line[:120]}")
            continue
        if in_be and line.strip() == '\\.':
            in_be = False
            break
        if in_be and line.strip():
            parts = line.split('\t')
            date_str = parts[4] if len(parts) > 4 else 'N/A'
            print(f"  Row {count}: date_field(col4) = '{date_str}'")
            count += 1
            if count >= 10:
                break

print("\n" + "=" * 60)
print("8. SUMMARY & RECOMMENDATION")
print("=" * 60)
valid_2025 = df[(df['invoice_date'] >= '2025-01-01') & (df['invoice_date'] <= today)]
print(f"  Total records: {len(df)}")
print(f"  Records with valid dates (2025 to today): {len(valid_2025)}")
print(f"  Records to REMOVE (before 2025): {len(before_2025)}")
print(f"  Records to REMOVE (after today): {len(after_today)}")
print(f"  Records with null dates: {df['invoice_date'].isna().sum()}")
print(f"\n  After cleaning:")
print(f"    New min date: {valid_2025['invoice_date'].min()}")
print(f"    New max date: {valid_2025['invoice_date'].max()}")
