import json
import time
import logging
import re  # Добавлен импорт модуля re
import requests
from collections import defaultdict
from parsers import get_chat_html, parse_chat_messages
from utils import generate_variants, extract_time, convert_date_time, PRICE_REGEX  # Добавлен импорт PRICE_REGEX

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# Загрузка конфигурации
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)
with open("add.json", "r", encoding="utf-8") as f:
    add_config = json.load(f)

CHAT_URL = config["CHAT_URL"]
DISCORD_WEBHOOK_URL = config["DISCORD_WEBHOOK_URL"]
STATS_UPDATE_INTERVAL_MINUTES = config["STATS_UPDATE_INTERVAL_MINUTES"]
MESSAGE_SEND_INTERVAL_MINUTES = config["MESSAGE_SEND_INTERVAL_MINUTES"]

# Генерация словаря фруктов/юнитов
prefixes = add_config["prefixes"]
fruits_with_perm = add_config["fruits_with_perm"]
units_with_shiny = add_config["units_with_shiny"]
items_without_prefixes = add_config["items_without_prefixes"]

all_fruits = {}
for fruit_name, variants in fruits_with_perm.items():
    all_fruits[fruit_name] = generate_variants(fruit_name, variants, prefixes, "perm")

for unit_name, variants in units_with_shiny.items():
    all_fruits[unit_name] = generate_variants(unit_name, variants, prefixes, "shiny")

all_fruits.update(items_without_prefixes)

# Глобальные переменные
fruit_data = defaultdict(list)

def collect_data(messages, fruits):
    current_time = time.localtime()
    current_minutes = current_time.tm_hour * 60 + current_time.tm_min
    for message in messages:
        text = message["text"]
        username = message["username"]
        link = message["link"]
        time_str = message["time"]
        
        if not time_str:
            logging.info(f"Сообщение от {username} пропущено: время не найдено")
            continue
        
        message_time = extract_time(time_str)
        if not message_time:
            logging.info(f"Сообщение от {username} пропущено: время не распознано")
            continue
        
        hours, minutes, _ = map(int, message_time.split(":"))
        message_minutes = hours * 60 + minutes
        time_difference = current_minutes - message_minutes
        
        if time_difference < 0:
            time_difference += 24 * 60
        
        if time_difference > 30:
            logging.info(f"Сообщение от {username} пропущено: старше 30 минут (разница: {time_difference} минут)")
            continue
        
        lines = text.split("\n")
        for line in lines:
            for fruit, variants in fruits.items():
                if any(re.search(rf"\b{re.escape(variant)}\b", line, re.IGNORECASE) for variant in variants):
                    price_match = PRICE_REGEX.search(line)
                    if price_match:
                        price = int(price_match.group(1))
                        user_index = next((index for index, item in enumerate(fruit_data[fruit]) if item["username"] == username), None)
                        
                        if user_index is not None:
                            if price < fruit_data[fruit][user_index]["price"]:
                                del fruit_data[fruit][user_index]
                        
                        fruit_data[fruit].append({"price": price, "username": username, "link": link})
                        logging.info(f"Добавлено: {fruit} - {price} руб. от {username}")
                    break

def calculate_stats():
    stats = {}
    for fruit, data in fruit_data.items():
        if not data:
            continue
        
        total_price = sum(item["price"] for item in data)
        average_price = total_price / len(data)
        best_buyer = max(data, key=lambda x: x["price"])
        
        stats[fruit] = {
            "average_price": average_price,
            "best_buyer": best_buyer
        }
    
    return stats

def send_stats_to_discord(stats):
    description = ""
    for fruit, data in stats.items():
        description += (
            f"💵 **{fruit}**\n"
            f"**Средняя цена:** {data['average_price']:.2f} руб.\n"
            f"**Лучший скупщик:** [{data['best_buyer']['username']}]({data['best_buyer']['link']}) - {data['best_buyer']['price']} руб.\n\n"
        )
    
    embed = {
        "title": "📊 Статистика цен на фрукты",
        "description": description,
        "color": 0x00FF00
    }
    
    payload = {"embeds": [embed]}
    response = requests.post(
        DISCORD_WEBHOOK_URL,
        data=json.dumps(payload),
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 204:
        logging.info("Статистика отправлена в Discord!")
    else:
        logging.error(f"Ошибка при отправке статистики: {response.status_code}")

def main():
    global fruit_data
    last_send_time = time.time()
    
    while True:
        try:
            html = get_chat_html(CHAT_URL)
            if html:
                messages = parse_chat_messages(html)
                collect_data(messages, all_fruits)
                stats = calculate_stats()
                current_time = time.time()
                
                if current_time - last_send_time >= MESSAGE_SEND_INTERVAL_MINUTES * 60:
                    if stats:
                        send_stats_to_discord(stats)
                    last_send_time = current_time
                
                fruit_data.clear()
            
            time.sleep(STATS_UPDATE_INTERVAL_MINUTES * 60)
        
        except Exception as e:
            logging.error(f"Произошла ошибка: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()