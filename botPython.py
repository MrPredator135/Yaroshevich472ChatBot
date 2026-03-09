import json
import os
from datetime import datetime, timedelta

# Назва файлу для бази даних (Вимога 1)
DATA_FILE = "student_events.json"

# 1. РОБОТА З ФАЙЛОМ

def load_data():
    """Зчитує дані з файлу при запуску."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return []

def save_data(events):
    """Автоматично оновлює дані у файлі після змін."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as file:
            json.dump(events, file, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Помилка збереження: {e}")

# ДОПОМІЖНІ ФУНКЦІЇ

def is_valid_datetime(date_str, time_str):
    """Перевіряє, чи існують введені дата та час (Вимога перевірки коректності)."""
    try:
        datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        return True
    except ValueError:
        return False

def print_event(e, index=None):
    """Виведення події через print()."""
    prefix = f"{index}. " if index is not None else "• "
    print(f"{prefix}{e['date']} [{e['start_time']}] - {e['title']}")
    print(f"   Опис: {e['description']} | Тривалість: {e['duration']}")

def check_conflicts(events, new_date, new_time, exclude_index=None):
    """Перевірка конфліктів у розкладі."""
    for i, e in enumerate(events):
        if i == exclude_index: continue
        if e['date'] == new_date and e['start_time'] == new_time:
            return e
    return None

# ОСНОВНІ КОМАНДИ

def greet_user():
    """Команда 'вітання'."""
    print("\n Бот: Привіт! Я твій помічник для організації подій.")

def show_help():
    """Команда 'допомога'."""
    print("\n Список доступних команд")
    print("вітання, допомога, додати подію, показати події, редагувати подію,")
    print("видалити подію, події на тиждень, події на сьогодні, події на завтра,")
    print("найближча подія, фільтри, вийти")

def add_event(events):
    """Додавання події з перевіркою реальності дати/часу."""
    print("\n Додавання нової події ")
    title = input("Назва: ").strip()
    
    # Цикл перевірки коректності дати
    while True:
        date = input("Дата (YYYY-MM-DD): ").strip()
        time = input("Час початку (HH:MM): ").strip()
        
        if is_valid_datetime(date, time):
            break
        print("Помилка: Некоректна дата або час. Спробуйте ще раз.")

    conflict = check_conflicts(events, date, time)
    if conflict:
        print(f" Конфлікт! Вже є подія: {conflict['title']}")
        if input("Все одно додати? (так/ні): ").lower() != 'так': return

    desc = input("Категорія/опис: ").strip()
    dur = input("Тривалість (необов'язково): ").strip()

    events.append({
        "title": title, "date": date, "start_time": time,
        "description": desc, "duration": dur or "не вказано"
    })
    save_data(events)
    print("Система: Подію додано!")

def show_all_events(events):
    if not events:
        print("Список порожній.")
        return
    for i, e in enumerate(sorted(events, key=lambda x: x['date']), 1):
        print_event(e, i)

def edit_event(events):
    """Редагування з перевіркою реальності нових даних."""
    show_all_events(events)
    try:
        idx = int(input("\nНомер події для редагування: ")) - 1
        if 0 <= idx < len(events):
            e = events[idx]
            print("(Натисніть Enter, щоб залишити без змін)")
            
            new_title = input(f"Нова назва ({e['title']}): ") or e['title']
            
            while True:
                new_date = input(f"Нова дата ({e['date']}): ") or e['date']
                new_time = input(f"Новий час ({e['start_time']}): ") or e['start_time']
                if is_valid_datetime(new_date, new_time):
                    break
                print("Помилка: Некоректна дата або час. Спробуйте ще раз")
            
            new_desc = input(f"Новий опис ({e['description']}): ") or e['description']
            new_dur = input(f"Нова тривалість ({e['duration']}): ") or e['duration']
            
            # Оновлення даних
            events[idx] = {
                "title": new_title, "date": new_date, "start_time": new_time,
                "description": new_desc, "duration": new_dur
            }
            save_data(events)
            print("Оновлено!")
    except ValueError: print("Помилка вводу.")

def delete_event(events):
    show_all_events(events)
    try:
        idx = int(input("\nНомер події для видалення: ")) - 1
        if 0 <= idx < len(events):
            removed = events.pop(idx)
            save_data(events)
            print(f"Подію '{removed['title']}' видалено.")
    except ValueError: print("Помилка.")

# РОБОТА З ЧАСОМ

def show_by_time(events, mode):
    today = datetime.now().date()
    if mode == "сьогодні": target_start, target_end = today, today
    elif mode == "завтра": target_start = target_end = today + timedelta(days=1)
    elif mode == "тиждень": target_start, target_end = today, today + timedelta(days=7)

    print(f"\n Події ({mode}) ")
    found = False
    for e in events:
        try:
            ev_date = datetime.strptime(e['date'], "%Y-%m-%d").date()
            if target_start <= ev_date <= target_end:
                print_event(e)
                found = True
        except ValueError: continue
    if not found: print("Нічого не знайдено.")

def show_next_event(events):
    now = datetime.now()
    future = []
    for e in events:
        try:
            ev_dt = datetime.strptime(f"{e['date']} {e['start_time']}", "%Y-%m-%d %H:%M")
            if ev_dt > now: future.append((ev_dt, e))
        except ValueError: continue
    
    if future:
        closest = min(future, key=lambda x: x[0])[1]
        print("\n Найближча подія ")
        print_event(closest)
    else: print("Майбутніх подій немає.")

# ФІЛЬТРИ

def filter_events(events):
    query = input("Введіть категорію або слово для пошуку: ").lower()
    for e in events:
        if query in e['description'].lower() or query in e['title'].lower():
            print_event(e)

# ГОЛОВНИЙ ЦИКЛ 

def main():
    events = load_data()
    print("Система готова. Введіть команду (наприклад, 'вітання' або 'допомога'):")
    
    while True:
        cmd = input("\nВведіть команду: ").strip().lower()

        if cmd == "вітання": greet_user()
        elif cmd == "допомога": show_help()
        elif cmd == "додати подію": add_event(events)
        elif cmd == "показати події": show_all_events(events)
        elif cmd == "редагувати подію": edit_event(events)
        elif cmd == "видалити подію": delete_event(events)
        elif cmd == "події на сьогодні": show_by_time(events, "сьогодні")
        elif cmd == "події на завтра": show_by_time(events, "завтра")
        elif cmd == "події на тиждень": show_by_time(events, "тиждень")
        elif cmd == "найближча подія": show_next_event(events)
        elif cmd == "фільтри": filter_events(events)
        elif cmd == "вийти":
            print("Роботу завершено. До зустрічі!")
            break
        else:
            print("Невідома команда. Напишіть 'допомога'.")

if __name__ == "__main__":
    main()