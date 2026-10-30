# Shopity Marketplace

Shopity is a fully functional, multi-vendor e-commerce web application built using **Django** and styled with **Bootstrap 5**. It enables independent merchants to register store profiles, manage product inventories, and handle customer orders, while providing buyers with a seamless product catalog, shopping cart, and checkout experience.

---

## Key Features

* **Multi-Vendor Architecture**: Registered users can apply to open independent storefronts, manage inventory, and track fulfillment.
* **Product Catalog & Details**: Browse products by category, view detailed descriptions, pricing, and high-resolution images.
* **Shopping Cart & Checkout**: Full cart management (add, remove, subtotal calculation) and order placement workflow.
* **Content Moderation & Admin Tools**: Admin queue for reviewing vendor applications and managing flagged content.
* **Robust Test Suite**: Includes comprehensive model, view, and URL routing tests ensuring system stability.

---

## Tech Stack

* **Backend**: Python 3.x, Django 6.1
* **Database**: MariaDB / SQLite (Development)
* **Frontend**: HTML5, Bootstrap 5, CSS
* **Media Handling**: Pillow (for product/store image uploads)

---

## Getting Started / Local Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repository-url>
   cd shopity_projectproper
Create and activate a virtual environment:Bashpython -m venv .venv
# On Windows (PowerShell):
& .venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate
Install dependencies:Bashpip install -r requirements.txt
Run database migrations:   Bashpython manage.py makemigrations
python manage.py migrate
Create a superuser (for admin access):   Bashpython manage.py createsuperuser
Run the development server:   Bashpython manage.py runserver
Open your browser and navigate to http://127.0.0.1:8000/.Running TestsTo run the automated test suite and verify all views, models, and URL routing:Bashpython manage.py test