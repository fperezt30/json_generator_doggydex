import pandas as pd
import json
from datetime import datetime

# Read the Excel file
import gspread
from gspread_dataframe import get_as_dataframe

#DEFAULT_PHOTO_URL
DEFAULT_PHOTO_URL = "https://offthestream.com/wp-content/uploads/2025/11/No-photo.webp"

# Path to your downloaded service account key
SERVICE_ACCOUNT_FILE = ".secrets/service_account.json"

# ID or URL of your Google Sheet
SPREADSHEET_ID = "1S3pYc6j0inIMmFs1ic38uWhCTv3GFBLn6HxDJrK8isw"

# Connect
gc = gspread.service_account(filename=SERVICE_ACCOUNT_FILE)
sh = gc.open_by_key(SPREADSHEET_ID)  # or use open_by_url("YOUR_SHEET_URL")

# Select the first worksheet
worksheet = sh.sheet1

# Convert to DataFrame
df = get_as_dataframe(worksheet, evaluate_formulas=True, dtype=str)

# Convert and sort by timestamp
df['Marca temporal'] = pd.to_datetime(df['Marca temporal'], dayfirst=True, format='%d/%m/%Y %H:%M:%S')
df = df.sort_values(by='Marca temporal', ascending=False)

dogs_list = []

def serialize(value, is_phone=False):
    """Convert non-JSON types to string, handle NaN, datetime."""
    if pd.isna(value):
        return ""
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.isoformat()
    if is_phone:
        # Convert float/int to int and then string
        try:
            return str(int(value))
        except (ValueError, TypeError):
            return str(value)
    return str(value)

for idx, row in df.iterrows():
    dog_obj = {
        "dog_id": str(idx + 1),
        "dog": {
            "name": serialize(row.get("Name")),
            "age": serialize(row.get("Age")),
            "sex": serialize(row.get("Sex")),
            "breed": serialize(row.get("Breed")),
            "photo_url": serialize(row.get("Photo")) or DEFAULT_PHOTO_URL
        },
        "owner": {
            "name": serialize(row.get("Pet owner's name")),
            "phone": serialize(row.get("Pet owner's phone"),is_phone=True),
            "preferred_contact": serialize(row.get("Preferred contact method"))
        },
        "pricing_data": {
            "last_price_boarding": serialize(row.get("Last Price / Boarding")),
            "last_price_day_care": serialize(row.get("Last Price / DayCare")),
            "outstanding_balance": serialize(row.get("Outstanding Balance"))
        },
        "feeding": {
            "times": serialize(row.get("Feeding times (you can choose more than one answer)")),
            "amount": serialize(row.get("  Amount of food per meal  "))
        },
        "walks": {
            "frequency": serialize(row.get("Going for walks (you can choose more than one answer)")),
            "duration": serialize(row.get("Approximate duration of each walk (in minutes): "))
        },

        "medical": {
            "medical_condition": serialize(row.get("Medical conditions / needs (optional)")),
            "allergies": serialize(row.get("Food or environmental intolerances ")),
            "allergies_detail": serialize(row.get("If yes, please details of any food or environmental intolerances:"))
        },

        "emergency": {
            "emergency_contact": serialize(row.get("Name of the emergency contact (not travelling with dog owner)")),
            "phone_number": serialize(row.get("Emergency contact phone number"),is_phone=True),
            "vet_name": serialize(row.get("Emergency vet name (optional)")),
            "vet_contact": serialize(row.get("Emergency vet phone number (optional)"),is_phone=True)
        },

        "behavior": {
            "barks_in_reaction_to": serialize(row.get("Barks in reaction to (If none, please just write 'None'):")),
            "afraid_of": serialize(row.get("Is afraid of (If none, please just write 'None'):")),
            "owners_remark": serialize(row.get("Some remarks we need to know:"))
        }
    }
    dogs_list.append(dog_obj)


output_path = "dogs.json"

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(dogs_list, f, ensure_ascii=False, indent=2)

print(f"Exported {len(dogs_list)} dog profiles to {output_path}")

'''
this is a comment
'''