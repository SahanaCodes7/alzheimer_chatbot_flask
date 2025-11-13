# Alzheimer Chatbot Flask

## Overview

A web-based chatbot application built with Flask, focused on aiding Alzheimer’s patients, caretakers, and doctors through personalized interactions, appointment management, and explainable AI.

## Project Structure

alzheimer_chatbot_flask/
│
├── app.py # Main Flask app, runs server and ties routes together
├── adaptive_flow.py # Adaptive conversational flow controller
├── appointment_routes.py # Routes & logic for appointments (CRUD)
├── auth_routes.py # Authentication routes (login, register)
├── config.py # Configuration settings (e.g., Flask, database)
├── crypto_utils.py # Cryptography helpers/utilities
├── doctor_routes.py # Doctor-specific routes and features
├── models.py # Data models / ORM classes
├── nlp_inference.py # NLP processing, chatbot inference
├── patient_routes.py # Patient-specific routes and features
├── requirements.txt # Required Python packages
├── test.py # Test script(s)
├── vercel.json # Configuration for Vercel deployment
├── xai.py # Explainable AI functions
│
├── pycache/ # Python bytecode cache (auto-generated)
├── instance/ # Instance configs, e.g., database.sqlite
├── static/ # Static files (CSS, images)
├── templates/ # HTML templates (login, chat interface, etc.)
└── .gitignore # Files/folders to exclude from version control


## Getting Started

### 1. Clone the repository
git clone https://github.com/SahanaCodes7/alzheimer_chatbot_flask.git
cd alzheimer_chatbot_flask


### 2. Install dependencies

Create a virtual environment (recommended):

python -m venv venv
source venv/bin/activate # macOS/Linux
venv\Scripts\activate # Windows


Install Python packages:

pip install -r requirements.txt


### 3. Configure environment

- Set up configuration in `instance/` or `config.py`.
- Ensure your database (e.g., SQLite) is initialized.

### 4. Run the application
python app.py


- Then open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

## Features

- **Chatbot**: Engage with the Alzheimer chatbot for FAQs, reminders, and help.
- **User Authentication**: Patients and doctors can log in securely.
- **Appointments**: Schedule/manage appointments (CRUD operations).
- **Explainable AI**: Get explanations for chatbot predictions (XAI).
- **Doctors & Patients Support**: Dedicated routes for each role.
- **NLP Inference**: Personalized, context-aware answers using NLP.

## Folder Details

- **static/**: CSS, JS, image assets.
- **templates/**: HTML pages.
- **instance/**: Local configuration/database files.
- **test.py**: Testing utilities.



## Contact

For issues, suggestions, or questions, open a GitHub Issue or contact [SahanaCodes7](https://github.com/SahanaCodes7).



