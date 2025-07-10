# Database Migrations with Alembic

This project use **Alembic** for database migrations.

---

## **Cheatsheet**

```bash
# Activate virtual environment
source .venv/bin/activate

# View migration history
alembic history

# Create a new migration (auto-generate from model changes)
alembic revision --autogenerate -m "Your migration message"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade fa749791dfc6
```