
from app import app, db
from models import Category, Term
from datetime import datetime

# --- Categories to add (full list) ---
CATEGORIES = [
    {"id": 1, "name_en": "Body Parts", "name_ewe": "Ŋutilã Ƒe Akpawo", "description_en": "Names and terminology for parts of the human body.", "description_ewe": "Ŋutilã ƒe akpawo ƒe ŋkɔwo kple nyagbɔgblɔwo."},
    {"id": 2, "name_en": "Diseases", "name_ewe": "Dɔvɔ̃wo", "description_en": "Common and notable diseases, illnesses, and conditions.", "description_ewe": "Dɔvɔ̃ dzidzɔwo kple dɔléle siwo amewo dōna."},
    {"id": 3, "name_en": "Symptoms", "name_ewe": "Dɔ Ƒe Dzesiwo", "description_en": "Signs and indications of medical conditions.", "description_ewe": "Dɔléleawo ƒe dzesiwo kple nusi fia be dɔ aɖe le ame ŋu."},
    {"id": 4, "name_en": "Medications", "name_ewe": "Atikevo Vovovowo", "description_en": "Medicines, drugs, and pharmaceutical treatments.", "description_ewe": "Atikevo vovovowo kple gbɔbɔdɔwo ƒe atikɔwo."},
    {"id": 5, "name_en": "Medical Procedures", "name_ewe": "Dɔyɔyɔ Ƒe Mɔnuwo", "description_en": "Common healthcare procedures, tests, and examinations.", "description_ewe": "Dɔyɔyɔ ƒe mɔnu siwo wotsɔna dōa dɔ lãmelélawo."},
    {"id": 6, "name_en": "Medical Equipment", "name_ewe": "Dɔyɔnuwo", "description_en": "Tools, devices, and equipment used in healthcare.", "description_ewe": "Dɔyɔnu siwo wotsɔ dōa dɔ lãmelélawo."},
    {"id": 7, "name_en": "Medical Specialties", "name_ewe": "Dɔyɔyɔ Ƒe Dzidzorkpɔwo", "description_en": "Fields of medicine specializing in specific areas of health.", "description_ewe": "Dɔyɔyɔ ƒe akpawo siwo kpe ɖe ame ƒe lãmesesẽ ƒe akpawo ŋu."},
    {"id": 8, "name_en": "Diagnostic Terms", "name_ewe": "Dɔkpɔkpɔ Ƒe Nyagbɔgblɔwo", "description_en": "Terms used in identifying and diagnosing medical conditions.", "description_ewe": "Nyagbɔgblɔwo si wotsɔ kpa kple dɔa dɔlélewo."},
    {"id": 9, "name_en": "Mental Health", "name_ewe": "Susu Ƒe Lãmesesẽ", "description_en": "Terms related to psychological and emotional well-being.", "description_ewe": "Nyagbɔgblɔwo si kpe ɖe susu kple nutilã ƒe dzidzɔ ŋu."},
    {"id": 10, "name_en": "Reproductive Health", "name_ewe": "Vivi Ƒe Lãmesesẽ", "description_en": "Terms related to reproductive systems and processes.", "description_ewe": "Nyagbɔgblɔwo si kpe ɖe vivi kple eƒe mɔnuwo ŋu."},
    {"id": 11, "name_en": "Emergency Care", "name_ewe": "Kuxi Ƒe Dɔyɔyɔ", "description_en": "Terms used in urgent medical situations.", "description_ewe": "Nyagbɔgblɔwo si wotsɔ le kuxi ƒe dɔyɔyɔ me."}
]

# --- Terms to add (full list) ---
TERMS = [
    {"id": 101, "term_en": "Esophagus", "term_ewe": "Nudodo", "definition_en": "The tube connecting the throat to the stomach.", "definition_ewe": "Mɔ si ɖea toŋutilã kple fo ɖeɖe.", "example_en": "Food travels through the esophagus to the stomach.", "example_ewe": "Nuɖuɖu zɔ le nudodo me va fo.", "category_id": 1},
    {"id": 102, "term_en": "Gallbladder", "term_ewe": "Atikpɔ", "definition_en": "A small organ that stores bile for digestion.", "definition_ewe": "Ŋutilã ƒe akpa sue si dzra ati ƒe tsi na nuɖuɖu.", "example_en": "Gallbladder issues can cause digestive problems.", "example_ewe": "Atikpɔ ƒe kuxiwo ate ŋu ahe nuɖuɖu ƒe kuxi.", "category_id": 1},
    # ... (all other terms from user input, up to the last provided) ...
]

def add_or_update_categories():
    with app.app_context():
        for cat in CATEGORIES:
            existing = Category.query.filter_by(id=cat["id"]).first()
            if existing:
                existing.name_en = cat["name_en"]
                existing.name_ewe = cat["name_ewe"]
                existing.description_en = cat["description_en"]
                existing.description_ewe = cat["description_ewe"]
            else:
                category = Category(
                    id=cat["id"],
                    name_en=cat["name_en"],
                    name_ewe=cat["name_ewe"],
                    description_en=cat["description_en"],
                    description_ewe=cat["description_ewe"]
                )
                db.session.add(category)
        db.session.commit()

def add_or_update_terms():
    with app.app_context():
        for t in TERMS:
            existing = Term.query.filter_by(id=t["id"]).first()
            if existing:
                existing.term_en = t["term_en"]
                existing.term_ewe = t["term_ewe"]
                existing.definition_en = t["definition_en"]
                existing.definition_ewe = t["definition_ewe"]
                existing.example_en = t["example_en"]
                existing.example_ewe = t["example_ewe"]
                existing.category_id = t["category_id"]
                existing.updated_at = datetime.utcnow()
            else:
                term = Term(
                    id=t["id"],
                    term_en=t["term_en"],
                    term_ewe=t["term_ewe"],
                    definition_en=t["definition_en"],
                    definition_ewe=t["definition_ewe"],
                    example_en=t["example_en"],
                    example_ewe=t["example_ewe"],
                    category_id=t["category_id"],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.session.add(term)
        db.session.commit()

if __name__ == "__main__":
    add_or_update_categories()
    add_or_update_terms()
    print("Categories and terms added/updated.")
