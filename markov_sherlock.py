#!/usr/bin/env python3
"""
Word-level Markov chain text generator for Sherlock-Holmes-style stories.

Usage examples:
  python markov_sherlock.py download
  python markov_sherlock.py generate --words 600 --order 2 --seed "Holmes"
"""

from __future__ import annotations

import argparse
import random
import re
import sys
import textwrap
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple


PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"
CORPUS_PATH = DATA_DIR / "sherlock_corpus.txt"

GUTENBERG_URLS = [
    # The Adventures of Sherlock Holmes, public domain in the US.
    "https://www.gutenberg.org/files/1661/1661-0.txt",
    # The Memoirs of Sherlock Holmes, public domain in the US.
    "https://www.gutenberg.org/files/834/834-0.txt",
]


TOKEN_RE = re.compile(r"\w+(?:'\w+)?|[.!?,;:\"()]")


def download_corpus(output_path: Path = CORPUS_PATH) -> None:
    """Download public-domain Sherlock Holmes texts from Project Gutenberg."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    parts: List[str] = []

    for url in GUTENBERG_URLS:
        print(f"Downloading {url}")
        with urllib.request.urlopen(url, timeout=30) as response:
            text = response.read().decode("utf-8", errors="replace")
        parts.append(strip_gutenberg_boilerplate(text))

    output_path.write_text("\n\n".join(parts), encoding="utf-8")
    print(f"Saved corpus to {output_path}")


def strip_gutenberg_boilerplate(text: str) -> str:
    """Remove common Project Gutenberg headers and footers."""
    start_match = re.search(r"\*\*\* START OF (?:THE|THIS) PROJECT GUTENBERG EBOOK .*?\*\*\*", text)
    end_match = re.search(r"\*\*\* END OF (?:THE|THIS) PROJECT GUTENBERG EBOOK .*?\*\*\*", text)

    if start_match:
        text = text[start_match.end() :]
    if end_match:
        text = text[: end_match.start()]

    return text.strip()


def tokenize(text: str) -> List[str]:
    return TOKEN_RE.findall(text)


def build_chain(tokens: List[str], order: int) -> Dict[Tuple[str, ...], List[str]]:
    if len(tokens) <= order:
        raise ValueError("Corpus is too small for the selected order.")

    chain: Dict[Tuple[str, ...], List[str]] = defaultdict(list)
    for index in range(len(tokens) - order):
        state = tuple(tokens[index : index + order])
        next_token = tokens[index + order]
        chain[state].append(next_token)
    return dict(chain)


def choose_start(chain: Dict[Tuple[str, ...], List[str]], seed: Optional[str]) -> Tuple[str, ...]:
    states = list(chain.keys())

    if seed:
        seed_lower = seed.lower()
        matches = [state for state in states if seed_lower in " ".join(state).lower()]
        if matches:
            return random.choice(matches)
        print(f"No matching start found for seed {seed!r}; using a random start.", file=sys.stderr)

    sentence_starts = [state for state in states if state[0][:1].isupper()]
    return random.choice(sentence_starts or states)


def generate_text(
    chain: Dict[Tuple[str, ...], List[str]],
    order: int,
    word_count: int,
    seed: Optional[str] = None,
) -> str:
    if word_count < order:
        raise ValueError("--words must be greater than or equal to --order.")

    state = choose_start(chain, seed)
    output = list(state)

    for _ in range(word_count - order):
        choices = chain.get(state)
        if not choices:
            state = choose_start(chain, seed=None)
            output.extend(state)
            continue

        next_token = random.choice(choices)
        output.append(next_token)
        state = tuple(output[-order:])

    return detokenize(output)


def detokenize(tokens: List[str]) -> str:
    text = " ".join(tokens)
    text = re.sub(r"\s+([.!?,;:])", r"\1", text)
    text = re.sub(r"\(\s+", "(", text)
    text = re.sub(r"\s+\)", ")", text)
    text = re.sub(r'\s+"', ' "', text)
    text = re.sub(r'"\s+', '" ', text)
    text = re.sub(r"\s+", " ", text).strip()
    return textwrap.fill(text, width=88)


def load_chain(corpus_path: Path, order: int) -> Dict[Tuple[str, ...], List[str]]:
    if not corpus_path.exists():
        raise FileNotFoundError(
            f"Corpus not found at {corpus_path}. Run: python markov_sherlock.py download"
        )

    text = corpus_path.read_text(encoding="utf-8")
    tokens = tokenize(text)
    return build_chain(tokens, order)


def generate_command(args: argparse.Namespace) -> None:
    if args.random_seed is not None:
        random.seed(args.random_seed)

    corpus_path = Path(args.corpus) if args.corpus else CORPUS_PATH
    chain = load_chain(corpus_path, args.order)
    story = generate_text(chain, args.order, args.words, args.seed)
    print(story)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate Sherlock-Holmes-style text with a Markov chain."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("download", help="Download public-domain Sherlock Holmes corpus")

    generate = subparsers.add_parser("generate", help="Generate text from the corpus")
    generate.add_argument("--corpus", help="Path to a custom text corpus")
    generate.add_argument("--words", type=int, default=500, help="Approximate token count")
    generate.add_argument(
        "--order",
        type=int,
        default=2,
        choices=range(1, 6),
        metavar="1-5",
        help="Number of previous words used as state. 2 or 3 is a good start.",
    )
    generate.add_argument("--seed", help='Starting hint, for example "Holmes" or "Watson"')
    generate.add_argument("--random-seed", type=int, help="Fixed seed for repeatable output")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    try:
        if args.command == "download":
            download_corpus()
        elif args.command == "generate":
            generate_command(args)
    except (FileNotFoundError, ValueError, TimeoutError, urllib.error.URLError) as error:
        parser.exit(status=1, message=f"Error: {error}\n")


if __name__ == "__main__":
    main()
