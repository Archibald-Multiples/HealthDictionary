from app import app, db
from models import Term, Category
from datetime import datetime

# Only keep one 'Blood Test' in the database with the correct description
def deduplicate_blood_test():
    with app.app_context():
        # Find all 'Blood Test' terms (case-insensitive)
        blood_tests = Term.query.filter(Term.term_en.ilike('%blood test%')).all()
        if not blood_tests:
            print("No 'Blood Test' terms found.")
            return
        # Keep the first, update it with the correct info, delete the rest
        keep = blood_tests[0]
        keep.term_en = "Blood Test"
        keep.term_ewe = "Ʋukpɔkpɔ"
        keep.definition_en = "An examination of a sample of blood to determine its composition and to diagnose disease."
        keep.definition_ewe = "Ʋu ƒe dodokpɔ si wowɔna be woanya ne dɔvɔ̃ aɖe le ame ŋu."
        keep.example_en = None
        keep.example_ewe = None
        keep.updated_at = datetime.utcnow()
        for dup in blood_tests[1:]:
            db.session.delete(dup)
        db.session.commit()
        print(f"Deduplicated 'Blood Test'. Now only one remains with the correct description.")

if __name__ == "__main__":
    deduplicate_blood_test()
