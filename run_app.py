#!/usr/bin/env python3
"""
Simple script to run the Healthcare Terminology Dictionary
This script will:
1. Check if the database exists and initialize it if needed
2. Start the Flask application
"""

import os
import sys
from app import app, db
from models import Category, Term



def initialize_database():
    """Initialize database with sample data if it's empty"""
    print("Checking database...")
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
        
        # Check if we have any data
        if Category.query.count() == 0:
            print("Database is empty. Initializing with sample data...")
            try:
                # Run the initialization script
                import sys
                import os
                sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))
                from init_db import init_db
                init_db()
                print("Database initialized successfully!")
            except Exception as e:
                print(f"Error initializing database: {e}")
                return False
        else:
            print("Database already contains data.")
    
    return True

def main():
    """Main function to run the application"""
    print("Healthcare Terminology Dictionary - Starting...")
    print("=" * 50)
    
    # Initialize database
    if not initialize_database():
        print("Failed to initialize database. Exiting.")
        sys.exit(1)
    
    # Start the application
    print("\nStarting web server...")
    print("The application will be available at: http://localhost:5000/admin/auth")
    print("Press Ctrl+C to stop the server")
    print("=" * 50)
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=True)
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    except Exception as e:
        print(f"Error starting server: {e}")

if __name__ == "__main__":
    main()