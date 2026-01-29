import json
import os
from supabase import create_client

# Your Supabase creds
SUPABASE_URL = "https://ljepgqjlwtvxotzgdikp.supabase.co"
SUPABASE_KEY = "sb_publishable_FJWN3AMGacjf45jCfhVyAA_ZrAUmQGg"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

with open("quotes.json", "r", encoding="utf-8") as f: 
    quotes = json.load(f) 

print(f"📊 Loading {len(quotes)} quotes...")

# Clear old data
supabase.table("quotes").delete().neq("quote_id", "").execute()

# Upload all
for i, quote in enumerate(quotes):
    supabase.table("quotes").insert(quote).execute()
    if (i+1) % 50 == 0:
        print(f"{i+1}/{len(quotes)} uploaded")
 