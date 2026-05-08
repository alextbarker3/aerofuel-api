from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.db.database import SessionLocal
from app.db.seed import seed_database
from app.ml.train import train_models


def main():
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    metadata = train_models()
    print("AeroFuel API bootstrap complete")
    print(metadata)


if __name__ == "__main__":
    main()
