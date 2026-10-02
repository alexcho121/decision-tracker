# Decision Tracker - Clean Fixed Version

This package is a small working replacement for the inconsistent Zorentia-generated database/backend and the frontend screen that failed to generate.

## What is included

- `frontend/` - create decisions, view history, add/remove options, add/remove pros and cons, choose a final option.
- `backend/` - one Flask API using one consistent database model.
- `database/schema.sql` - clean MySQL schema with unique foreign-key names.
- `tests/` - basic end-to-end API tests using SQLite.
- `ZORENTIA_ISSUES.md` - issues found in the generated files and frontend generator.

## Fastest local run (recommended first)

From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m backend.app
```

Then open:

```text
http://127.0.0.1:5000
```

If `DATABASE_URL` is not set, the app automatically creates a local SQLite file called `decision_tracker.db`. This is the quickest way to test the complete frontend/backend flow before deployment.

## Use MySQL instead

Create the database once:

```bash
mysql -u root
```

```sql
CREATE DATABASE app_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit;
```

Copy the environment example:

```bash
cp .env.example .env
```

Set `.env` to:

```text
DATABASE_URL=mysql+mysqlconnector://root@localhost:3306/app_db
```

You can either let the backend create the three tables automatically when it starts, or import the included clean schema manually:

```bash
mysql -u root app_db < database/schema.sql
```

Then run:

```bash
python -m backend.app
```

## Run tests

```bash
pytest -q
```

## Production entry point

```bash
gunicorn -w 2 -b 0.0.0.0:8000 backend.wsgi:app
```

The frontend is served by the same Flask app, so there is no separate CORS configuration and no hard-coded API hostname. This makes it easier to put the whole app behind one domain later.

## Main API

- `GET /health`
- `POST /api/decisions`
- `GET /api/decisions`
- `GET /api/decisions/<id>`
- `DELETE /api/decisions/<id>`
- `POST /api/decisions/<id>/options`
- `DELETE /api/options/<id>`
- `POST /api/options/<id>/pros-cons`
- `DELETE /api/pros-cons/<id>`
- `POST /api/decisions/<id>/select`

## Important

The original Zorentia package should be kept separately as evidence. This folder is the cleaned working version, not a claim that Zorentia generated these fixes automatically.
