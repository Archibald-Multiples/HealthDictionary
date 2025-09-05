from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///c:/Users/Archibald/Desktop/digital/instance/dictionary.db'
db = SQLAlchemy(app)

class Term(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    term_en = db.Column(db.String(200), nullable=False, index=True)
    term_ewe = db.Column(db.String(200), nullable=False, index=True)
    definition_en = db.Column(db.Text, nullable=False)
    definition_ewe = db.Column(db.Text, nullable=False)

def verify_term():
    with app.app_context():
        term = Term.query.filter(Term.term_en.ilike('penis')).first()
        if term:
            print(f"Term found:")
            print(f"English: {term.term_en}")
            print(f"Ewe: {term.term_ewe}")
            print(f"English Definition: {term.definition_en}")
            print(f"Ewe Definition: {term.definition_ewe}")
        else:
            print("Term not found in database")

if __name__ == '__main__':
    verify_term()
