# Finance Dashboard Backend

A role-based finance data management API built with **Django** and **Django REST Framework**.

---

## Tech Stack

| Layer | Choice | Reason |
|---|---|---|
| Language | Python 3.12 | Assignment requirement |
| Framework | Django 4.2 + DRF 3.15 | Batteries-included, mature ecosystem |
| Auth | JWT via `djangorestframework-simplejwt` | Stateless, works well with SPAs |
| Database | SQLite (dev) | Zero-config local setup; swap to PostgreSQL for prod |
| Filtering | `django-filter` | Declarative, composable filter sets |
| API Docs | `drf-spectacular` (Swagger UI) | Auto-generated from code, zero drift |

---

## Project Structure

```
finance_backend/
├── finance_backend/          # Django project config
│   ├── settings.py
│   └── urls.py
├── apps/
│   ├── core/                 # Shared: permissions, pagination, exception handler
│   ├── users/                # User model, auth, role management
│   ├── records/              # Financial records CRUD
│   └── dashboard/            # Summary and analytics APIs
├── tests/                    # Test suite
├── scripts/
│   └── seed.py               # Loads sample data
├── manage.py
└── requirements.txt
```

---

## Setup

```bash
# 1. Create and activate virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run migrations
python manage.py migrate

# 4. (Optional) Load seed data
python manage.py seed 

# 5. Start the server
python manage.py runserver
```

API docs available at: **http://localhost:8000/api/docs/**

---

## Roles

| Role | Permissions |
|---|---|
| `viewer` | Read financial records, view overview dashboard |
| `analyst` | Read records + all dashboard analytics |
| `admin` | Full CRUD on records, manage users, all dashboard |

New registrations default to **viewer**.

---

## API Endpoints

### Auth — `/api/auth/`

| Method | Path | Description | Auth |
|---|---|---|---|
| POST | `/register/` | Create account (viewer) | Public |
| POST | `/login/` | Get access + refresh tokens | Public |
| POST | `/refresh/` | Refresh access token | Refresh token |
| POST | `/logout/` | Blacklist refresh token | Bearer |

### Users — `/api/users/`

| Method | Path | Description | Role |
|---|---|---|---|
| GET | `/me/` | Own profile | Any |
| POST | `/me/change-password/` | Change own password | Any |
| GET | `/` | List all users | Admin |
| POST | `/` | Create user with role | Admin |
| GET | `/<id>/` | Get user detail | Admin |
| PATCH | `/<id>/` | Update role / status | Admin |
| DELETE | `/<id>/` | Delete user | Admin |
| POST | `/<id>/deactivate/` | Deactivate account | Admin |
| POST | `/<id>/activate/` | Reactivate account | Admin |

**Filters:** `?role=viewer` `?is_active=true` `?search=john`

### Records — `/api/records/`

| Method | Path | Description | Role |
|---|---|---|---|
| GET | `/` | List records (paginated) | All |
| POST | `/` | Create record | Admin |
| POST | `/bulk/` | Bulk create records | Admin |
| GET | `/<id>/` | Get record detail | All |
| PATCH | `/<id>/` | Update record | Admin |
| DELETE | `/<id>/` | Soft delete | Admin |
| DELETE | `/<id>/?hard=true` | Hard delete | Admin |
| POST | `/<id>/restore/` | Restore soft-deleted | Admin |

**Filters:** `?type=income` `?category=salary` `?date_from=2024-01-01` `?date_to=2024-12-31` `?amount_min=100` `?amount_max=5000`  
**Search:** `?search=freelance`  
**Ordering:** `?ordering=-date` `?ordering=amount`

**Record fields:**

```json
{
  "amount":      "1500.00",
  "type":        "income",
  "category":    "salary",
  "date":        "2024-06-15",
  "description": "June salary"
}
```

**Types:** `income` | `expense`  
**Categories:** `salary` `investment` `freelance` `food` `rent` `utilities` `healthcare` `transport` `education` `entertainment` `tax` `other`

### Dashboard — `/api/dashboard/`

| Method | Path | Description | Role |
|---|---|---|---|
| GET | `/overview/` | Totals: income, expense, net | All |
| GET | `/categories/` | Per-category breakdown | Analyst+ |
| GET | `/categories/top/` | Top N categories | Analyst+ |
| GET | `/trends/monthly/` | Monthly income vs expense | Analyst+ |
| GET | `/trends/weekly/` | Weekly income vs expense | Analyst+ |
| GET | `/activity/` | Recent records | Analyst+ |
| GET | `/spending/daily/` | Daily expense totals | Analyst+ |

**Query params for overview:** `?date_from=` `?date_to=`  
**Query params for trends:** `?months=6` / `?weeks=8`  
**Query params for top categories:** `?type=expense&limit=5`

---

## Authentication Flow

```
POST /api/auth/login/
  { "username": "admin", "password": "Admin@1234" }

→ { "access": "<JWT>", "refresh": "<JWT>" }

# Use in subsequent requests:
Authorization: Bearer <access token>
```

---

## Error Response Format

All errors follow a consistent envelope:

```json
{
  "error": true,
  "message": "Human-readable description",
  "details": { "field": ["Validation message"] }
}
```

---

## Running Tests

```bash
python manage.py test tests
```

Test coverage:
- Auth (register, login, token)
- Records CRUD and access control per role
- Record filtering
- Soft delete / restore
- Dashboard endpoint access control
- Dashboard aggregate correctness

---

## Design Decisions & Assumptions

1. **Soft delete by default** — `DELETE /records/<id>/` marks `is_deleted=True` and preserves data for auditing. Pass `?hard=true` for permanent removal.

2. **Service layer for analytics** — `apps/dashboard/services.py` holds all aggregation logic. Views stay thin; the service layer is independently testable.

3. **Custom exception handler** — All error responses use the same `{ error, message, details }` shape, making frontend integration predictable.

4. **UUID primary keys on records** — Avoids sequential ID enumeration on financial data.

5. **Viewer sees overview only** — Category breakdowns and trends are analyst-level insights, not raw reads. Viewers can see the top-level summary but not drill-down analytics.

6. **Token blacklisting on logout** — Refresh tokens are blacklisted so logout is real, not just client-side token removal.

7. **Pagination on all lists** — Default 20 items per page; override with `?page_size=50` (max 100).
