from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, date

app = Flask(__name__)

# Хранилище задач: список словарей
tasks = [
    {'id': 1, 'task': 'Купить продукты', 'priority': 'Средний', 'deadline': '2026-03-15', 'done': False},
    {'id': 2, 'task': 'Сдать отчет', 'priority': 'Высокий', 'deadline': '2026-03-12', 'done': False},
    {'id': 3, 'task': 'Полить цветы', 'priority': 'Низкий', 'deadline': '2026-03-18', 'done': True},
]
next_id = 4

# Конфигурация приоритетов для сортировки
PRIORITY_ORDER = {'Высокий': 1, 'Средний': 2, 'Низкий': 3}

def sort_tasks(task_list, sort_by):
    """Функция для сортировки задач по заданному критерию."""
    if sort_by == 'priority':
        # Сортируем по приоритету, используя словарь PRIORITY_ORDER
        return sorted(task_list, key=lambda x: PRIORITY_ORDER.get(x['priority'], 4))
    elif sort_by == 'deadline':
        # Сортируем по сроку. Задачи без срока отправляем в конец.
        return sorted(task_list, key=lambda x: x['deadline'] if x['deadline'] else '9999-99-99')
    else:
        # По умолчанию сортируем по ID (как добавлены)
        return sorted(task_list, key=lambda x: x['id'])

@app.route('/', methods=['GET', 'POST'])
def index():
    global next_id
    today = date.today().isoformat()

    if request.method == 'POST':
        # Добавление новой задачи
        task_text = request.form.get('task')
        priority = request.form.get('priority', 'Средний')
        deadline = request.form.get('deadline')
        if task_text:
            new_task = {
                'id': next_id,
                'task': task_text,
                'priority': priority,
                'deadline': deadline if deadline else None,
                'done': False
            }
            tasks.append(new_task)
            next_id += 1
        return redirect(url_for('index'))

    # Получаем параметр сортировки из URL (например, ?sort=priority)
    sort_by = request.args.get('sort', 'default')

    # Получаем поисковый запрос
    search_query = request.args.get('search', '').lower()

    # Фильтруем задачи по поиску, если есть запрос
    displayed_tasks = tasks
    if search_query:
        displayed_tasks = [t for t in tasks if search_query in t['task'].lower()]

    # Сортируем отфильтрованный список
    sorted_tasks = sort_tasks(displayed_tasks, sort_by)

    return render_template('index.html',
                           tasks=sorted_tasks,
                           today=today,
                           sort_by=sort_by,
                           search_query=search_query)

@app.route('/done/<int:task_id>')
def toggle_done(task_id):
    """Отметить задачу как выполненную/невыполненную."""
    for task in tasks:
        if task['id'] == task_id:
            task['done'] = not task['done']
            break
    # Возвращаемся на ту же страницу с сохранением параметров сортировки
    return redirect(request.referrer or url_for('index'))

@app.route('/delete/<int:task_id>')
def delete_task(task_id):
    """Удалить задачу."""
    global tasks
    tasks = [task for task in tasks if task['id'] != task_id]
    return redirect(request.referrer or url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)