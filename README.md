# 🛒 Ecomm API

A production-ready Django REST API for e-commerce, built with Cookiecutter Django, Docker, PostgreSQL, and Celery.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | Django 6 + Django REST Framework |
| Database | PostgreSQL 18 |
| Auth | django-allauth (JWT-ready) |
| Background Tasks | Celery + Redis |
| Containerization | Docker + Docker Compose |
| Project Structure | Cookiecutter Django |
| API Docs | drf-spectacular (Swagger) |

---

## Features

- **Products** — list and retrieve products
- **Cart** — add items, view cart, remove items
- **Orders** — place orders from cart, view order history
- **Auth** — register, login, email verification via allauth
- **Background Tasks** — order confirmation emails via Celery
- **Admin Panel** — manage all models via Django admin

---

## Project Structure

```
ecomm_api/
├── config/
│   ├── settings/
│   │   ├── base.py          # shared settings
│   │   ├── local.py         # dev settings
│   │   └── production.py    # production settings
│   ├── urls.py
│   └── wsgi.py
├── ecomm_api/
│   ├── store/               # main app
│   │   ├── models.py        # Product, Cart, CartItem, Order, OrderItem
│   │   ├── serializers.py   # DRF serializers
│   │   ├── views.py         # API views
│   │   ├── urls.py          # URL routing
│   │   ├── tasks.py         # Celery background tasks
│   │   └── admin.py         # Admin panel config
│   ├── users/               # pre-built auth app
│   └── celery_app.py        # Celery configuration
├── .envs/
│   └── .local/
│       ├── .django          # Django env vars
│       └── .postgres        # Database env vars
├── docker-compose.local.yml
└── manage.py
```

---

## Getting Started

### Prerequisites

- Docker Desktop (running)
- Python 3.14+

### 1. Clone the repo

```bash
git clone <your-repo-url>
cd ecomm_api
```

### 2. Start all services

```bash
docker-compose -f docker-compose.local.yml up --build
```

This spins up 4 containers:
- `django` — the API on port 8000
- `postgres` — the database on port 5432
- `redis` — message broker on port 6379
- `celery_worker` — background task worker

### 3. Run migrations

In a second terminal:

```bash
docker-compose -f docker-compose.local.yml run --rm django python manage.py migrate
```

### 4. Create a superuser

```bash
docker-compose -f docker-compose.local.yml run --rm django python manage.py createsuperuser
```

### 5. Visit the app

| URL | Description |
|---|---|
| `http://localhost:8000/api/` | Browsable REST API |
| `http://localhost:8000/admin/` | Django admin panel |
| `http://localhost:8000/api/docs/` | Swagger API documentation |

---

## API Endpoints

### Auth
```
POST   /accounts/signup/          register a new user
POST   /accounts/login/           login
POST   /accounts/logout/          logout
```

### Products
```
GET    /api/products/             list all products
GET    /api/products/<id>/        get a single product
```

### Cart
```
GET    /api/cart/                 view your cart
POST   /api/cart/items/           add item to cart
DELETE /api/cart/items/<id>/      remove item from cart
```

### Orders
```
GET    /api/orders/               list your orders
POST   /api/orders/               place order from cart
GET    /api/orders/<id>/          get a single order
```

---

## Environment Variables

All secrets live in `.envs/.local/`. Never commit these to Git.

**`.envs/.local/.django`**
```
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost
REDIS_URL=redis://redis:6379/0
```

**`.envs/.local/.postgres`**
```
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=ecomm_api
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
```

---

## Useful Commands

```bash
# run all services
docker-compose -f docker-compose.local.yml up

# stop all services
docker-compose -f docker-compose.local.yml down

# run migrations
docker-compose -f docker-compose.local.yml run --rm django python manage.py migrate

# make migrations after model changes
docker-compose -f docker-compose.local.yml run --rm django python manage.py makemigrations

# open Django shell
docker-compose -f docker-compose.local.yml run --rm django python manage.py shell

# run tests
docker-compose -f docker-compose.local.yml run --rm django pytest

# view logs
docker-compose -f docker-compose.local.yml logs

# rebuild from scratch (after dependency changes)
docker-compose -f docker-compose.local.yml build --no-cache
```

---

## Data Models

```
Product
  - name, description, price, stock

Cart (one per user)
  - user (OneToOne)
  - get_total()

CartItem
  - cart (FK), product (FK), quantity
  - get_subtotal()

Order
  - user (FK), total, status (pending/confirmed/shipped/delivered/cancelled)

OrderItem
  - order (FK), product (FK), quantity, price (snapshot at order time)
```

---

## Background Tasks (Celery)

When an order is placed, an order confirmation email is sent asynchronously:

```python
send_order_confirmation.delay(
    order_id=order.id,
    user_email=request.user.email,
    total=order.total
)
```

The Celery worker picks this up from Redis and processes it in the background — the user gets an instant API response without waiting for the email to send.

In development, emails are printed to the Django console log.

---

## What I Learned Building This

- Django MTV architecture and the URL → View → Model → Response flow
- Django ORM — models, relationships, querysets
- Django REST Framework — serializers, APIViews, permissions
- Cookiecutter Django — split settings, production-ready project structure
- Docker Compose — multi-container setup with service dependencies
- Celery + Redis — background task processing
- django-allauth — production-grade authentication with email verification

---

## Next Steps

- [ ] Product filtering and search (`django-filter`)
- [ ] Pagination for product and order lists
- [ ] Stock management on order placement
- [ ] Order cancellation endpoint
- [ ] Write tests with `pytest-django`
- [ ] Deploy to production

---

## License

MIT