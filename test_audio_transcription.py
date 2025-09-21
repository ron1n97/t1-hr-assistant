#!/usr/bin/env python3
"""
Тест для проверки интеграции аудио транскрипции
"""

import asyncio
import httpx
import tempfile
import os
from pathlib import Path

# URL сервера
BASE_URL = "http://localhost:8000"

async def test_audio_transcription():
    """Тестирует эндпоинт аудио транскрипции"""
    
    # Создаем простой тестовый аудио файл (заглушка)
    # В реальном тесте здесь должен быть настоящий аудио файл
    test_audio_content = b"fake audio content for testing"
    
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
        temp_file.write(test_audio_content)
        temp_file_path = temp_file.name
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Тестируем эндпоинт транскрипции
            with open(temp_file_path, 'rb') as audio_file:
                files = {
                    'file': ('test_audio.mp3', audio_file, 'audio/mpeg')
                }
                data = {
                    'agent_type': 'hr',
                    'conversation_id': 'test_session_123'
                }
                
                print("Отправка запроса на транскрипцию...")
                response = await client.post(
                    f"{BASE_URL}/audio/transcriptions",
                    files=files,
                    data=data
                )
                
                print(f"Статус ответа: {response.status_code}")
                print(f"Ответ: {response.text}")
                
                if response.status_code == 200:
                    result = response.json()
                    print("✅ Транскрипция успешна!")
                    print(f"Транскрибированный текст: {result.get('text', '')}")
                    print(f"Тип агента: {result.get('agent_type', '')}")
                    print(f"Время обработки: {result.get('processing_time', 0):.2f}с")
                    if result.get('chat_response'):
                        print(f"Ответ агента: {result['chat_response'].get('response', '')}")
                else:
                    print(f"❌ Ошибка: {response.status_code}")
                    print(f"Детали: {response.text}")
                    
    except httpx.ConnectError:
        print("❌ Не удалось подключиться к серверу. Убедитесь, что сервер запущен на http://localhost:8000")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        # Удаляем временный файл
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

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

async def main():
    """Основная функция тестирования"""
    print("🧪 Тестирование аудио транскрипции")
    print("=" * 50)
    
    # Проверяем доступность сервера
    if not await test_health_check():
        print("\n❌ Сервер недоступен. Запустите сервер командой:")
        print("   uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
        return
    
    print("\n🎵 Тестирование транскрипции аудио...")
    await test_audio_transcription()

if __name__ == "__main__":
    asyncio.run(main())
