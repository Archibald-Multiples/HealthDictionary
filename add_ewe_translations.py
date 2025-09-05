from app import app, db
from models import Term

# Add your English-to-Ewe translations here	ranslations = {
    "headache": "kɔkɔ",
    "fever": "dzɔdzɔ",
    "cough": "kɔkɔkɔ",
    # Add more terms as needed
}

with app.app_context():
    for en, ewe in translations.items():
        term = Term.query.filter_by(term_en=en).first()
        if term:
            term.term_ewe = ewe
            print(f"Updated: {en} -> {ewe}")
        else:
            print(f"Term not found: {en}")
    db.session.commit()
    print("Ewe translations updated!")
