#!/usr/bin/env python3
"""Typing Speed Tester - a simple terminal game using only the standard library."""

import json
import random
import time
from difflib import SequenceMatcher
from pathlib import Path

SCORE_FILE = Path.home() / ".typing_speed_scores.json"

SENTENCES = {
    "easy": [
        "The quick brown fox jumps over the lazy dog.",
        "Practice makes perfect when you type every day.",
        "A small step each day leads to big progress.",
        "The sun rises in the east and sets in the west.",
        "Good code is simple, clear, and easy to read.",
    ],
    "medium": [
        "Programming is the art of telling a computer exactly what you want it to do.",
        "Consistency matters more than speed when you are learning a new skill.",
        "Every expert was once a beginner who refused to give up on their goals.",
        "Debugging is twice as hard as writing the code in the first place.",
        "A journey of a thousand miles begins with a single step forward.",
    ],
    "hard": [
        "Premature optimization is the root of all evil, but readable code is its own reward; always test!",
        "In 2024, developers wrote over 100,000 lines of code (with 3% bugs) before lunch: impressive, right?",
        "\"Simplicity is prerequisite for reliability,\" said Dijkstra; complexity, however, sells more books.",
        "Asynchronous, multi-threaded architectures demand meticulous synchronization & thorough documentation.",
        "The rain in Spain stays mainly in the plain, but the zebra quickly jumped over fifty-six boxes.",
    ],
}


def load_scores():
    try:
        return json.loads(SCORE_FILE.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_scores(scores):
    try:
        SCORE_FILE.write_text(json.dumps(scores, indent=2))
    except OSError:
        print("(Could not save high score.)")


def countdown(seconds=3):
    print("\nGet ready...")
    for i in range(seconds, 0, -1):
        print(f"  {i}...")
        time.sleep(1)
    print("  GO!\n")


def calculate_results(original, typed, elapsed):
    """Return (wpm, accuracy%) using the standard 5-characters-per-word rule."""
    minutes = max(elapsed, 0.001) / 60
    wpm = (len(typed) / 5) / minutes

    # Character-level accuracy: compare position by position
    correct = sum(1 for a, b in zip(original, typed) if a == b)
    accuracy = (correct / max(len(original), 1)) * 100
    # Penalise extra characters typed beyond the target
    if len(typed) > len(original):
        accuracy = max(0.0, accuracy - (len(typed) - len(original)))

    return wpm, accuracy


def choose_difficulty():
    while True:
        choice = input("Choose difficulty (easy / medium / hard): ").strip().lower()
        if choice in SENTENCES:
            return choice
        print("Please type easy, medium, or hard.")


def choose_rounds():
    while True:
        raw = input("How many sentences? (1-5, default 3): ").strip()
        if raw == "":
            return 3
        if raw.isdigit() and 1 <= int(raw) <= 5:
            return int(raw)
        print("Enter a number from 1 to 5.")


def play_round(sentence, number, total):
    print(f"--- Sentence {number}/{total} ---")
    print(f"\n  {sentence}\n")
    input("Press Enter when you're ready to start...")
    countdown()

    print(f"  {sentence}")
    start = time.perf_counter()
    typed = input("  > ")
    elapsed = time.perf_counter() - start

    wpm, accuracy = calculate_results(sentence, typed, elapsed)
    similarity = SequenceMatcher(None, sentence, typed).ratio() * 100

    print(f"\n  Time:     {elapsed:.2f}s")
    print(f"  Speed:    {wpm:.1f} WPM")
    print(f"  Accuracy: {accuracy:.1f}%  (similarity {similarity:.1f}%)\n")
    return wpm, accuracy


def run_test():
    difficulty = choose_difficulty()
    rounds = choose_rounds()
    sentences = random.sample(SENTENCES[difficulty], rounds)

    all_wpm, all_acc = [], []
    for i, sentence in enumerate(sentences, 1):
        wpm, acc = play_round(sentence, i, rounds)
        all_wpm.append(wpm)
        all_acc.append(acc)

    avg_wpm = sum(all_wpm) / len(all_wpm)
    avg_acc = sum(all_acc) / len(all_acc)

    print("=" * 36)
    print("          FINAL RESULTS")
    print("=" * 36)
    print(f"  Difficulty:   {difficulty}")
    print(f"  Average WPM:  {avg_wpm:.1f}")
    print(f"  Avg accuracy: {avg_acc:.1f}%")
    print(f"  Rating:       {rate(avg_wpm)}")

    scores = load_scores()
    best = scores.get(difficulty, 0)
    if avg_wpm > best:
        print(f"\n  New high score for '{difficulty}'! (previous: {best:.1f} WPM)")
        scores[difficulty] = round(avg_wpm, 1)
        save_scores(scores)
    else:
        print(f"\n  Best for '{difficulty}': {best:.1f} WPM")
    print("=" * 36)


def rate(wpm):
    if wpm < 20:
        return "Beginner"
    if wpm < 40:
        return "Average"
    if wpm < 60:
        return "Good"
    if wpm < 80:
        return "Fast"
    return "Expert"


def show_scores():
    scores = load_scores()
    print("\n--- High Scores ---")
    if not scores:
        print("  No scores yet. Take a test first!")
    for level in SENTENCES:
        if level in scores:
            print(f"  {level.capitalize():<7} {scores[level]:.1f} WPM")
    print()


def main():
    print("=" * 36)
    print("      TYPING SPEED TESTER")
    print("=" * 36)

    while True:
        print("\n1) Start test\n2) View high scores\n3) Quit")
        choice = input("Select an option: ").strip()
        if choice == "1":
            run_test()
        elif choice == "2":
            show_scores()
        elif choice == "3":
            print("Goodbye, keep practicing!")
            break
        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")
