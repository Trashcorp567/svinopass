import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.config import settings
from app.db.database import SessionLocal
from app.services.watch_service import run_due_watch_checks


def main() -> int:
    db = SessionLocal()
    try:
        stats = run_due_watch_checks(db, min_interval_days=settings.watch_check_interval_days)
        print(stats)
        return 0 if stats["errors"] == 0 else 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
