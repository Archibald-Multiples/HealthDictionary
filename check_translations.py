from app import app, db
from models import Term
import pandas as pd

def check_missing_translations():
    # Read the Excel file
    df = pd.read_excel('learnentry_healthcare_terms_full.xlsx')
    
    with app.app_context():
        # Check for 'penis' specifically
        term = Term.query.filter_by(term_en='penis').first()
        if term:
            print(f"\nFound term 'penis':")
            print(f"English: {term.term_en}")
            print(f"Ewe: {term.term_ewe}")
            print(f"English Definition: {term.definition_en}")
            print(f"Ewe Definition: {term.definition_ewe}")
        else:
            print("\nTerm 'penis' not found in database")
            
        # Look for it in Excel
        penis_row = df[df['English Term'].str.lower() == 'penis'].first_valid_index()
        if penis_row is not None:
            print("\nFound in Excel file:")
            print(f"English: {df.loc[penis_row, 'English Term']}")
            print(f"Ewe: {df.loc[penis_row, 'Ewe Term']}")
            print(f"English Definition: {df.loc[penis_row, 'English Definition']}")
            print(f"Ewe Definition: {df.loc[penis_row, 'Ewe Definition']}")
        else:
            print("\nTerm not found in Excel file")

if __name__ == "__main__":
    check_missing_translations()
