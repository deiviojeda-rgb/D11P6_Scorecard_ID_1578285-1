# Примеры для отчёта

## Один маленький пример условного подсчёта

Ниже игрушечные отметки, которые не взяты из твоего журнала. Мы хотим отдельно посчитать `pass` и `fail`, оставив остальные отметки за пределами этих двух чисел.

```sql
WITH toy_marks(verdict) AS (
    VALUES ('pass'), ('fail'), ('unclear'), ('pass'), ('na')
)
SELECT
    SUM(CASE WHEN verdict = 'pass' THEN 1 ELSE 0 END) AS passed,
    SUM(CASE WHEN verdict = 'fail' THEN 1 ELSE 0 END) AS failed
FROM toy_marks;
```

Результат: `passed = 2`, `failed = 1`. Для каждой строки `CASE` выбирает 1 при нужной отметке и 0 в остальных случаях; `SUM` складывает эти числа. Это объяснение приёма. Состав групп, единицу подсчёта и запросы своего отчёта ты определяешь по заданию.

## Python и JOIN без повторения попыток

Этот пример можно запустить отдельно. Он создаёт игрушечную базу в памяти и не открывает файлы проекта. У первой попытки две оценки, у второй ни одной. Цель примера — вывести **по одной строке на попытку**, вместе с числом её оценок. Это не отчёт Дня 11.

```python
import sqlite3

with sqlite3.connect(':memory:') as con:
    con.executescript('''
        CREATE TABLE attempts (
            attempt_id INTEGER PRIMARY KEY,
            model TEXT NOT NULL
        );
        CREATE TABLE assessments (
            assessment_id INTEGER PRIMARY KEY,
            attempt_id INTEGER NOT NULL,
            dimension_id TEXT NOT NULL
        );
        INSERT INTO attempts VALUES (1, 'toy-model'), (2, 'toy-model');
        INSERT INTO assessments VALUES
            (10, 1, 'meaning'), (11, 1, 'calculation');
    ''')
    query = '''
        SELECT a.attempt_id, a.model, n.mark_count
        FROM attempts AS a
        LEFT JOIN (
            SELECT attempt_id, COUNT(*) AS mark_count
            FROM assessments
            GROUP BY attempt_id
        ) AS n ON n.attempt_id = a.attempt_id
        WHERE a.model = ?
        ORDER BY a.attempt_id
    '''
    for attempt_id, model, mark_count in con.execute(query, ('toy-model',)):
        if mark_count is None:
            mark_count = 0
        print(attempt_id, model, mark_count)
```

Вывод:

```text
1 toy-model 2
2 toy-model 0
```

Внутренний запрос сначала сводит оценки к одной строке на `attempt_id`. Поэтому JOIN не размножает попытки. `LEFT JOIN` сохраняет вторую попытку, даже когда оценки для неё нет. В этом случае число оценок равно нулю; никакого вывода о качестве ответа мы не сделали.

Параметр `?` получает значение отдельным аргументом `('toy-model',)`. Так пользовательский текст остаётся значением, а не становится частью SQL. В реальном журнале также бывают оценки пар: этот учебный пример не подсчитывает их и не заменяет требования отчёта.

Схемы сверены с `data/schema.sql` и `data/journal_schema.sql`. Если нужно увидеть все поля и ограничения, открывай эти файлы; значения и связи в этой памятке не вводят новых требований к проекту.
