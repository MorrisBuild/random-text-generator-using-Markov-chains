# Sherlock Markov Text Generator

This is a simple Python project that generates Sherlock-Holmes-style text using a word-level Markov chain.

It does not need any external Python library. It can download public-domain Sherlock Holmes text from Project Gutenberg and train from that local text file.

## 1. Open the Project Folder

```bash
cd /Users/your_folder
```

## 2. Download the Corpus

```bash
python3 markov_sherlock.py download
```

This saves the training text here:

```bash
data/sherlock_corpus.txt
```

If the download does not work, manually download public-domain Sherlock Holmes text from Project Gutenberg, paste it into `data/sherlock_corpus.txt`, and continue.

## 3. Generate a Story

```bash
python3 markov_sherlock.py generate --words 700 --order 2 --seed "Holmes"
```

Try these variations:

```bash
python3 markov_sherlock.py generate --words 1000 --order 3 --seed "Watson"
python3 markov_sherlock.py generate --words 500 --order 1
python3 markov_sherlock.py generate --words 800 --order 2 --random-seed 42
```

## How It Works

A Markov chain looks at the current sequence of words and randomly chooses a next word based on what appeared in the training text.

For example, with `--order 2`, the generator uses the previous 2 words as its state:

```text
("said", "Holmes") -> ["quietly", "as", "with", ...]
```

Lower order gives more surprising but less coherent text. Higher order gives more coherent text, but it may copy the source style more closely.

## Recommended Settings

Start with:

```bash
python3 markov_sherlock.py generate --words 700 --order 2 --seed "Holmes"
```

Use `--order 3` when you want more readable sentences. Use `--order 1` when you want more strange, experimental output.

## Use Your Own Text

Put any `.txt` file somewhere on your computer and run:

```bash
python3 markov_sherlock.py generate --corpus /path/to/your/file.txt --words 700 --order 2
```

## Optional Improvements

- Add more Sherlock Holmes books to `GUTENBERG_URLS` in `markov_sherlock.py`.
- Save generated stories to a file:

```bash
python3 markov_sherlock.py generate --words 1000 --order 2 > my_story.txt
```

- Build a small web app later with Flask or FastAPI so the generator can run from a browser.

## Note

This creates imitation-style text from public-domain material. The output may be odd or repetitive because Markov chains do not understand plot, character motivation, or logic. They only model word transitions.
