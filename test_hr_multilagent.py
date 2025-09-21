#!/usr/bin/env python3
"""
Тест для проверки мультиагентной HR системы
"""

import asyncio
import httpx
import json

# URL сервера
BASE_URL = "http://localhost:8000"

async def test_candidate_search():
    """Тестирует поиск кандидатов"""
    test_queries = [
        "Найди мне frontend разработчика с опытом React",
        "Ищу Python разработчика для backend",
        "Нужен DevOps инженер с опытом Kubernetes",
        "Покажи всех кандидатов на позицию Product Manager",
        "Найди разработчика с зарплатой до 200000 рублей"
    ]
    
    print("🔍 Тестирование поиска кандидатов")
    print("=" * 50)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Запрос: {query}")
            
            try:
                response = await client.post(
                    f"{BASE_URL}/chat/hr",
                    json={"message": query}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Ответ получен за {result.get('processing_time', 0):.2f}с")
                    print(f"Ответ: {result.get('response', '')[:200]}...")
                else:
                    print(f"❌ Ошибка: {response.status_code}")
                    print(f"Детали: {response.text}")
                    
            except Exception as e:
                print(f"❌ Ошибка: {e}")

async def test_general_questions():
    """Тестирует общие HR вопросы"""
    test_queries = [
        "Расскажи о политике отпусков в компании",
        "Какие документы нужны для оформления нового сотрудника?",
        "Как проходит процесс адаптации новых сотрудников?",
        "Какие есть льготы для сотрудников?",
        "Расскажи о корпоративной культуре"
    ]
    
    print("\n\n💼 Тестирование общих HR вопросов")
    print("=" * 50)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Запрос: {query}")
            
            try:
                response = await client.post(
                    f"{BASE_URL}/chat/hr",
                    json={"message": query}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Ответ получен за {result.get('processing_time', 0):.2f}с")
                    print(f"Ответ: {result.get('response', '')[:200]}...")
                else:
                    print(f"❌ Ошибка: {response.status_code}")
                    print(f"Детали: {response.text}")
                    
            except Exception as e:
                print(f"❌ Ошибка: {e}")

async def test_health_check():
    """Проверяет доступность сервера"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                print("✅ Сервер доступен")
                return True
            else:
                print(f"❌ Сервер недоступен: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Ошибка подключения к серверу: {e}")
        return False

async def test_agents_info():
    """Проверяет информацию об агентах"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{BASE_URL}/agents")
            if response.status_code == 200:
                result = response.json()
                print("✅ Информация об агентах получена")
                print(f"Доступно агентов: {result.get('total_agents', 0)}")
                for agent in result.get('agents', []):
                    print(f"  - {agent.get('agent_type', 'Unknown')}: {agent.get('model', 'Unknown')}")
                return True
            else:
                print(f"❌ Ошибка получения информации об агентах: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

async def main():
    """Основная функция тестирования"""
    print("🧪 Тестирование мультиагентной HR системы")
    print("=" * 60)
    
    # Проверяем доступность сервера
    if not await test_health_check():
        print("\n❌ Сервер недоступен. Запустите сервер командой:")
        print("   uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
        return
    
    # Проверяем информацию об агентах
    await test_agents_info()
    
    # Тестируем поиск кандидатов
    await test_candidate_search()
    
    # Тестируем общие вопросы
    await test_general_questions()
    
    print("\n\n🎉 Тестирование завершено!")

if __name__ == "__main__":
    asyncio.run(main())
