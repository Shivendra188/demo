import pandas as pd
from datetime import date, timedelta
import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def fix_phone(phone_raw):
    """Convert 9.18138E+11 → +919181380000"""
    if pd.isna(phone_raw):
        return None
    
    # Scientific notation → int → string → +91
    phone_str = str(int(float(phone_raw)))
    if phone_str.startswith('9') and len(phone_str) == 10:
        return f"+91{phone_str}"
    return phone_str

def load_customers(csv_path: str):
    """Fix phone + load customers"""
    df = pd.read_csv(csv_path)
    
    data = []
    for _, row in df.iterrows():
        data.append({
            'customer_id': row['customer_id'],
            'name': row['name'],
            'phone': fix_phone(row['phone'])  # Magic fix!
        })
    
    # Clear + upsert
    supabase.table("customers").delete().neq("customer_id", "").execute()
    supabase.table("customers").insert(data).execute()
    print(f"Loaded {len(data)} customers with fixed phones")


def load_policies(csv_path: str):
    df = pd.read_csv(csv_path)
    today = date.today()
    expiry_threshold = today + timedelta(days=30)

    data = []
    for _, row in df.iterrows():
        expiry_date = pd.to_datetime(row['expiry_date']).date()
        
        #  3-state dynamic status
        if expiry_date < today:
            status = "Expired"
        elif today <= expiry_date <= expiry_threshold:
            status = "Expiring"
        else:
            status = "Active"
        
        data.append({
            'policy_id': row['policy_id'],
            'customer_id': row['customer_id'],
            'policy_type': row['policy_type'],
            'insurer': row.get('insurer', 'Demo Insurer'),
            'premium': float(row['premium']),
            'policy_start': pd.to_datetime(row['start_date']).strftime('%Y-%m-%d'),
            'policy_expiry': expiry_date.strftime('%Y-%m-%d'),
            'status': status  # Dynamic!
        })
    
    # Clear + batch insert
    supabase.table("policies").delete().neq("policy_id", "").execute()
    for i in range(0, len(data), 100):
        supabase.table("policies").insert(data[i:i+100]).execute()
    

if __name__ == "__main__":
    load_customers("customers.csv")
    load_policies("policies.csv")
    print("loaded!")

