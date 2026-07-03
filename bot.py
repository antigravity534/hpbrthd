import os
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup
import requests

def check_birthdays():
    # Настройка часового пояса Москвы (UTC+3)
    msk_tz = timezone(timedelta(hours=3))
    today_msk = datetime.now(msk_tz)
    today_str = today_msk.strftime("%d.%m")  # Получаем 'ДД.ММ' (например, '25.02')

    # Чтение HTML-файла
    try:
        with open("index.html", "r", encoding="utf-8") as file:
            html_content = file.read()
    except FileNotFoundError:
        print("Файл index.html не найден.")
        return

    # Парсинг таблицы
    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.find("table", id="birthday-table")
    if not table:
        print("Таблица с id='birthday-table' не найдена.")
        return

    celebrants = []
    
    rows = table.find_all("tr")[1:]  # Пропускаем заголовок таблицы
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 2:
            name = cols[0].text.strip()
            full_birthday = cols[1].text.strip()  # Читает 'ДД.ММ.ГГГГ'
            
            # Извлекаем только день и месяц (первые две части даты через точку)
            birthday_parts = full_birthday.split(".")
            if len(birthday_parts) >= 2:
                birthday_dm = f"{birthday_parts[0]}.{birthday_parts[1]}"  # Получаем 'ДД.ММ'
                
                if birthday_dm == today_str:
                    # Если есть третья колонка с телеграмом, берем его
                    telegram = cols[2].text.strip() if len(cols) >= 3 else ""
                    if telegram and telegram != "-":
                        celebrants.append(f"{name} ({telegram})")
                    else:
                        celebrants.append(name)

    # Если есть именинники, отправляем сообщение
    if celebrants:
        bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        chat_id = os.environ.get("TELEGRAM_CHAT_ID")

        if not bot_token or not chat_id:
            print("Переменные окружения TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID не настроены.")
            return

        names_str = ", ".join(celebrants)
        message = f"Сегодня день рождения празднует:\n{names_str}! Поздравляем! 🎉"

        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        
        try:
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                print(f"Сообщение отправлено для: {names_str}")
            else:
                print(f"Ошибка отправки сообщения: {response.text}")
        except Exception as e:
            print(f"Ошибка запроса к Telegram API: {e}")
    else:
        print("Сегодня именинников нет.")

if __name__ == "__main__":
    check_birthdays()
