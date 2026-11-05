# -*- coding: utf-8 -*-
"""Своя Т9: маленькая языковая модель на частотах слов.

Заготовка. Допиши функции, отмеченные TODO, по их описаниям (докстрингам).
Имена функций, их аргументы и формат результата не меняй: по ним работает
проверка python3 checks/acceptance.py и демонстрационная программа python3 demo.py.
Можно добавлять свои вспомогательные функции и константы.
Сторонние библиотеки запрещены: только стандартная библиотека Python.
"""
from __future__ import annotations

import random
import re

START = "<s>"   
END = "</s>"    


# ---------------------------------------------------------------- Задание 1

def normalize(word):
    """Привести слово к нижнему регистру и заменить «ё» на «е».

    >>> normalize("Ёжик")
    'ежик'
    """
    return word.lower().replace("ё", "е")


def tokenize(text):
    """Разбить текст на слова (токены).

    Правила:
    - текст приводится функцией normalize (нижний регистр, «ё» -> «е»);
    - слово — непрерывная цепочка русских букв (а–я), латинских букв (a–z) и цифр;
    - дефис остаётся внутри слова, только если и слева, и справа от него буква
      или цифра: «кто-то» — одно слово; в остальных случаях дефис — разделитель;
    - всё остальное (пробелы, знаки препинания, тире «—», кавычки) — разделители.

    >>> tokenize("Кто-то съел ВСЁ, что было!")
    ['кто-то', 'съел', 'все', 'что', 'было']
    >>> tokenize("По-моему - нет")
    ['по-моему', 'нет']
    """
    text = normalize(text)
    pattern = r"[а-яa-z0-9]+(?:-[а-яa-z0-9]+)*"
    return re.findall(pattern, text)


def split_sentences(text):
    """Разбить текст на предложения, каждое предложение — список слов.

    Граница предложения — любой из символов . ! ? … и перевод строки.
    Несколько таких символов подряд («?!», «...») — одна граница.
    Каждый кусок разбивается функцией tokenize; пустые предложения
    (в которых не осталось ни одного слова) выбрасываются.

    >>> split_sentences("Привет! Как дела?\\nХорошо... Спасибо")
    [['привет'], ['как', 'дела'], ['хорошо'], ['спасибо']]
    """
    chunks = re.split(r"[.!?…\n]+", text)
    result = []
    for chunk in chunks:
        words = tokenize(chunk)
        if words:                      
            result.append(words)
    return result


def read_sentences(path):
    """Прочитать файл (UTF-8) и вернуть split_sentences от его текста.

    Готовая функция, менять не нужно.
    """
    with open(path, encoding="utf-8") as file:
        return split_sentences(file.read())


# ---------------------------------------------------------------- Задание 2

def count_words(sentences):
    """Посчитать, сколько раз встречается каждое слово.

    sentences — список предложений (каждое — список слов).
    Возвращает словарь {слово: сколько раз встретилось}.

    >>> count_words([["кот", "спит"], ["кот"]])
    {'кот': 2, 'спит': 1}
    """
    counts = {}
    for sentence in sentences:
        for word in sentence:
            counts[word] = counts.get(word, 0) + 1
    return counts


def top_k(counts, k):
    """Вернуть k ключей словаря с наибольшими значениями.

    Порядок: по убыванию значения, при равенстве — по алфавиту (обычное
    сравнение строк в Python). Если ключей меньше k — вернуть все.

    >>> top_k({"б": 2, "а": 2, "в": 5, "г": 1}, 3)
    ['в', 'а', 'б']
    """
    ordered = sorted(counts, key=lambda word: (-counts[word], word))
    return ordered[:k]


def complete(prefix, word_counts, k=3):
    """Дописать слово по началу.

    prefix приводится функцией normalize, лишние пробелы по краям убираются.
    Кандидаты — все слова из word_counts, которые начинаются с prefix
    (само слово, равное prefix, тоже подходит). Вернуть top_k кандидатов.
    Пустой prefix подходит ко всем словам. Нет кандидатов — пустой список.

    >>> complete("ко", {"кот": 5, "кошка": 2, "кит": 9})
    ['кот', 'кошка']
    """
    prefix = normalize(prefix.strip())
    candidates = {
        word: count
        for word, count in word_counts.items()
        if word.startswith(prefix)
    }
    return top_k(candidates, k)


# ---------------------------------------------------------------- Задание 3

