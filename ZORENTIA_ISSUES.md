# Zorentia issues found during Decision Tracker build

Keep this file as a technical record for the individual report / feedback.

## 1. Frontend generator failure

The frontend generator repeatedly failed while generating the next screen with:

```text
screen_composition_invalid
```

The message said that existing complete files were not changed, but generation could not continue. This happened inside the Zorentia frontend generation step before the generated frontend was run locally.

## 2. Same Decision concept split across multiple tables

Manual review of the generated backend package and schema showed multiple separate tables representing the same core concepts, for example several generated `decisions`, `options`, and pros/cons tables with different feature prefixes. Different backend features were therefore not consistently reading and writing the same data model.

## 3. Missing PyMySQL dependency

Generated modules such as `local_data_storage` and `create_decision` build connection strings using:

```text
mysql+pymysql://...
```

but the generated `requirements.txt` does not include `PyMySQL`. It includes `mysql-connector-python` instead.

## 4. Duplicate foreign-key constraint name

The generated `schema.sql` defines `fk_pros_cons_option` more than once for different generated tables. Importing the schema into MySQL produced:

```text
ERROR 1826 (HY000): Duplicate foreign key constraint name 'fk_pros_cons_option'
```

Because the duplicate name is visibly present in the generated schema, this is a concrete schema consistency issue. A fresh-database import can still be used as an additional clean verification step if needed for the report.

## 5. `db_engine` expected but not configured

Several generated features access:

```python
current_app.config['db_engine']
```

but the generated `backend/app.py` registers those blueprints without setting `app.config['db_engine']`. The package does contain a separate `get_engine()` helper, but it is not wired into those feature modules through the app configuration.

## What was changed in this fixed version

- Replaced the duplicated feature-specific tables with three shared tables: `decisions`, `decision_options`, and `pros_cons`.
- Used one SQLAlchemy engine for every API route.
- Removed the inconsistent generated authentication placeholders because login was not part of this small MVP.
- Used `mysql+mysqlconnector` when MySQL is selected, matching the installed dependency.
- Added unique foreign-key names and cascade relationships.
- Kept a SQLite fallback so the full application can be tested immediately without MySQL setup.
- Served frontend and backend from the same Flask app to simplify local testing and later domain deployment.
