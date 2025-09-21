#!/usr/bin/env python3
"""
Тест для проверки API транскрипции аудио
"""
import requests
import io
import wave

def create_test_audio():
    """Создает тестовый аудио файл"""
    # Создаем простой WAV файл с тишиной
    sample_rate = 44100
    duration = 2  # секунды
    samples = [0] * (sample_rate * duration)
    
    # Создаем WAV файл в памяти
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)  # моно
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(b''.join([int(sample).to_bytes(2, byteorder='little', signed=True) for sample in samples]))
    
    wav_buffer.seek(0)
    return wav_buffer.getvalue()

def test_audio_transcription():
    """Тест транскрипции аудио"""
    url = "http://localhost:8000/audio/transcriptions"
    
    # Создаем тестовый аудио файл
    audio_data = create_test_audio()
    
    # Подготавливаем данные для отправки
    files = {
        'file': ('test_audio.wav', audio_data, 'audio/wav')
    }
    data = {
        'agent_type': 'user',
        'conversation_id': 'test_audio_123'
    }
    
    try:
        print("🎤 Отправляем тестовый аудио файл на транскрипцию...")
        response = requests.post(url, files=files, data=data, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Транскрипция успешна!")
            print(f"📝 Транскрибированный текст: {result['text']}")
            print(f"🤖 Тип агента: {result['agent_type']}")
            print(f"⏱️ Время обработки: {result['processing_time']:.2f}с")
            
            if result.get('chat_response'):
                print(f"💬 Ответ агента: {result['chat_response']['response'][:100]}...")
            
            return True
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(f"📄 Ответ: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка сети: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

def test_hr_audio_transcription():
    """Тест транскрипции аудио для HR агента"""
    url = "http://localhost:8000/audio/transcriptions"
    
    # Создаем тестовый аудио файл
    audio_data = create_test_audio()
    
    # Подготавливаем данные для отправки
    files = {
        'file': ('test_hr_audio.wav', audio_data, 'audio/wav')
    }
    data = {
        'agent_type': 'hr',
        'conversation_id': 'test_hr_audio_456'
    }
    
    try:
        print("\n🎤 Отправляем тестовый аудио файл для HR агента...")
        response = requests.post(url, files=files, data=data, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ HR транскрипция успешна!")
            print(f"📝 Транскрибированный текст: {result['text']}")
            print(f"🤖 Тип агента: {result['agent_type']}")
            print(f"⏱️ Время обработки: {result['processing_time']:.2f}с")
            
            if result.get('chat_response'):
                print(f"💬 Ответ HR агента: {result['chat_response']['response'][:100]}...")
            
            return True
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(f"📄 Ответ: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка сети: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

if __name__ == "__main__":
    print("🔊 Тестирование API транскрипции аудио...")
    print("=" * 50)
    
    user_ok = test_audio_transcription()
    hr_ok = test_hr_audio_transcription()
    
    print("\n" + "=" * 50)
    if user_ok and hr_ok:
        print("🎉 Все тесты аудио API прошли успешно!")
    else:
        print("❌ Есть проблемы с аудио API")
