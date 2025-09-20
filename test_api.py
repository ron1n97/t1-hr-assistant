#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы FastAPI сервера
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"


def test_health():
    """Тест проверки здоровья сервиса"""
    print("🔍 Тестирование /health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Сервис здоров: {data['status']}")
            print(f"   Доступные агенты: {data['agents_available']}")
            return True
        else:
            print(f"❌ Ошибка здоровья: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Не удается подключиться к серверу. Убедитесь, что сервер запущен.")
        return False


def test_agents_info():
    """Тест получения информации об агентах"""
    print("\n🔍 Тестирование /agents...")
    try:
        response = requests.get(f"{BASE_URL}/agents")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Информация об агентах получена")
            print(f"   Всего агентов: {data['total_agents']}")
            for agent in data['agents']:
                print(f"   - {agent['agent_type']}: {agent['model']}")
            return True
        else:
            print(f"❌ Ошибка получения агентов: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def test_chat_endpoint(agent_type: str, message: str) -> bool:
    """Тест чата с агентом"""
    print(f"\n🔍 Тестирование /chat/{agent_type}...")
    try:
        response = requests.post(
            f"{BASE_URL}/chat/{agent_type}",
            json={"message": message}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Ответ от {agent_type} агента:")
            print(f"   Время обработки: {data['processing_time']:.2f}с")
            print(f"   Ответ: {data['response'][:100]}...")
            return True
        else:
            print(f"❌ Ошибка чата с {agent_type}: {response.status_code}")
            print(f"   Ответ: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def test_universal_chat():
    """Тест универсального эндпоинта чата"""
    print(f"\n🔍 Тестирование /chat...")
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={
                "message": "Привет! Как дела?",
                "agent_type": "user",
                "conversation_id": "test_session_123"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Универсальный чат работает:")
            print(f"   Агент: {data['agent_type']}")
            print(f"   Сессия: {data['conversation_id']}")
            print(f"   Время: {data['processing_time']:.2f}с")
            return True
        else:
            print(f"❌ Ошибка универсального чата: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def test_validation_errors():
    """Тест обработки ошибок валидации"""
    print(f"\n🔍 Тестирование валидации...")
    try:
        # Пустое сообщение
        response = requests.post(
            f"{BASE_URL}/chat/hr",
            json={"message": ""}
        )
        
        if response.status_code == 422:
            print("✅ Валидация работает (пустое сообщение отклонено)")
            return True
        else:
            print(f"❌ Неожиданный статус: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


def main():
    """Основная функция тестирования"""
    print("🚀 Запуск тестов T1 HR Assistant API")
    print("=" * 50)
    
    tests = [
        ("Проверка здоровья", test_health),
        ("Информация об агентах", test_agents_info),
        ("Чат с HR агентом", lambda: test_chat_endpoint("hr", "Расскажи о корпоративной культуре")),
        ("Чат с User агентом", lambda: test_chat_endpoint("user", "Помоги с настройкой рабочего места")),
        ("Универсальный чат", test_universal_chat),
        ("Валидация", test_validation_errors),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ Тест '{test_name}' завершился с ошибкой: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Результаты: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты пройдены успешно!")
    else:
        print("⚠️  Некоторые тесты не прошли. Проверьте логи выше.")


if __name__ == "__main__":
    main()
