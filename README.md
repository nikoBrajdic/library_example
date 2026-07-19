# Django-Wagtail Book Repository

API-first book repository backed by Django and Wagtail CMS. Administrators manage catalog content in Wagtail; approved authors authenticate with JWT and submit works through the API. Authors never get Wagtail admin access.

## Assumptions


| Decision        | Choice                                                                        |
| --------------- | ----------------------------------------------------------------------------- |
| Content model   | Custom Django models registered as Wagtail **snippets** (not a page tree)     |
| Book lifecycle  | `draft` → `pending_review` (author submit) → `published` / `rejected` (admin) |
| Author auth     | JWT (`simplejwt`); Wagtail uses session auth for CMS staff                    |
| Author identity | `AuthorProfile` 1:1 with Django `User`; `is_approved` gates submit API        |
| Public API      | Unauthenticated read of **published** books only                              |
| Author API      | Authenticated + approved; create/list/update own non-published works          |
| Search / filter | Title search (`q`), genre slug, author id; page-number pagination             |
| Local run       | Docker Compose + Postgres (SQLite works for local/dev without Docker)         |




## Quick start (Docker)

```bash
cp .env.example .env
docker compose up --build
```

Then:

- API docs: [http://localhost:8000/api/docs/](http://localhost:8000/api/docs/)
- Wagtail admin: [http://localhost:8000/admin/](http://localhost:8000/admin/) (`admin` / `adminpass`)
- Author API user: `niko` / `authorpass`

Demo seed runs automatically when `RUN_SEED=true` (default in Compose).

## Local development (without Docker)

```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Uses SQLite when `DATABASE_URL` is unset.

## API map



### Auth

```bash
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"niko","password":"authorpass"}'
```

Refresh: `POST /api/auth/token/refresh/` with `{"refresh":"<token>"}`.

### Public

```bash
# List published books (optional: ?q=clean&genre=computing&author=1)
curl http://localhost:8000/api/books/

# Book detail
curl http://localhost:8000/api/books/clean-code/

# Authors
curl http://localhost:8000/api/authors/
```



### Author (JWT required)

```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"niko","password":"authorpass"}' | python -c "import sys,json; print(json.load(sys.stdin)['access'])")

# Submit a work → pending_review
curl -X POST http://localhost:8000/api/author/books/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"My New Manuscript","synopsis":"A short synopsis","genre_ids":[1]}'

# List / patch own submissions
curl http://localhost:8000/api/author/books/ -H "Authorization: Bearer $TOKEN"
curl -X PATCH http://localhost:8000/api/author/books/1/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"synopsis":"Updated synopsis"}'
```

Published books cannot be edited by authors. Admins change status (and other fields) in Wagtail snippets.

## Project layout

```
config/     Django/Wagtail settings and URLs
home/       Minimal Wagtail homepage (CMS bootstrap)
catalog/    Book/Genre models, APIs, seed command
users/      AuthorProfile + auto-create signal
```



## Tests

```bash
python manage.py test catalog
```



## Notes for reviewers

- Authors are created with `is_staff=False`; Wagtail admin rejects non-staff users.
- New non-staff users get an unapproved `AuthorProfile` via signal; an admin must tick **Approved** in Wagtail before API submits succeed.
- OpenAPI schema: `/api/schema/` and Swagger UI at `/api/docs/`.

