from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

app.config['SECRET_KEY'] = 'ds7f6sd8f76sd87f6sd87f6s8d7f6'  # Set a proper secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dictionary.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

import routes

if __name__ == "__main__":
    app.run(debug=True)
