Shopity Marketplace
Shopity is a modular, multi-vendor e-commerce platform built with Django. It supports role-based access for buyers, vendors, and administrators, and includes full product management, a shopping cart, and email invoice checkout workflows.
Features
Multi-Vendor Store Management: Vendors can create stores, manage product catalogs, and update customer order fulfillment and tracking statuses.
Role-Based Views & Dashboards: Distinct interfaces and permissions for Buyers, Vendors, and Administrators.
Session Shopping Cart & Checkout: Full cart management with automated order creation and email invoice generation.
Live Reddit Integration (Part 2): Displays top posts from community subreddits with error handling.
Global Context Processors: Automated detection and template injection of vendor store status and cart state.
Project Structure
shopity_projectproper/
├── functions/                 # External integration helpers for Part 2 (e.g., Reddit feed)
│   └── reddit.py
├── marketplace/               # Core marketplace app
│   ├── templates/
│   │   └── marketplace/       # App HTML templates (base.html, home.html, login.html, etc.)
│   ├── cart.py                # Session-based shopping cart logic
│   ├── context_processors.py  # Cart context processor
│   ├── forms.py               # Registration, store, product, review, and tracking forms
│   ├── models.py              # Models (Store, Product, Order, OrderItem, ProductReview, ResetToken)
│   ├── views.py               # Core web views & Reddit integration
│   ├── views_vendor.py        # Vendor catalog & order processing logic
│   ├── views_admin.py         # Administrative & moderation views
│   └── urls.py                # App routing configuration
├── shopity_projectproper/     # Project configuration directory
│   ├── settings.py            # Global settings, MariaDB/MySQL config & context processors
│   └── urls.py                # Root URL routing
├── manage.py                  # Django management script
├── README.md                  # Project documentation
└── requirements.txt           # Project dependencies
Getting Started
Prerequisites
Python 3.10+
MariaDB or MySQL Server (running locally on port 3306)
pip package manager
Git
Installation & Setup
Clone the repository and enter the project directory:

git clone https://github.com/faraazmahomed/shopity_projectproper.git
cd shopity_projectproper

(Note: If you uploaded the repository under a slightly different repository slug on GitHub, update the URL above to match your exact live repository link.)

Create and activate a virtual environment:

Windows (PowerShell):

python -m venv .venv
.venv\Scripts\Activate.ps1

macOS / Linux:

python3 -m venv .venv
source .venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Configure the MariaDB / MySQL database and user:

Log in to your MariaDB or MySQL shell as root:

mysql -u root -p

Run the following SQL commands to create the database and user expected by shopity_projectproper/settings.py:

CREATE DATABASE shopity_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'shopity_user'@'127.0.0.1' IDENTIFIED BY 'secure_password123';
GRANT ALL PRIVILEGES ON shopity_db.* TO 'shopity_user'@'127.0.0.1';
FLUSH PRIVILEGES;
EXIT;

(Optional: If you prefer to use your own database name, username, or password, update the DATABASES dictionary in shopity_projectproper/settings.py accordingly.)

Apply database migrations:

python manage.py makemigrations
python manage.py migrate

Create a superuser (optional):

python manage.py createsuperuser

Run the development server:

python manage.py runserver

Open your browser and navigate to http://127.0.0.1:8000/.
Important Endpoints
Home Page: http://127.0.0.1:8000/
Product Catalog: http://127.0.0.1:8000/catalog/
Login: http://127.0.0.1:8000/login/
Register: http://127.0.0.1:8000/register/
Vendor Dashboard: http://127.0.0.1:8000/vendor/dashboard/
Buyer Dashboard: http://127.0.0.1:8000/buyer/dashboard/
Django Admin: http://127.0.0.1:8000/admin/
