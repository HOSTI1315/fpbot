import requests
from bs4 import BeautifulSoup
from utils import extract_time, convert_date_time
import logging

def get_chat_html(url):
    """
    Загружает HTML-контент чата.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        logging.error(f"Ошибка при загрузке страницы: {response.status_code}")
        return None

def parse_chat_messages(html):
    """
    Парсит сообщения из HTML-контента чата.
    """
    soup = BeautifulSoup(html, "html.parser")
    messages = []
    for message in soup.find_all("div", class_="chat-msg-item"):
        username_tag = message.find("a", class_="chat-msg-author-link")
        username = username_tag.text.strip() if username_tag else "Неизвестно"
        link = username_tag["href"] if username_tag else "#"
        text_tag = message.find("div", class_="chat-msg-text")
        text = text_tag.text.strip() if text_tag else ""
        time_tag = message.find("div", class_="chat-msg-date")
        time_str = time_tag["title"] if time_tag and "title" in time_tag.attrs else None
        messages.append({"text": text, "username": username, "link": link, "time": time_str})
    return messages