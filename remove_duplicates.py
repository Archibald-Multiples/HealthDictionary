"""
Script to remove duplicate terms from the Term table in the database.
Duplicates are defined as having the same English term (term_en) and category_id.
"""

from app import app, db
from models import Term
from collections import defaultdict

def remove_duplicate_terms():
    with app.app_context():
        # Normalize term_en (lowercase, strip spaces) and group by category_id
        seen = defaultdict(list)
        for term in Term.query.all():
            norm_en = term.term_en.lower().strip() if term.term_en else ''
            key = (norm_en, term.category_id)
            seen[key].append(term)
        removed = 0
        for key, terms in seen.items():
            if len(terms) > 1:
                # Keep the first, delete the rest
                for dup in terms[1:]:
                    db.session.delete(dup)
                    removed += 1
        db.session.commit()
        print(f"Removed {removed} near-duplicate terms.")

if __name__ == "__main__":
    remove_duplicate_terms()
