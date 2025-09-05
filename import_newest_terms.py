from app import app, db
from models import Category, Term
import pandas as pd
from datetime import datetime

def import_newest_terms():
    print("Reading Excel file...")
    df = pd.read_excel('learnentry_healthcare_terms_full.xlsx')
    
    # Focus on the newest terms (after row 115)
    new_terms_df = df.iloc[115:]  # Get all rows after 115
    print(f"\nFound {len(new_terms_df)} new terms to process")
    
    # Get category mapping
    with app.app_context():
        categories = {cat.name_en: cat.id for cat in Category.query.all()}
        
        # Keywords to help categorize terms
        category_keywords = {
            'Body Parts': ['organ', 'tissue', 'body', 'bone', 'muscle', 'blood', 'anatomy', 'part'],
            'Diseases': ['disease', 'infection', 'disorder', 'syndrome', 'condition', 'virus', 'sick', 'ill'],
            'Symptoms': ['pain', 'ache', 'feeling', 'discomfort', 'symptom', 'sign', 'sore', 'hurt'],
            'Medications': ['medicine', 'drug', 'pill', 'medication', 'tablet', 'treatment', 'cure', 'remedy'],
            'Medical Procedures': ['surgery', 'procedure', 'test', 'scan', 'examination', 'check'],
            'Medical Equipment': ['device', 'tool', 'machine', 'equipment', 'instrument'],
            'Emergency Care': ['emergency', 'urgent', 'critical', 'immediate', 'accident'],
            'Mental Health': ['mental', 'psychological', 'emotional', 'behavioral', 'fear', 'anxiety'],
            'Reproductive Health': ['pregnancy', 'birth', 'reproductive', 'fertility', 'sexual'],
            'Diagnostic Terms': ['diagnosis', 'assessment', 'evaluation', 'condition']
        }
        
        terms_added = 0
        terms_skipped = 0
        
        print("\nProcessing new terms...")
        for idx, row in new_terms_df.iterrows():
            # Skip empty rows
            if pd.isna(row['English Term']):
                continue
                
            term_en = str(row['English Term']).strip()
            definition_en = str(row['English Definition']).strip() if pd.notna(row['English Definition']) else ''
            
            # Skip if term already exists
            existing = Term.query.filter_by(term_en=term_en).first()
            if existing:
                print(f"Skipping existing term: {term_en}")
                terms_skipped += 1
                continue
            
            # Determine best category based on keywords
            scores = {cat: 0 for cat in categories.keys()}
            for category, keywords in category_keywords.items():
                for keyword in keywords:
                    if keyword.lower() in term_en.lower() or keyword.lower() in definition_en.lower():
                        scores[category] += 1
            
            # Get category with highest score, default to 'Diagnostic Terms' if no match
            best_category = max(scores.items(), key=lambda x: x[1])[0]
            if scores[best_category] == 0:
                best_category = 'Diagnostic Terms'
            
            # Handle potentially empty cells
            term_ewe = str(row['Ewe Term']) if pd.notna(row['Ewe Term']) else ''
            definition_ewe = str(row['Ewe Definition']) if pd.notna(row['Ewe Definition']) else ''
            
            # Create new term
            new_term = Term(
                term_en=term_en,
                term_ewe=term_ewe.strip(),
                definition_en=definition_en,
                definition_ewe=definition_ewe.strip(),
                category_id=categories[best_category],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            print(f"Adding term '{term_en}' to category '{best_category}'")
            db.session.add(new_term)
            terms_added += 1
            
            # Commit every 5 terms
            if terms_added % 5 == 0:
                db.session.commit()
                print(f"Committed {terms_added} terms so far...")
        
        # Final commit
        if terms_added % 5 != 0:
            db.session.commit()
        
        print(f"\nImport complete!")
        print(f"Terms added: {terms_added}")
        print(f"Terms skipped: {terms_skipped}")
        print(f"Total processed: {terms_added + terms_skipped}")

if __name__ == "__main__":
    import_newest_terms()
