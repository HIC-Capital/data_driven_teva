"""
Thesis supervisor matching — student-facing entry point.

Usage:
    python match.py                          # full pipeline (embed + Claude)
    python match.py --top 10                 # keep top 10 after Claude
    python match.py --embed-only             # skip Claude (faster / cheaper)
    python match.py --embed-top 30           # widen Stage-1 candidate pool

Prerequisites:
    - data/professors.json must exist (run: python main.py)
    - OPENAI_API_KEY env var set
    - ANTHROPIC_API_KEY env var set (unless --embed-only)
"""

import argparse
import os

parser = argparse.ArgumentParser(description="HSG Thesis Supervisor Matcher")
parser.add_argument("--top", type=int, default=5, help="Final results to show (default: 5)")
parser.add_argument("--embed-top", type=int, default=20, help="Stage-1 candidate pool size (default: 20)")
parser.add_argument("--embed-only", action="store_true", help="Skip Claude reranking")
args = parser.parse_args()

# Check prerequisites
if not os.path.exists("data/professors.json"):
    print("ERROR: data/professors.json not found. Run `python main.py` first.")
    raise SystemExit(1)

if not os.environ.get("OPENAI_API_KEY"):
    print("ERROR: OPENAI_API_KEY environment variable not set.")
    raise SystemExit(1)

if not args.embed_only and not os.environ.get("ANTHROPIC_API_KEY"):
    print("ERROR: ANTHROPIC_API_KEY not set. Use --embed-only to skip Claude reranking.")
    raise SystemExit(1)

# Load profiles
from src.data_processing.profile_builder import ProfileStore
from src.data_collection.questionnaire import run_questionnaire
from src.matching.matcher import ThesisMatcher

store = ProfileStore()

# Collect student input
student = run_questionnaire()

# Run matching
matcher = ThesisMatcher(store)
results = matcher.match(
    student,
    embed_top_k=args.embed_top,
    final_top_k=args.top,
    skip_claude=args.embed_only,
)

# Display results
print("\n" + "=" * 60)
print("  Top Supervisor Matches")
print("=" * 60)
for r in results:
    print()
    print(str(r))

print("\n" + "=" * 60)