def count_pairs(sentences):
    """Посчитать пары соседних слов (биграммы).

    Каждое предложение дополняется маркерами: [START] + предложение + [END].
    Для каждой пары соседей (первое, второе) увеличить счётчик pairs[первое][второе].
    Возвращает словарь словарей {слово: {следующее слово: сколько раз}}.

    >>> count_pairs([["кот", "спит"]])
    {'<s>': {'кот': 1}, 'кот': {'спит': 1}, 'спит': {'</s>': 1}}
    """
    pairs = {}
    for sentence in sentences:
        extended = [START] + sentence + [END]
        for i in range(len(extended) - 1):
            first = extended[i]
            second = extended[i + 1]
            followers = pairs.setdefault(first, {})
            followers[second] = followers.get(second, 0) + 1
    return pairs


def next_words(word, pairs, k=3):
    """Подсказать следующее слово по одному предыдущему.

    word приводится функцией normalize. Чтобы узнать, с каких слов начинаются
    предложения, передай маркер START. Кандидаты — слова, которые шли после word,
    кроме маркера END. Вернуть top_k кандидатов. Слова нет в pairs — пустой список.

    >>> next_words("кот", {"кот": {"спит": 3, "ест": 1, "</s>": 7}})
    ['спит', 'ест']
    """
    word = normalize(word)
    if word not in pairs:
        return []
    candidates = {
        follower: count
        for follower, count in pairs[word].items()
        if follower != END
    }
    return top_k(candidates, k)


# ---------------------------------------------------------------- Задание 4

def count_ngrams(sentences, n):
    """Посчитать n-граммы: какое слово идёт после каждого контекста из n-1 слов.

    Предложение дополняется: [START] * (n - 1) + предложение + [END].
    Для каждого слова, начиная с позиции n - 1, контекст — это n - 1 слов перед
    ним, склеенные через один пробел. Возвращает {контекст: {слово: сколько раз}}.
    При n = 1 контекст — пустая строка "", при n = 2 результат совпадает с count_pairs.

    >>> count_ngrams([["кот", "спит"]], 3)
    {'<s> <s>': {'кот': 1}, '<s> кот': {'спит': 1}, 'кот спит': {'</s>': 1}}
    """
    ngrams = {}
    pad = n - 1
    for sentence in sentences:
        extended = [START] * pad + sentence + [END]
        for i in range(pad, len(extended)):
            context = " ".join(extended[i - pad:i])   
            word = extended[i]
            followers = ngrams.setdefault(context, {})
            followers[word] = followers.get(word, 0) + 1
    return ngrams


def build_model(sentences, max_n=3):
    """Собрать модель: словарь {n: count_ngrams(sentences, n)} для n от 1 до max_n.

    >>> sorted(build_model([["кот"]], 2))
    [1, 2]
    """
    return {n: count_ngrams(sentences, n) for n in range(1, max_n + 1)}


def context_for(history, n):
    """Контекст для n-граммы: последние n - 1 слов истории, склеенные пробелом.

    history — слова, набранные с начала текущего предложения (уже нормализованы).
    Если слов не хватает, слева добавляются маркеры START, как при подсчёте.
    При n = 1 контекст — пустая строка.

    >>> context_for(["я", "не", "знаю"], 3)
    'не знаю'
    >>> context_for(["я"], 3)
    '<s> я'
    >>> context_for(["я", "не"], 1)
    ''
    """
    pad = n - 1
    if pad == 0:
        return ""
    tail = history[-pad:] if pad <= len(history) else list(history)
    missing = pad - len(tail)
    context_words = [START] * missing + list(tail)
    return " ".join(context_words)


def find_context(history, model):
    """Найти самый длинный контекст, который модель видела (откат, back-off).

    Слова history приводятся функцией normalize. Пусть N — наибольший ключ model.
    Перебираем n = N, N-1, ..., 1: если контекст context_for(history, n) есть
    в model[n], вернуть пару (n, контекст). Не нашёлся ни один — вернуть None.

    >>> find_context(["кот", "сидит"], {1: {"": {"кот": 1}}, 2: {"кот": {"сидит": 1}}})
    (1, '')
    """
    history = [normalize(word) for word in history]
    if not model:
        return None
    max_n = max(model)
    for n in range(max_n, 0, -1):
        context = context_for(history, n)
        if context in model.get(n, {}):
            return (n, context)
    return None


def predict(history, model, k=3):
    """Подсказать следующее слово по всей набранной истории.

    found = find_context(history, model). Если None — пустой список. Иначе
    кандидаты — model[n][контекст] без маркера END; вернуть top_k кандидатов.
    """
    found = find_context(history, model)
    if found is None:
        return []
    n, context = found
    candidates = {
        word: count
        for word, count in model[n][context].items()
        if word != END
    }
    return top_k(candidates, k)


