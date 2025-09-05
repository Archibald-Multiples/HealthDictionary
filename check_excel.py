from app import app, db
from models import Category, Term
import pandas as pd

def show_categories():
    with app.app_context():
        categories = Category.query.all()
        print("\nAvailable Categories:")
        print("--------------------")
        for cat in categories:
            print(f"{cat.id}: {cat.name_en}")

def import_excel():
    file_path = "learnentry_healthcare_terms_full.xlsx"
    
    # Read Excel file
    df = pd.read_excel(file_path)
    print(f"\nFound {len(df)} terms in Excel file")
    
    # Show first few rows
    print("\nFirst few terms from Excel:")
    print(df.head())
    
    return df

if __name__ == "__main__":
    show_categories()
    df = import_excel()
