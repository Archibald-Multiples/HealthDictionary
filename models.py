from app import db
from datetime import datetime
import openai
from werkzeug.security import generate_password_hash, check_password_hash

class Category(db.Model):
    """Model for term categories"""
    id = db.Column(db.Integer, primary_key=True)
    name_en = db.Column(db.String(100), nullable=False)
    name_ewe = db.Column(db.String(100), nullable=False)
    description_en = db.Column(db.Text)
    description_ewe = db.Column(db.Text)
    terms = db.relationship('Term', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name_en}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name_en': self.name_en,
            'name_ewe': self.name_ewe,
            'description_en': self.description_en,
            'description_ewe': self.description_ewe
        }

class Term(db.Model):
    """Model for healthcare terms"""
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

    def __repr__(self):
        return f'<Term {self.term_en}>'

    def to_dict(self):
        return {
            'id': self.id,
            'term_en': self.term_en,
            'term_ewe': self.term_ewe,
            'definition_en': self.definition_en,
            'definition_ewe': self.definition_ewe,
            'example_en': self.example_en,
            'example_ewe': self.example_ewe,
            'pronunciation': self.pronunciation,
            'category_id': self.category_id,
            'category_name_en': self.category.name_en,
            'category_name_ewe': self.category.name_ewe,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'ai_explanation_en': self.ai_explanation_en,
            'ai_explanation_ewe': self.ai_explanation_ewe
        }

class Feedback(db.Model):
    """Model for user feedback"""
    id = db.Column(db.Integer, primary_key=True)
    term_id = db.Column(db.Integer, db.ForeignKey('term.id'), nullable=True)
    feedback_type = db.Column(db.String(50), nullable=False)  # error, suggestion, new_term
    term_suggestion_en = db.Column(db.String(200))
    term_suggestion_ewe = db.Column(db.String(200))
    term_language = db.Column(db.String(10))
    description = db.Column(db.Text, nullable=False)
    contact_email = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Feedback {self.id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'term_id': self.term_id,
            'feedback_type': self.feedback_type,
            'term_suggestion_en': self.term_suggestion_en,
            'term_suggestion_ewe': self.term_suggestion_ewe,
            'term_language': self.term_language,
            'description': self.description,
            'contact_email': self.contact_email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# NOTE: After this change, you must generate and apply a database migration to add the new columns.

class AdminUser(db.Model):
    """Model for admin users"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Grok3API(db.Model):
    """Model for storing API queries and responses"""
    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.String(256), nullable=False)
    response = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'query': self.query,
            'response': self.response,
            'created_at': self.created_at
        }

# Helper function (optional, better in a service/helper file)
def generate_ai_explanation(term, definition, language='en'):
    if language == 'ewe':
        prompt = f"Explain the medical term '{term}' in Ewe for a layperson. Example: {definition}"
    else:
        prompt = f"Explain the medical term '{term}' in simple English for a layperson. Example: {definition}"

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful medical dictionary assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=200,
        temperature=0.5
    )
    return response.choices[0].message['content'].strip()