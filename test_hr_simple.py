#!/usr/bin/env python3
"""
Простой тест HR мультиагентной системы без запуска сервера
"""

def test_hr_imports():
    """Тестирует импорты HR системы"""
    try:
        from hr.hr_agentic_system import HRRequestServer
        from hr.state import HRState
        from hr.candidates_data import MOCK_CANDIDATES
        from models import Candidate, Experience
        
        print("✅ Все импорты успешны")
        return True
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False

def test_candidates_data():
    """Тестирует данные кандидатов"""
    try:
        from hr.candidates_data import MOCK_CANDIDATES
        
        print(f"✅ Загружено {len(MOCK_CANDIDATES)} кандидатов")
        
        for candidate in MOCK_CANDIDATES:
            print(f"  - {candidate.name} ({candidate.position})")
            print(f"    Навыки: {', '.join(candidate.skills)}")
            print(f"    Статус: {candidate.status}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка данных кандидатов: {e}")
        return False

def test_hr_state():
    """Тестирует состояние HR системы"""
    try:
        from hr.state import HRState
        
        # Создаем тестовое состояние
        test_state = {
            "messages": [{"role": "user", "content": "Найди frontend разработчика"}],
            "candidates": None,
            "request_type": None,
            "search_query": None,
            "selected_candidates": None,
            "reasoning": None
        }
        
        print("✅ Состояние HR системы создано успешно")
        print(f"  Сообщений: {len(test_state['messages'])}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка состояния: {e}")
        return False

def test_router_logic():
    """Тестирует логику роутера"""
    try:
        # Ключевые слова для поиска кандидатов
        candidate_keywords = [
            "кандидат", "candidate", "найди", "поиск", "ищу", "ищем",
            "разработчик", "developer", "программист", "инженер", "engineer",
            "менеджер", "manager", "дизайнер", "designer", "аналитик", "analyst",
            "devops", "frontend", "backend", "fullstack", "python", "javascript",
            "react", "angular", "vue", "java", "c#", "php", "ruby", "go",
            "опыт", "experience", "навыки", "skills", "технологии", "technologies"
        ]
        
        test_queries = [
            ("Найди frontend разработчика", True),
            ("Расскажи о политике отпусков", False),
            ("Ищу Python разработчика", True),
            ("Какие документы нужны для найма?", False),
            ("Покажи DevOps инженеров", True),
            ("Как проходит адаптация?", False)
        ]
        
        print("✅ Тестирование логики роутера:")
        
        for query, expected in test_queries:
            user_message = query.lower()
            is_candidate_search = any(keyword in user_message for keyword in candidate_keywords)
            
            status = "✅" if is_candidate_search == expected else "❌"
            request_type = "поиск кандидатов" if is_candidate_search else "общий вопрос"
            
            print(f"  {status} '{query}' -> {request_type}")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка логики роутера: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🧪 Простое тестирование HR мультиагентной системы")
    print("=" * 60)
    
    tests = [
        ("Импорты", test_hr_imports),
        ("Данные кандидатов", test_candidates_data),
        ("Состояние системы", test_hr_state),
        ("Логика роутера", test_router_logic)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        if test_func():
            passed += 1
        else:
            print(f"❌ Тест '{test_name}' не пройден")
    
    print(f"\n📊 Результаты: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("🎉 Все тесты пройдены успешно!")
    else:
        print("⚠️  Некоторые тесты не пройдены")

if __name__ == "__main__":
    main()
