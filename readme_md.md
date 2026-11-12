# Shopity Marketplace

Shopity is a modular, multi-vendor e-commerce platform built with Django. It supports role-based access for buyers, vendors, and administrators, includes full product management and cart workflows, provides RESTful API endpoints, and features an integrated live Reddit feed.

## Features

- **Multi-Vendor Store Management:** Vendors can create stores, manage product catalogs, and update customer order fulfillment statuses.
- **Role-Based Views & Dashboards:** Distinct interfaces and permissions for Buyers, Vendors, and Administrators.
- **Live Reddit API Integration:** Displays top posts from community subreddits with full error handling and fallback mock data.
- **RESTful API:** Integrated API endpoints for authentication, product catalogs, shopping cart operations, store management, and order checkouts.
- **Global Context Processors:** Automated detection and template injection of vendor store status.

## Project Structure

```text
shopity_projectproperpart2/
│
├── marketplace/               # Core marketplace app
│   ├── templates/
│   │   └── marketplace/       # App HTML templates (base.html, reddit_feed.html, etc.)
│   ├── models.py              # Models (Store, Product, OrderItem, etc.)
│   ├── views.py               # Core web views & Reddit integration
│   ├── views_vendor.py        # Vendor catalog & order processing logic
│   ├── views_admin.py         # Administrative & moderation views
│   ├── views_api.py           # REST API endpoints
│   └── urls.py                # App routing configuration
│
├── shopity_projectproper/     # Project configuration directory
│   ├── settings.py            # Global settings & context processors
│   └── urls.py                # Root URL routing
│
├── manage.py                  # Django management script
├── README.md                  # Project documentation
└── requirements.txt           # Project dependencies
```

## Getting Started

### Prerequisites

- Python 3.10+
- `pip` package manager

### Installation & Setup

1. **Clone or download the repository:**
   ```bash
   cd shopity_projectproperpart2
   ```

2. **Create and activate a virtual environment:**
   - **Windows:**
     ```bash
     python -m venv .venv
     .venv\Scripts\activate
     ```
   - **macOS / Linux:**
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply database migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser (optional):**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

7. Open your browser and navigate to `http://127.0.0.1:8000/`.

## Important Endpoints

- **Home Page:** `http://127.0.0.1:8000/`
- **Product Catalog:** `http://127.0.0.1:8000/catalog/`
- **Reddit Feed:** `http://127.0.0.1:8000/reddit/`
- **Login:** `http://127.0.0.1:8000/login/`
- **Vendor Dashboard:** `http://127.0.0.1:8000/vendor/dashboard/`
- **Django Admin:** `http://127.0.0.1:8000/admin/`