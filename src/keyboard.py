from __future__ import annotations

import sys

from t9 import build_model, read_sentences, suggest

DEFAULT_CORPUS = "src/my_corpus.txt"


def main(argv):
    path = argv[1] if len(argv) > 1 else DEFAULT_CORPUS
    sentences = read_sentences(path)
    model = build_model(sentences)

    print(f"Корпус: {path} ({sum(len(s) for s in sentences)} слов)")
    print("Введите строку и нажмите Enter. Пустая строка или Ctrl+D — выход.")

    while True:
        try:
            typed = input("> ")
        except EOFError:
            print()
            break
        if not typed.strip():
            break
        hints = suggest(typed, model, k=3)
        if hints:
            print("  " + "  ".join(hints))
        else:
            print("  (нет подсказок)")


if __name__ == "__main__":
    main(sys.argv)