# ---------------------------------------------------------------- Бонус 5

def generate_greedy(start, model, max_words=20):
    """Жадная генерация: каждый раз брать самое частое продолжение.

    start — список начальных слов (приводятся normalize), может быть пустым.
    Повторять не больше max_words раз:
      found = find_context(слова, model); если None — остановиться;
      counts = model[n][контекст]; выбрать top_k(counts, 1)[0] — маркер END
      тоже участвует; если выбран END — остановиться; иначе дописать слово.
    Вернуть список: начальные слова + сгенерированные (без маркеров).
    """
    words = [normalize(w) for w in start]
    for _ in range(max_words):
        found = find_context(words, model)
        if found is None:
            break
        n, context = found
        counts = model[n][context]
        best = top_k(counts, 1)[0]
        if best == END:
            break
        words.append(best)
    return words


def pick_random(counts, rng):
    """Выбрать слово случайно, с вероятностью, пропорциональной частоте.

    Чтобы результат совпадал с проверкой, порядок строго такой:
    1) кандидаты упорядочены как в top_k (по убыванию частоты, затем по алфавиту);
    2) r = rng.random() * (сумма всех частот);
    3) идём по кандидатам, накапливая сумму частот; вернуть первого,
       у которого накопленная сумма стала больше r.
    """
    candidates = top_k(counts, len(counts))       
    total = sum(counts[w] for w in candidates)
    r = rng.random() * total
    acc = 0
    for word in candidates:
        acc += counts[word]
        if acc > r:
            return word
    return candidates[-1]


def generate_random(start, model, seed, max_words=20):
    """Случайная генерация: как generate_greedy, но слово выбирает pick_random.

    Генератор случайных чисел создаётся один раз в начале: rng = random.Random(seed).
    С одинаковым seed результат всегда одинаковый.
    """
    rng = random.Random(seed)
    words = [normalize(w) for w in start]
    for _ in range(max_words):
        found = find_context(words, model)
        if found is None:
            break
        n, context = found
        counts = model[n][context]
        best = pick_random(counts, rng)
        if best == END:
            break
        words.append(best)
    return words


# ---------------------------------------------------------------- Бонус 6

def suggest(typed, model, k=3):
    """Подсказка как в клавиатуре телефона: учитывает и контекст, и начало слова.

    typed — то, что человек уже набрал, например "Я не зна" или "я не ".
    1) Берём только последнее предложение: часть typed после последней границы
       предложения (. ! ? … или перевод строки).
    2) Если последний символ typed — буква или цифра (из тех, что tokenize
       включает в слова; «ё» тоже считается) — последнее слово недописано:
       prefix = последнее слово, history = слова перед ним.
       Иначе (пробел, запятая, пустая строка, конец предложения): prefix = "",
       history = все слова последнего предложения.
    3) Перебираем n от наибольшего к 1: контекст context_for(history, n);
       если он есть в model[n], кандидаты — слова оттуда, которые начинаются
       с prefix (кроме END). Первый уровень, где кандидаты нашлись, — ответ: top_k.
    4) Нигде не нашлось — пустой список.

    Откат здесь не такой, как в predict: predict останавливается на первом
    известном контексте (даже если там только END), а suggest идёт дальше,
    пока не найдёт подходящих кандидатов. Подробнее — materials/model.md.

    >>> suggest("Кот с", build_model([["кот", "спит"], ["кот", "сидит"], ["пес", "спит"]]))
    ['сидит', 'спит']
    """
    if not model:
        return []

    
    last_sentence = re.split(r"[.!?…\n]", typed)[-1]

    if last_sentence and re.match(r"[а-яёa-z0-9]", last_sentence[-1]):
        m = re.search(r"[а-яёa-z0-9]+(?:-[а-яёa-z0-9]+)*$", last_sentence)
        prefix = m.group(0) if m else ""
        history_text = last_sentence[:m.start()] if m else last_sentence
    else:
        prefix = ""
        history_text = last_sentence

    prefix = normalize(prefix)
    history = tokenize(history_text)

    
    max_n = max(model)
    for n in range(max_n, 0, -1):
        context = context_for(history, n)
        if context not in model.get(n, {}):
            continue
        candidates = {
            word: count
            for word, count in model[n][context].items()
            if word != END and word.startswith(prefix)
        }
        if candidates:
            return top_k(candidates, k)
    return []
