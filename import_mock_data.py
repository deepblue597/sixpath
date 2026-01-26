#!/usr/bin/env python3
"""
Script to import MOCK_DATA.csv into the application's database (users table).
Usage:
    python scripts/import_mock_data.py [--db-url URL] [--csv path] [--dry-run]

By default the script reads DB URL from `utils.config.get_settings().database_url` and CSV from `MOCK_DATA.csv`.
It will skip inserting rows where an existing user with the same email already exists.
"""
from __future__ import annotations

import csv
import argparse
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from utils.config import get_settings
from models.database_models import UserModel, Base


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--db-url", help="Database URL (overrides settings)")
    p.add_argument("--csv", default="MOCK_DATA.csv", help="Path to mock CSV file")
    p.add_argument("--dry-run", action="store_true", help="Don't commit changes; just show what would be inserted")
    return p.parse_args()


def load_csv(path: str):
    rows = []
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for r in reader:
            rows.append(r)
    return rows


def main():
    args = parse_args()
    settings = get_settings()
    db_url = args.db_url or settings.database_url

    print(f"Using DB: {db_url}")
    engine = create_engine(db_url)

    # Ensure tables exist (useful for sqlite/test)
    Base.metadata.create_all(engine)

    rows = load_csv(args.csv)
    print(f"Loaded {len(rows)} rows from {args.csv}")

    inserted = 0
    skipped = 0
    with Session(engine) as session:
        for r in rows:
            email = (r.get("email") or "").strip()
            first_name = (r.get("first_name") or "").strip()
            last_name = (r.get("last_name") or "").strip()
            company = (r.get("company") or None)
            sector = (r.get("sector") or None)
            phone = (r.get("phone") or None)

            # skip empty rows
            if not (first_name or last_name or email):
                skipped += 1
                continue

            # check duplicate by email
            if email:
                existing = session.query(UserModel).filter(UserModel.email == email).first()
                if existing:
                    skipped += 1
                    print(f"Skipping existing email: {email}")
                    continue

            user = UserModel(
                first_name=first_name,
                last_name=last_name,
                company=company,
                sector=sector,
                is_me=False,
                email=email or None,
                phone=phone or None,
            )
            session.add(user)
            if not args.dry_run:
                session.commit()
            inserted += 1
            print(f"Inserted: {first_name} {last_name} <{email}>")

    print(f"Done. Inserted: {inserted}. Skipped: {skipped}.")


if __name__ == '__main__':
    main()
