# DokanDar — Multi-Vendor Product Marketplace

DokanDar is a multi-vendor e-commerce marketplace. Independent vendors ("admins") list and manage their own products; customers browse, review, and buy across all vendors in one place; a super admin oversees the whole platform.

## Tech Stack

- **Backend:** Django 5.1 + Django REST Framework
- **Database:** Microsoft SQL Server (via `mssql-django` + ODBC Driver 17)
- **Auth:** JWT (`djangorestframework-simplejwt`)
- **Payments:** eSewa (ePay v2, sandbox/UAT credentials by default)
- **Frontend:** Vanilla HTML / CSS / JavaScript, served as Django templates + static files, talking to the API via `fetch`

## User Roles

| Role | Capabilities |
|---|---|
| **Super Admin** | Manage categories, approve/reject vendor registrations, view all orders and sales across the platform, view stats dashboard |
| **Admin (Vendor)** | Add/edit/delete their own products (with photos), view orders containing their products. Requires super admin approval before they can sell |
| **User (Customer)** | Browse/search/filter products, leave ratings & reviews (only on purchased products), manage cart, checkout via eSewa, view their own order history |

## Project Structure

```
config/           Django project settings, root URLconf, shared permission classes
users/            Custom User model (role + approval), auth endpoints (register/login/JWT)
catalog/          Category, Product, ProductImage, Review models + API
orders/           Cart, CartItem, Order, OrderItem models + API, dashboard stats
payments/         Payment model, eSewa signing/verification logic
frontend/
  templates/      One HTML page per screen (login, register, products, product detail,
                   cart, orders, vendor dashboard, super admin dashboard)
  static/css/     Shared stylesheet (design system: colors, cards, tables, toasts, dark mode)
  static/js/      One JS file per page + shared api.js (fetch wrapper, auth/token
                   handling, toast notifications)
media/            Uploaded product images (gitignored)
```

## Setup

1. **Python & dependencies**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. **Database** — connection settings live in `.env` (not committed). Required keys:
   ```
   DB_NAME=...
   DB_HOST=...
   DB_USER=...
   DB_PASSWORD=...
   DB_TRUSTED_CONNECTION=yes|no
   DB_DRIVER=ODBC Driver 17 for SQL Server
   ```
   Then apply migrations:
   ```powershell
   python manage.py migrate
   ```

3. **eSewa** — sandbox credentials default in `.env` (`ESEWA_MERCHANT_CODE=EPAYTEST`, etc.), pointing at eSewa's UAT environment. Swap for real merchant credentials before going live.

4. **Run**
   ```powershell
   python manage.py runserver 127.0.0.1:8000
   ```
   Open http://127.0.0.1:8000/ — this serves the product grid directly as the home page.

5. **First super admin** — no self-registration path exists for this role; create one via `python manage.py shell` (set `role='super_admin'`, `is_approved=True`, `is_staff=True`, `is_superuser=True`) or `createsuperuser` + manually setting `role`.

## Key API Endpoints

```
POST   /api/auth/register/              Register (role: user | admin)
POST   /api/auth/login/                 JWT login
GET    /api/auth/vendors/pending/       Super admin: list pending vendor approvals
POST   /api/auth/vendors/<id>/approve/  Super admin: approve a vendor

GET    /api/products/?category=&search=&min_price=&max_price=&min_rating=&sort=
POST   /api/products/                   Vendor (approved) or super admin only
POST   /api/products/<id>/reviews/      Only for purchased products

GET    /api/cart/ | POST /api/cart/add/ | PATCH|DELETE /api/cart/items/<id>/
POST   /api/orders/checkout/            Creates order, returns signed eSewa form fields
GET    /api/orders/mine/ | /vendor/ | /all/
GET    /api/dashboard/stats/            Super admin: totals + sales by vendor

GET    /api/payment/esewa/success/      eSewa redirect target; verifies + marks order paid
```

## Notable Design Decisions

- **Vendor approval:** self-registered vendor accounts start `is_approved=False` and cannot log in until a super admin approves them.
- **Reviews require purchase:** enforced server-side by checking for a paid/shipped/delivered `OrderItem` before allowing a review.
- **`GET /api/products/`** filters to `is_active=True` for public browsing, but a vendor (or super admin) requesting their *own* products via `?vendor=<their id>` sees inactive ones too — needed so vendors can manage deactivated listings from their own dashboard.
- **Toast notifications:** all transient success/error feedback across the frontend goes through a shared `showToast()` helper (`api.js`) rather than inline alert boxes; persistent state banners (e.g. "vendor pending approval") remain inline since they shouldn't auto-dismiss.

## Known Gaps

- No automated test suite — functionality has been verified via live manual requests during development.
- No password reset flow.
- eSewa integration currently targets the sandbox/UAT endpoint only.
