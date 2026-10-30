# Sticky Notes Application

A full-stack web application built with Django that allows users to create, view, update, and delete sticky notes efficiently.

## Features

* **Full CRUD Operations:** Create, view, update, and safely delete sticky notes with dedicated confirmation steps.
* **Color Categories:** Select from customizable color themes (Yellow, Blue, Green, Pink) with server-side form validation.
* **Smart Pinning & Ordering Rule:** Pin important notes to automatically sort them above all unpinned notes in the list view.

## Project Structure

```text
stickynotes_app/
│
├── stickynotes_app/      # Inner project configuration folder (settings.py, urls.py)
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── notes/                # Main Django application folder
│   ├── migrations/
│   ├── templates/
│   ├── forms.py
│   ├── models.py
│   ├── tests.py          # Application unit tests
│   ├── urls.py
│   └── views.py
│
├── design_diagrams/      # Project design documentation and diagrams
│   ├── Use_Case.png
│   ├── Sequence.png
│   └── Class.png
│
├── manage.py
└── README.md

Design Diagrams
The project documentation includes the following diagrams located in the design_diagrams/ folder:

Use Case Diagram

Sequence Diagram

Class Diagram

Getting Started
Prerequisites
Python 3.10+

Virtual environment (venv)

Installation & Setup
Clone the repository and navigate into the project root:

cd stickynotes_app

Create and activate a virtual environment:

python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

Install dependencies:

pip install -r requirements.txt

Run database migrations:

python manage.py makemigrations
python manage.py migrate

Run the development server:

python manage.py runserver

Running Tests
To run the application unit test suite (covering views, forms, color validation, and the pinned-ordering rule):

python manage.py test