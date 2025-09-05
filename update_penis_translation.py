from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///c:/Users/Archibald/Desktop/digital/instance/dictionary.db'
db = SQLAlchemy(app)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_en = db.Column(db.String(100), nullable=False)
    name_ewe = db.Column(db.String(100), nullable=False)
    description_en = db.Column(db.Text)
    description_ewe = db.Column(db.Text)
    terms = db.relationship('Term', backref='category', lazy=True)

class Term(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    term_en = db.Column(db.String(200), nullable=False, index=True)
    term_ewe = db.Column(db.String(200), nullable=False, index=True)
    definition_en = db.Column(db.Text, nullable=False)
    definition_ewe = db.Column(db.Text, nullable=False)
    example_en = db.Column(db.Text)
    example_ewe = db.Column(db.Text)
    pronunciation = db.Column(db.String(200))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ai_explanation_en = db.Column(db.Text)
    ai_explanation_ewe = db.Column(db.Text)

def update_penis_translation():
    with app.app_context():
        # Find the term in the database
        term = Term.query.filter(Term.term_en.ilike('penis')).first()
        if term:
            # Update with the Excel file data
            term.term_ewe = "ŋutsu ƒe vidzinu"
            term.definition_ewe = "nan"
            # Keep other fields unchanged
            db.session.commit()
            print("Successfully updated translation for 'penis'")
            print(f"Updated term: {term.term_en}")
            print(f"New Ewe translation: {term.term_ewe}")
            print(f"New Ewe definition: {term.definition_ewe}")
        else:
            # If term doesn't exist, create it with required fields
            print("Term 'penis' not found, creating new entry")
            category = Category.query.first()  # Get any category for now
            new_term = Term(
                term_en='penis',
                term_ewe="ŋutsu ƒe vidzinu",
                definition_en='The male reproductive organ involved in urination and reproduction',
                definition_ewe="nan",
                category_id=category.id if category else 1
            )
            db.session.add(new_term)
            db.session.commit()
            print("Successfully created new term 'penis' with translation")

if __name__ == '__main__':
    update_penis_translation()
