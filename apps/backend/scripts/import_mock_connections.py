#!/usr/bin/env python3
"""
Script to import MOCK_DATA_connections.csv into the connections table.
Usage:
    python scripts/import_mock_connections.py [--db-url URL] [--csv path] [--dry-run]

By default the script reads DB URL from `utils.config.get_settings().database_url` 
and CSV from `MOCK_DATA_connections.csv`.
It will skip inserting rows where person_1 and person_2 are the same ID.
"""
from __future__ import annotations

import csv
import argparse
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from utils.config import get_settings
from models.database_models import ConnectionModel, UserModel, Base


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--db-url", help="Database URL (overrides settings)")
    p.add_argument("--csv", default="MOCK_DATA_connections.csv", help="Path to mock connections CSV file")
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
            person_1 = (r.get("person_1") or "").strip()
            person_2 = (r.get("person_2") or "").strip()
            relationship = (r.get("relationship") or "").strip()
            strength = (r.get("strength") or "").strip()
            notes = (r.get("notes") or "").strip()

            # skip empty rows
            if not (person_1 and person_2):
                skipped += 1
                print(f"Skipping empty row")
                continue

            try:
                person1_id = int(person_1)
                person2_id = int(person_2)
            except ValueError:
                skipped += 1
                print(f"Skipping invalid IDs: {person_1}, {person_2}")
                continue

            # Skip if person_1 and person_2 are the same
            if person1_id == person2_id:
                skipped += 1
                print(f"Skipping same person connection: {person1_id} == {person2_id}")
                continue

            # Verify both users exist
            user1 = session.query(UserModel).filter(UserModel.id == person1_id).first()
            user2 = session.query(UserModel).filter(UserModel.id == person2_id).first()

            if not user1:
                skipped += 1
                print(f"Skipping: person_1 ID {person1_id} not found in users table")
                continue

            if not user2:
                skipped += 1
                print(f"Skipping: person_2 ID {person2_id} not found in users table")
                continue

            # Check if connection already exists (in either direction)
            existing = session.query(ConnectionModel).filter(
                ((ConnectionModel.person1_id == person1_id) & (ConnectionModel.person2_id == person2_id)) |
                ((ConnectionModel.person1_id == person2_id) & (ConnectionModel.person2_id == person1_id))
            ).first()

            if existing:
                skipped += 1
                print(f"Skipping existing connection: {person1_id} <-> {person2_id}")
                continue

            # Parse strength
            try:
                strength_val = int(strength) if strength else None
            except ValueError:
                strength_val = None

            connection = ConnectionModel(
                person1_id=person1_id,
                person2_id=person2_id,
                relationship=relationship or None,
                strength=strength_val,
                notes=notes or None,
            )
            session.add(connection)
            if not args.dry_run:
                session.commit()
            inserted += 1
            print(f"Inserted: {person1_id} <-> {person2_id} ({relationship})")

    print(f"Done. Inserted: {inserted}. Skipped: {skipped}.")


if __name__ == '__main__':
    main()
