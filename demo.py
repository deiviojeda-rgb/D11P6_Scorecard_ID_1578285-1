# -*- coding: utf-8 -*-
"""Демонстрационная программа: показывает, что умеет твоя модель из src/t9.py. Выдана готовой, менять не нужно.

Запуск из корня репозитория:

    python3 demo.py words --corpus datasets/chats_2000.txt                    # частые слова       (задание 2)
    python3 demo.py complete при --corpus datasets/chats_2000.txt --k 3       # дописать слово     (задание 2)
    python3 demo.py next можешь --corpus datasets/chats_2000.txt --k 3        # следующее по паре  (задание 3)
    python3 demo.py predict "можешь прислать" --corpus datasets/chats_2000.txt  # с откатом      (задание 4)
    python3 demo.py greedy я --corpus datasets/chats_2000.txt                 # жадная генерация   (бонус 5)
    python3 demo.py random я --corpus datasets/chats_2000.txt --seed 7        # случайная         (бонус 5)
    python3 demo.py suggest "можешь при" --corpus datasets/chats_2000.txt     # как в телефоне     (бонус 6)

Числа в скобках — частоты: сколько раз слово встретилось в корпусе (complete),
после слова (next) или после найденного контекста (predict).

Общие параметры:
    --corpus ПУТЬ   на каком тексте учить модель (по умолчанию datasets/chats_2000.txt)
    --n ЧИСЛО       наибольшая длина n-граммы: модель смотрит на n-1 слов назад (по умолчанию 3)
    --k ЧИСЛО       сколько подсказок показать (по умолчанию 5)
"""
import argparse
import importlib.util
import os
import time
from pathlib import Path

КОРЕНЬ = Path(__file__).resolve().parent


def загрузить_t9():
    путь = КОРЕНЬ / "src" / "t9.py"
    if not путь.exists():
        raise SystemExit("Не найден src/t9.py. Запускай из корня репозитория.")
    spec = importlib.util.spec_from_file_location("t9", путь)
    модуль = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(модуль)
    return модуль


def main():
    разбор = argparse.ArgumentParser(description="Демонстрационная программа модели из src/t9.py")
    разбор.add_argument("команда", choices=["words", "complete", "next", "predict",
                                            "greedy", "random", "suggest"])
    разбор.add_argument("текст", nargs="?", default="")
    разбор.add_argument("--corpus", default=str(КОРЕНЬ / "datasets" / "chats_2000.txt"))
    разбор.add_argument("--n", type=int, default=3)
    разбор.add_argument("--k", type=int, default=5)
    разбор.add_argument("--seed", type=int, default=21)
    разбор.add_argument("--words", type=int, default=20, help="сколько слов сгенерировать")
    арг = разбор.parse_args()

    t9 = загрузить_t9()
    try:
        начало = time.time()
        предложения = t9.read_sentences(арг.corpus)
        print(f"Корпус: {os.path.relpath(арг.corpus)} — предложений {len(предложения)}, "
              f"слов {sum(len(п) for п in предложения)}")

        if арг.команда == "words":
            частоты = t9.count_words(предложения)
            print(f"Разных слов: {len(частоты)}. Самые частые:")
            for слово in t9.top_k(частоты, max(арг.k, 20)):
                print(f"  {частоты[слово]:7d}  {слово}")

        elif арг.команда == "complete":
            частоты = t9.count_words(предложения)
            варианты = t9.complete(арг.текст, частоты, арг.k)
            print(f"«{арг.текст}» → " + ", ".join(f"{в} ({частоты[в]})" for в in варианты))

        elif арг.команда == "next":
            пары = t9.count_pairs(предложения)
            слово = арг.текст or t9.START
            частоты = пары.get(t9.normalize(слово), {})
            варианты = t9.next_words(слово, пары, арг.k)
            print(f"После «{слово}» → " + (", ".join(f"{в} ({частоты.get(в, '?')})" for в in варианты)
                                           or "подсказок нет"))

        else:
            модель = t9.build_model(предложения, арг.n)
            print(f"Модель до {арг.n}-грамм собрана за {time.time() - начало:.1f} с")
            история = t9.tokenize(арг.текст)

            if арг.команда == "predict":
                найдено = t9.find_context(история, модель)
                if найдено is None:
                    print("Модель не знает ни одного подходящего контекста.")
                else:
                    n, контекст = найдено
                    частоты = модель[n][контекст]
                    показ = f"«{контекст}»" if контекст else "пустой"
                    print(f"Контекст {показ} (n = {n}), примеров за ним: {sum(частоты.values())}, "
                          f"вариантов продолжения: {len(частоты)}")
                    подсказка = t9.predict(история, модель, арг.k)
                    print("Подсказка: " + (", ".join(f"{в} ({частоты.get(в, '?')})" for в in подсказка) or
                                           "пусто — после этого контекста в корпусе только конец предложения"))
                    if "</s>" in частоты:
                        print(f"Конец предложения </s> после этого контекста: {частоты['</s>']}")

            elif арг.команда == "greedy":
                print(" ".join(t9.generate_greedy(история, модель, арг.words)))

            elif арг.команда == "random":
                print(f"seed = {арг.seed}")
                print(" ".join(t9.generate_random(история, модель, арг.seed, арг.words)))

            elif арг.команда == "suggest":
                print(f"«{арг.текст}» → " + ", ".join(t9.suggest(арг.текст, модель, арг.k)))

    except NotImplementedError as ошибка:
        raise SystemExit(f"\nЕщё не написано: {ошибка}. Сначала сделай это задание.")


if __name__ == "__main__":
    main()
