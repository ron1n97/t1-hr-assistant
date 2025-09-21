#!/usr/bin/env python3
"""
Простой тест для проверки исправления ошибки валидации
"""
import requests
import json

def test_hr_chat():
    """Тест HR чата"""
    url = "http://localhost:8000/chat/hr"
    data = {
        "message": "Привет! Как дела?",
        "conversation_id": "test_hr_123"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"HR Chat Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"HR Response: {result['response'][:100]}...")
        else:
            print(f"HR Error: {response.text}")
    except Exception as e:
        print(f"HR Error: {e}")

def test_user_chat():
    """Тест User чата"""
    url = "http://localhost:8000/chat/user"
    data = {
        "message": "Привет! Как дела?",
        "conversation_id": "test_user_123"
    }
    
    try:
        response = requests.post(url, json=data)
        print(f"User Chat Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"User Response: {result['response'][:100]}...")
        else:
            print(f"User Error: {response.text}")
    except Exception as e:
        print(f"User Error: {e}")

if __name__ == "__main__":
    print("Тестирование исправления ошибки валидации...")
    test_hr_chat()
    print()
    test_user_chat()
