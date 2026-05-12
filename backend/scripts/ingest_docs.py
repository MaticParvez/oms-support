#!/usr/bin/env python3
"""
CLI script to bulk-ingest OMS documentation into the knowledge base.

Usage:
  python scripts/ingest_docs.py --dir ../docs
  python scripts/ingest_docs.py --url https://docs.polygon.technology/oms
  python scripts/ingest_docs.py --file path/to/doc.md --category api
"""
import sys
import argparse
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from knowledge.ingestion import ingest_directory, ingest_url, ingest_file
from knowledge.vector_store import count_documents


def main():
    parser = argparse.ArgumentParser(description="Ingest OMS docs into knowledge base")
    parser.add_argument("--dir", help="Directory of markdown files to ingest")
    parser.add_argument("--url", help="URL to ingest")
    parser.add_argument("--file", help="Single file to ingest")
    parser.add_argument("--category", default="docs", help="Category tag")
    parser.add_argument("--glob", default="**/*.md", help="Glob pattern for directory ingestion")
    args = parser.parse_args()

    before = count_documents()

    if args.dir:
        print(f"Ingesting directory: {args.dir}")
        result = ingest_directory(args.dir, category=args.category, glob=args.glob)
        print(f"  Files ingested: {result['ingested']}")
        print(f"  Chunks created: {result['chunks']}")
        if result["errors"]:
            print(f"  Errors: {result['errors']}")

    elif args.url:
        print(f"Ingesting URL: {args.url}")
        ids = ingest_url(args.url, category=args.category)
        print(f"  Chunks created: {len(ids)}")

    elif args.file:
        print(f"Ingesting file: {args.file}")
        ids = ingest_file(args.file, category=args.category)
        print(f"  Chunks created: {len(ids)}")

    else:
        # Default: ingest the bundled docs/ directory
        docs_dir = str(Path(__file__).parent.parent.parent / "docs")
        print(f"Ingesting default docs dir: {docs_dir}")
        result = ingest_directory(docs_dir, category="oms_docs")
        print(f"  Files ingested: {result['ingested']}")
        print(f"  Chunks created: {result['chunks']}")

    after = count_documents()
    print(f"\nKnowledge base: {before} → {after} chunks total")


if __name__ == "__main__":
    main()
