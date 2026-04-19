"""Simple CSV importer for seeding the database.
Expected CSV headers: title,author,genre,published_year,average_rating,description
Usage: python scripts/import_books.py sample_books.csv
"""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.database import SessionLocal, Base, engine
from app.models import Book

Base.metadata.create_all(bind=engine)

if len(sys.argv) < 2:
    raise SystemExit("Usage: python scripts/import_books.py <csv_path>")

csv_path = Path(sys.argv[1])
if not csv_path.exists():
    raise SystemExit(f"File not found: {csv_path}")

db = SessionLocal()
count = 0
with csv_path.open("r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        book = Book(
            title=row.get("title", "Untitled"),
            author=row.get("author", "Unknown"),
            genre=row.get("genre", "General"),
            published_year=int(row["published_year"]) if row.get("published_year") else None,
            average_rating=float(row["average_rating"]) if row.get("average_rating") else 0.0,
            description=row.get("description"),
        )
        db.add(book)
        count += 1

db.commit()
db.close()
print(f"Imported {count} books from {csv_path}")
