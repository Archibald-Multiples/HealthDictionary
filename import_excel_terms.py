from app import app, db
from models import Term, Category
import pandas as pd
from datetime import datetime
import sys
import os

def import_terms_from_excel(excel_file_path, category_id):
    """
    Import terms from an Excel file into the database
    
    Args:
        excel_file_path (str): Path to the Excel file
        category_id (int): ID of the category to assign terms to
    """
    # Read the Excel file
    df = pd.read_excel(excel_file_path)
    
    # Initialize counters
    added = 0
    skipped = 0
    errors = 0
        
    with app.app_context():
            # Verify category exists
            category = Category.query.get(category_id)
            if not category:
                print(f"Error: Category ID {category_id} not found")
                return
            
            # Process each row
            for index, row in df.iterrows():
                try:
                    # Check if term already exists
                    existing_term = Term.query.filter_by(
                        term_en=row['English Term'],
                        category_id=category_id
                    ).first()
                    
                    if existing_term:
                        print(f"Skipping existing term: {row['English Term']}")
                        skipped += 1
                        continue
                    
                    # Create new term
                    new_term = Term(
                        term_en=row['English Term'],
                        term_ewe=row['Ewe Term'],
                        definition_en=row['English Definition'],
                        definition_ewe=row['Ewe Definition'],
                        category_id=category_id,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    
                    db.session.add(new_term)
                    added += 1
                    
                    # Commit every 10 terms to avoid large transactions
                    if added % 10 == 0:
                        db.session.commit()
                        print(f"Imported {added} terms...")
                    
                except Exception as e:
                    errors += 1
                    print(f"Error importing term '{row['English Term']}': {str(e)}")
                    continue
            
            # Final commit for remaining terms
            try:
                db.session.commit()
            except Exception as e:
                print(f"Error during final commit: {str(e)}")
                db.session.rollback()
            
            print("\nImport Summary:")
            print(f"Terms added: {added}")
            print(f"Terms skipped (already exist): {skipped}")
            print(f"Errors: {errors}")

def list_categories():
    """List all available categories to help user choose category_id"""
    with app.app_context():
        categories = Category.query.all()
        print("\nAvailable Categories:")
        print("--------------------")
        for category in categories:
            print(f"ID: {category.id} - {category.name_en} ({category.name_ewe})")

if __name__ == "__main__":
    # First, show available categories
    list_categories()
    
    # Get input from user
    excel_path = input("\nEnter the path to your Excel file: ")
    category_id = int(input("Enter the category ID for these terms: "))
    
    # Import the terms
    import_terms_from_excel(excel_path, category_id)
