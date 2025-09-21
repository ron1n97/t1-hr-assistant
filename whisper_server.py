#!/usr/bin/env python3
"""
Простой Whisper сервер для транскрипции аудио
"""

import os
import tempfile
import whisper
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

# Загружаем модель при запуске
model_name = os.getenv("WHISPER_MODEL", "large-v3")
print(f"Загружаем модель Whisper: {model_name}")
model = whisper.load_model(model_name)
print("Модель загружена успешно!")

@app.get("/health")
async def health():
    """Проверка здоровья сервера"""
    return {"status": "healthy", "model": model_name}

@app.post("/v1/audio/transcriptions")
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = Form("ru"),
    response_format: str = Form("json")
):
    """Транскрипция аудио файла"""
    try:
        print(f"Получен файл: {file.filename}, размер: {file.size}")
        
        # Сохраняем файл временно
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        print(f"Файл сохранен: {tmp_file_path}")
        
        # Транскрибируем
        print(f"Начинаем транскрипцию на языке: {language}")
        result = model.transcribe(tmp_file_path, language=language)
        
        # Удаляем временный файл
        os.unlink(tmp_file_path)
        
        print(f"Транскрипция завершена: {len(result['text'])} символов")
        
        return JSONResponse(content={"text": result["text"]})
        
    except Exception as e:
        print(f"Ошибка транскрипции: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

if __name__ == "__main__":
    print("Запуск Whisper сервера...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
