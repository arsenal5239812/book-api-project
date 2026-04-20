"""Import books from either a simple local CSV or the public goodbooks-10k dataset.

Examples:
  python scripts/import_books.py scripts/sample_books.csv
  python scripts/import_books.py --goodbooks-dir scripts/goodbooks-10k --limit 2000
  python scripts/import_books.py --download-goodbooks --goodbooks-dir scripts/goodbooks-10k --limit 1000
"""

import argparse
import csv
import sys
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Tuple
from urllib.error import URLError

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.database import Base, SessionLocal, engine
from app.models import Book


GOODBOOKS_FILES = {
    "books.csv": "https://raw.githubusercontent.com/zygmuntz/goodbooks-10k/master/books.csv",
    "tags.csv": "https://raw.githubusercontent.com/zygmuntz/goodbooks-10k/master/tags.csv",
    "book_tags.csv": "https://raw.githubusercontent.com/zygmuntz/goodbooks-10k/master/book_tags.csv",
}

GENRE_KEYWORDS = {
    "Fantasy": {"fantasy", "epic-fantasy", "urban-fantasy", "magic"},
    "Science Fiction": {"science-fiction", "sci-fi", "dystopia", "post-apocalyptic"},
    "Romance": {"romance", "love", "chick-lit", "contemporary-romance"},
    "Mystery": {"mystery", "crime", "detective", "suspense"},
    "Thriller": {"thriller", "psychological-thriller", "action", "adventure"},
    "Historical": {"historical-fiction", "history", "historical", "world-war-ii"},
    "Young Adult": {"young-adult", "ya", "teen", "coming-of-age"},
    "Classics": {"classics", "classic-literature", "literature"},
    "Nonfiction": {"non-fiction", "nonfiction", "memoir", "biography", "self-help"},
    "Horror": {"horror", "paranormal", "ghosts"},
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import books into the coursework database.")
    parser.add_argument("csv_path", nargs="?", help="Simple CSV with title,author,genre,published_year,average_rating,description")
    parser.add_argument("--goodbooks-dir", default="scripts/goodbooks-10k", help="Directory containing goodbooks-10k CSV files")
    parser.add_argument("--download-goodbooks", action="store_true", help="Download required goodbooks-10k files before importing")
    parser.add_argument("--limit", type=int, default=1000, help="Maximum number of goodbooks rows to import")
    parser.add_argument("--min-ratings-count", type=int, default=5000, help="Minimum ratings_count for goodbooks imports")
    parser.add_argument("--reset", action="store_true", help="Delete existing books before importing")
    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> None:
    if args.limit < 1:
        raise SystemExit("--limit must be at least 1")
    if args.min_ratings_count < 0:
        raise SystemExit("--min-ratings-count cannot be negative")


def ensure_schema() -> None:
    Base.metadata.create_all(bind=engine)


def maybe_reset_books(db) -> None:
    db.query(Book).delete()
    db.commit()


def normalize_tag(tag_name: str) -> str:
    return tag_name.strip().lower().replace(" ", "-")


def infer_genre(tag_scores: dict[str, int]) -> str:
    best_genre = "General"
    best_score = 0
    for genre, keywords in GENRE_KEYWORDS.items():
        score = sum(count for tag, count in tag_scores.items() if tag in keywords)
        if score > best_score:
            best_genre = genre
            best_score = score
    return best_genre


def download_goodbooks_files(target_dir: Path) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    for filename, url in GOODBOOKS_FILES.items():
        destination = target_dir / filename
        if destination.exists():
            print(f"Using existing {filename} from {target_dir}")
            continue
        print(f"Downloading {filename}...")
        try:
            urllib.request.urlretrieve(url, destination)
        except URLError as exc:
            raise SystemExit(
                f"Failed to download {filename} from {url}. Check your internet connection and try again."
            ) from exc


def load_tag_lookup(tags_path: Path) -> dict[str, str]:
    with tags_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {row["tag_id"]: normalize_tag(row["tag_name"]) for row in reader}


def load_book_genres(book_tags_path: Path, tag_lookup: dict[str, str]) -> dict[str, str]:
    scores_by_book: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    with book_tags_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tag_name = tag_lookup.get(row["tag_id"])
            if not tag_name:
                continue
            scores_by_book[row["goodreads_book_id"]][tag_name] += int(row["count"])
    return {book_id: infer_genre(tag_scores) for book_id, tag_scores in scores_by_book.items()}


def import_simple_csv(db, csv_path: Path) -> Tuple[int, int]:
    imported = 0
    skipped = 0
    seen_keys = {
        (title, author, source)
        for title, author, source in db.query(Book.title, Book.author, Book.source).all()
    }
    with csv_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row.get("title", "Untitled")
            author = row.get("author", "Unknown")
            source = row.get("source", "manual")
            book_key = (title, author, source)
            if book_key in seen_keys:
                skipped += 1
                continue
            book = Book(
                title=title,
                author=author,
                genre=row.get("genre", "General"),
                published_year=int(row["published_year"]) if row.get("published_year") else None,
                average_rating=float(row["average_rating"]) if row.get("average_rating") else 0.0,
                description=row.get("description"),
                ratings_count=int(row["ratings_count"]) if row.get("ratings_count") else 0,
                isbn13=row.get("isbn13"),
                language_code=row.get("language_code"),
                source=source,
            )
            db.add(book)
            seen_keys.add(book_key)
            imported += 1
    db.commit()
    return imported, skipped


def import_goodbooks(db, dataset_dir: Path, limit: int, min_ratings_count: int) -> Tuple[int, int]:
    books_path = dataset_dir / "books.csv"
    tags_path = dataset_dir / "tags.csv"
    book_tags_path = dataset_dir / "book_tags.csv"
    missing = [path.name for path in (books_path, tags_path, book_tags_path) if not path.exists()]
    if missing:
        raise SystemExit(
            f"Missing goodbooks files in {dataset_dir}: {', '.join(missing)}. "
            "Run the importer with --download-goodbooks or place the CSV files in that directory first."
        )

    tag_lookup = load_tag_lookup(tags_path)
    genres_by_book = load_book_genres(book_tags_path, tag_lookup)

    imported = 0
    skipped = 0
    seen_keys = {
        (title, author, source)
        for title, author, source in db.query(Book.title, Book.author, Book.source).all()
    }
    with books_path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ratings_count = int(row["work_ratings_count"]) if row.get("work_ratings_count") else 0
            if ratings_count < min_ratings_count:
                continue
            if imported >= limit:
                break

            goodreads_book_id = row["goodreads_book_id"]
            title = row.get("title") or row.get("original_title") or "Untitled"
            author = (row.get("authors") or "Unknown")[:255]
            book_key = (title[:255], author, "goodbooks-10k")
            if book_key in seen_keys:
                skipped += 1
                continue
            book = Book(
                title=title[:255],
                author=author,
                genre=genres_by_book.get(goodreads_book_id, "General"),
                published_year=int(float(row["original_publication_year"])) if row.get("original_publication_year") else None,
                average_rating=float(row["average_rating"]) if row.get("average_rating") else 0.0,
                ratings_count=ratings_count,
                isbn13=(row.get("isbn13") or None)[:20] if row.get("isbn13") else None,
                language_code=(row.get("language_code") or None)[:10] if row.get("language_code") else None,
                source="goodbooks-10k",
                description=(
                    f"Imported from goodbooks-10k. Goodreads book id {goodreads_book_id}; "
                    f"books_count={row.get('books_count')}; text_reviews={row.get('work_text_reviews_count')}."
                )[:2000],
            )
            db.add(book)
            seen_keys.add(book_key)
            imported += 1
    db.commit()
    return imported, skipped


def main() -> None:
    args = parse_args()
    validate_args(args)
    ensure_schema()
    db = SessionLocal()
    try:
        if args.reset:
            maybe_reset_books(db)

        if args.download_goodbooks:
            download_goodbooks_files(Path(args.goodbooks_dir))

        if args.csv_path:
            csv_path = Path(args.csv_path)
            if not csv_path.exists():
                raise SystemExit(f"File not found: {csv_path}")
            imported, skipped = import_simple_csv(db, csv_path)
            print(f"Imported {imported} books from {csv_path}")
            if skipped:
                print(f"Skipped {skipped} duplicate rows already present in the database")
            return

        dataset_dir = Path(args.goodbooks_dir)
        if not args.download_goodbooks and not dataset_dir.exists():
            raise SystemExit(
                f"Dataset directory not found: {dataset_dir}. Run with --download-goodbooks to fetch the files automatically."
            )

        imported, skipped = import_goodbooks(
            db=db,
            dataset_dir=dataset_dir,
            limit=args.limit,
            min_ratings_count=args.min_ratings_count,
        )
        print(f"Imported {imported} books from goodbooks-10k in {args.goodbooks_dir}")
        if skipped:
            print(f"Skipped {skipped} duplicate rows already present in the database")
    finally:
        db.close()


if __name__ == "__main__":
    main()
