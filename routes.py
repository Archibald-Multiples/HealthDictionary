from flask import render_template, request, jsonify, redirect, url_for, flash, session
from sqlalchemy import or_
from app import app, db
from models import Term, Category, Feedback, AdminUser, generate_ai_explanation, Grok3API
import os
import openai
from flask_mail import Mail, Message
import requests

# --- Glosbe API integration ---


# Set your OpenAI API key (store securely in production!)
openai.api_key = os.environ.get("OPENAI_API_KEY", "sk-...your-key...")

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'changeme')  # Set a secure password in environment

# Flask-Mail config (set these in your app config or environment)
app.config['MAIL_SERVER'] = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.environ.get('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'alleyedem@gmail.com')
app.config['MAIL_PASSWORD'] = 'cuqs wvue whlp nikq'  # Gmail app password set directly
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_DEFAULT_SENDER', 'alleyedem@gmail.com')
mail = Mail(app)

def is_admin():
    return session.get('is_admin') is True

@app.route('/')
def index():
    """Home page with search form"""
    recent_terms = Term.query.order_by(Term.created_at.desc()).limit(10).all()
    categories = Category.query.all()
    return render_template('index.html', recent_terms=recent_terms, categories=categories)

@app.route('/about')
def about():
    """About page with information about the dictionary"""
    return render_template('about.html')

@app.route('/search')
def search():
    """Search page for finding terms"""
    query = request.args.get('q', '')
    category_id = request.args.get('category', '')
    
    # Base query
    terms_query = Term.query

    # Apply filters if provided
    if query:
        # Only match exact term or close match, not substring in unrelated words
        terms_query = terms_query.filter(
            or_(
                Term.term_en.ilike(f'{query}'),
                Term.term_en.ilike(f'{query.capitalize()}'),
                Term.term_en.ilike(f'{query.lower()}'),
                Term.term_en.ilike(f'{query.title()}'),
                Term.term_en.ilike(f'% {query} %'),
                Term.term_ewe.ilike(f'{query}'),
                Term.term_ewe.ilike(f'{query.capitalize()}'),
                Term.term_ewe.ilike(f'{query.lower()}'),
                Term.term_ewe.ilike(f'{query.title()}'),
                Term.term_ewe.ilike(f'% {query} %')
            )
        )

    if category_id and category_id.isdigit():
        terms_query = terms_query.filter(Term.category_id == int(category_id))

    # Only show terms that have a valid category (not None)
    terms = [t for t in terms_query.order_by(Term.term_en).all() if t.category_id is not None]
    categories = Category.query.all()


    ewe_translation = None
    show_explanation = False
    def google_translate(text, target_lang='ee', source_lang='en'):
        url = 'https://translate.googleapis.com/translate_a/single'
        params = {
            'client': 'gtx',
            'sl': source_lang,
            'tl': target_lang,
            'dt': 't',
            'q': text
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data[0][0][0]
        except Exception as e:
            return f"Error: {e}"

    if query and not terms:
        ewe_translation = google_translate(query, target_lang='ee', source_lang='en')
        show_explanation = True
    elif query and terms:
        first_term = terms[0]
        if not getattr(first_term, 'term_ewe', None):
            ewe_translation = google_translate(first_term.term_en, target_lang='ee', source_lang='en')
            show_explanation = True
    return render_template('search.html', 
                           terms=terms, 
                           query=query, 
                           selected_category=category_id,
                           categories=categories,
                           ewe_translation=ewe_translation,
                           show_explanation=show_explanation)

@app.route('/term/<int:term_id>')
def term_detail(term_id):
    """Detail page for a specific term"""
    term = Term.query.get_or_404(term_id)
    return render_template('term.html', term=term)

@app.route('/categories')
def categories():
    """Categories overview page"""
    categories = Category.query.all()
    return render_template('categories.html', categories=categories)

@app.route('/category/<int:category_id>')
def category_detail(category_id):
    """List of terms in a specific category"""
    category = Category.query.get_or_404(category_id)
    terms = Term.query.filter_by(category_id=category_id).order_by(Term.term_en).all()
    return render_template('search.html', 
                           terms=terms, 
                           selected_category=category_id,
                           category=category,
                           categories=Category.query.all())

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    """Feedback submission form and handling"""
    if request.method == 'POST':
        term_id = request.form.get('term_id')
        feedback_type = request.form.get('feedback_type')
        term_suggestion_en = request.form.get('term_suggestion_en')
        term_suggestion_ewe = request.form.get('term_suggestion_ewe')
        term_language = request.form.get('term_language')
        description_en = request.form.get('description_en')
        description_ewe = request.form.get('description_ewe')
        contact_email = request.form.get('contact_email')

        # Simple validation
        if not feedback_type:
            flash('Please select a feedback type / Taflatse tia susuɖeɖegblɔ ƒomevi aɖe', 'danger')
            return redirect(url_for('feedback'))

        if feedback_type == 'new_term':
            if not description_en or not description_ewe:
                flash('Please provide descriptions in both English and Ewe / Taflatse ŋlɔ nyagbɔgblɔa ƒe gɔmeɖeɖe le English kple Eʋegbe me', 'danger')
                return redirect(url_for('feedback'))
        else:
            # For other feedback types, use description_en as the main description
            description_en = description_en or description_ewe  # Use whichever is provided
            if not description_en:
                flash('Please provide a description / Taflatse ŋlɔ nyagbɔgblɔa ƒe gɔmeɖeɖe', 'danger')
                return redirect(url_for('feedback'))

        # Create new feedback
        new_feedback = Feedback(
            term_id=term_id if term_id and term_id.isdigit() else None,
            feedback_type=feedback_type,
            term_suggestion_en=term_suggestion_en,
            term_suggestion_ewe=term_suggestion_ewe,
            term_language=term_language,
            description=f"English: {description_en}\n\nEwe: {description_ewe}",
            contact_email=contact_email
        )

        success_message = False
        try:
            db.session.add(new_feedback)
            db.session.commit()
            success_message = True
            
            # Send confirmation email if user provided an email
            if contact_email:
                try:
                    msg = Message(
                        "Feedback Submitted Successfully",
                        recipients=[contact_email],
                        body="Thank you for your feedback! Your suggestion has been received. An admin may contact you if needed."
                    )
                    mail.send(msg)
                except Exception as e:
                    print(f"Error sending confirmation email: {e}")
                    # Email error doesn't affect overall success
                    
        except Exception as e:
            db.session.rollback()
            flash('Error submitting feedback / Vodada le susuɖeɖegblɔa ɖoɖo me', 'danger')
            return redirect(url_for('feedback'))

        if success_message:
            flash('Feedback submitted successfully thank you', 'success')
        
        return redirect(url_for('index'))
    
    # For GET requests
    term_id = request.args.get('term_id')
    term = None
    if term_id and term_id.isdigit():
        term = Term.query.get(term_id)
        ai_explanation_en = generate_ai_explanation(term.term_en, term.definition_en, language='en')
        term.ai_explanation_en = ai_explanation_en
        db.session.commit()
    
    return render_template('feedback.html', term=term)

@app.route('/terms')
def term_list():
    terms = Term.query.all()
    return render_template('term_list.html', terms=terms)

# API routes for offline functionality

@app.route('/api/terms', methods=['GET'])
def get_terms():
    """API endpoint to get all terms for offline storage"""
    terms = Term.query.all()
    return jsonify([term.to_dict() for term in terms])

@app.route('/api/categories', methods=['GET'])
def get_categories():
    """API endpoint to get all categories for offline storage"""
    categories = Category.query.all()
    return jsonify([category.to_dict() for category in categories])

@app.route('/api/search', methods=['GET'])
def api_search():
    """API endpoint for search functionality"""
    query = request.args.get('q', '')
    category_id = request.args.get('category', '')
    language = request.args.get('lang', 'en')  # 'en' or 'ewe'
    
    # Base query
    terms_query = Term.query
    
    # Apply filters if provided
    if query:
        if language == 'en':
            terms_query = terms_query.filter(
                or_(
                    Term.term_en.ilike(f'%{query}%'),
                    Term.definition_en.ilike(f'%{query}%')
                )
            )
        else:
            terms_query = terms_query.filter(
                or_(
                    Term.term_ewe.ilike(f'%{query}%'),
                    Term.definition_ewe.ilike(f'%{query}%')
                )
            )
    
    if category_id and category_id.isdigit():
        terms_query = terms_query.filter(Term.category_id == int(category_id))
    
    # Get results and convert to dict
    terms = [term.to_dict() for term in terms_query.all()]
    
    return jsonify(terms)

@app.route('/api/term/<int:term_id>', methods=['GET'])
def get_term(term_id):
    """API endpoint to get a specific term"""
    term = Term.query.get_or_404(term_id)
    return jsonify(term.to_dict())

@app.route('/api/feedback', methods=['POST'])
def submit_feedback():
    """API endpoint for submitting feedback"""
    data = request.json
    
    # Create new feedback
    new_feedback = Feedback(
        term_id=data.get('term_id'),
        feedback_type=data.get('feedback_type'),
        term_suggestion=data.get('term_suggestion'),
        term_language=data.get('term_language'),
        description=data.get('description'),
        contact_email=data.get('contact_email')
    )
    
    db.session.add(new_feedback)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Feedback submitted successfully'})

@app.route('/api/explain', methods=['POST'])
def explain_term():
    data = request.get_json()
    term = data.get('term')
    language = data.get('language', 'en')

    if not term:
        return jsonify({'error': 'No term provided'}), 400

    prompt = f"Explain the medical term '{term}' in simple, clear {language.upper()} for a layperson."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful medical dictionary assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.5
        )
        explanation = response.choices[0].message['content'].strip()
        return jsonify({'explanation': explanation})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/auth', methods=['GET', 'POST'])
def admin_auth():
    mode = request.args.get('mode', 'login')
    if request.method == 'POST':
        action = request.form.get('action')
        username = request.form.get('username')
        password = request.form.get('password')
        if action == 'signup':
            if not username or not password:
                flash('Username and password required.', 'danger')
            elif AdminUser.query.filter_by(username=username).first():
                flash('Username already exists.', 'danger')
            else:
                admin = AdminUser(username=username)
                admin.set_password(password)
                db.session.add(admin)
                db.session.commit()
                flash('Admin account created. Please log in.', 'success')
                return redirect(url_for('admin_auth', mode='login'))
            mode = 'signup'
        elif action == 'login':
            admin = AdminUser.query.filter_by(username=username).first()
            if admin and admin.check_password(password):
                session['is_admin'] = True
                session['admin_username'] = username
                flash('Logged in as admin.', 'success')
                return redirect(url_for('admin_feedback'))
            else:
                flash('Invalid credentials.', 'danger')
                mode = 'login'
    return render_template('admin_auth.html', mode=mode)

@app.route('/admin/login')
def admin_login():
    return redirect(url_for('admin_auth', mode='login'))

@app.route('/admin/signup')
def admin_signup():
    return redirect(url_for('admin_auth', mode='signup'))

@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    session.pop('admin_username', None)
    flash('Logged out.', 'success')
    return redirect(url_for('admin_login'))

from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin():
            flash('Admin login required.', 'warning')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/feedback')
@admin_required
def admin_feedback():
    """Admin page to view all feedback submissions"""
    feedback_list = Feedback.query.order_by(Feedback.id.desc()).all()
    return render_template('admin_feedback.html', feedback_list=feedback_list)

@app.route('/admin/feedback/delete/<int:feedback_id>', methods=['POST'])
@admin_required
def delete_feedback(feedback_id):
    """Delete a feedback entry (admin only)"""
    feedback = Feedback.query.get_or_404(feedback_id)
    db.session.delete(feedback)
    db.session.commit()
    flash('Feedback deleted.', 'success')
    return redirect(url_for('admin_feedback'))

@app.route('/admin/feedback/reply/<int:feedback_id>', methods=['POST'])
@admin_required
def reply_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    reply_message = request.form.get('reply_message')
    if not feedback.contact_email:
        flash('No user email to reply to.', 'danger')
        return redirect(url_for('admin_feedback'))
    if not reply_message:
        flash('Reply message required.', 'danger')
        return redirect(url_for('admin_feedback'))
    import traceback
    try:
        msg = Message(f"Reply to your feedback (ID {feedback.id})",
                      recipients=[feedback.contact_email],
                      body=reply_message)
        mail.send(msg)
        flash('Reply sent to user.', 'success')
    except Exception as e:
        print('Error sending email:', e)
        print(traceback.format_exc())
        flash(f'Error sending email: {e}', 'danger')
    return redirect(url_for('admin_feedback'))

@app.route('/admin/feedback/approve/<int:feedback_id>', methods=['POST'])
@admin_required
def approve_suggestion(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    # Only process if it's a term suggestion
    if not (feedback.term_suggestion_en or feedback.term_suggestion_ewe):
        flash('No valid term suggestion in this feedback.', 'danger')
        return redirect(url_for('admin_feedback'))
    # Check if term already exists (by English or Ewe term)
    exists = Term.query.filter(
        (Term.term_en == feedback.term_suggestion_en) | (Term.term_ewe == feedback.term_suggestion_ewe)
    ).first()
    if exists:
        flash('This term already exists in the dictionary.', 'warning')
        return redirect(url_for('admin_feedback'))
    # Add new term (minimal info, admin can edit later)
    suggestion_en = feedback.term_suggestion_en or ''
    suggestion_ewe = feedback.term_suggestion_ewe or ''
    language = (feedback.term_language or '').lower()
    # Automatically use correct Ewe term and description for 'penis'
    if suggestion_ewe == 'penis' and language == 'ewe':
        term_en = '[English translation needed]'
        term_ewe = 'Ŋutsudɔ'
        definition_en = '[English definition needed]'
        definition_ewe = 'Ŋutsuvi ƒe ŋutilã ƒe akpa si kpe ɖe tsiɖeɖe kple vivi ŋu.'
    else:
        term_en = suggestion_en or '[English translation needed]'
        term_ewe = suggestion_ewe or '[Ewe translation needed]'
        definition_en = feedback.description or '[English definition needed]'
        definition_ewe = '[Ewe definition needed]'
    # Use a default category if none is provided (e.g., first category or create 'Uncategorized')
    default_category = Category.query.first()
    category_id = default_category.id if default_category else 1  # Fallback to 1 if no categories exist
    new_term = Term(
        term_en=term_en,
        term_ewe=term_ewe,
        definition_en=definition_en,
        definition_ewe=definition_ewe,
        example_en='',
        example_ewe='',
        category_id=category_id
    )
    db.session.add(new_term)
    db.session.commit()
    flash('Suggested term added to the dictionary. Please edit to complete details.', 'success')
    return redirect(url_for('admin_feedback'))

@app.route('/admin/feedback/reject/<int:feedback_id>', methods=['POST'])
@admin_required
def reject_suggestion(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    db.session.delete(feedback)
    db.session.commit()
    flash('Suggestion rejected and removed.', 'info')
    return redirect(url_for('admin_feedback'))

@app.errorhandler(404)
def page_not_found(e):
    """Custom 404 page"""
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    """Custom 500 page"""
    return render_template('500.html'), 500

# Utility function to call Grok 3 API

def call_grok3_api(query, language='en'):
    """Call Grok 3 API for term explanation or translation."""
    api_url = os.environ.get('GROK3_API_URL', 'https://api.grok3.com/explain')
    api_key = os.environ.get('GROK3_API_KEY', 'your-grok3-key')
    payload = {
        'query': query,
        'language': language
    }
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get('explanation', '')
    except Exception as e:
        return f"Error: {e}"

@app.route('/api/grok3/explain', methods=['GET', 'POST'])
def grok3_explain():
    if request.method == 'POST':
        data = request.get_json()
        query = data.get('query')
        language = data.get('language', 'en')
    else:
        query = request.args.get('query')
        language = request.args.get('language', 'en')
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    # Optionally format prompt like OpenAI
    prompt = f"Explain the medical term '{query}' in simple, clear {language.upper()} for a layperson."
    explanation = call_grok3_api(prompt, language)
    # Log to DB
    grok_log = Grok3API(query=query, response=explanation)
    db.session.add(grok_log)
    db.session.commit()
    return jsonify({'explanation': explanation})

# --- xAI Grok API integration ---
def call_xai_grok_api(messages, model="grok-3"):
    """
    Call xAI Grok API for explainable AI.
    messages: List of dicts, e.g. [{"role": "user", "content": "Explain diabetes simply."}]
    model: "grok-3" or "grok-4"
    """
    api_key = os.environ.get("XAI_API_KEY", "your-xai-api-key")
    url = "https://api.x.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": messages
    }
    response = requests.post(url, headers=headers, json=payload, timeout=20)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

@app.route('/api/xai/explain', methods=['POST'])
def xai_explain():
    data = request.get_json()
    term = data.get('term')
    if not term:
        return jsonify({'error': 'No term provided'}), 400
    messages = [
        {"role": "system", "content": "You are a helpful medical dictionary assistant."},
        {"role": "user", "content": f"Explain the medical term '{term}' in simple terms."}
    ]
    try:
        explanation = call_xai_grok_api(messages)
        return jsonify({'explanation': explanation})
    except Exception as e:
        return jsonify({'error': str(e)}), 500