"""
Тестирование пользовательской агентной системы
"""
import json
import logging
from user.user_agentic_system import UserRequestServer
from user.profile_api import load_user_profile, save_user_profile, create_empty_profile

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_profile_creation():
    """Тест создания профиля"""
    logger.info("=== Тест создания профиля ===")
    
    # Создаем пустой профиль
    profile = create_empty_profile()
    logger.info(f"Создан пустой профиль: {profile.get_completion_percentage():.1f}% заполнен")
    
    # Заполняем основную информацию
    profile.basicInfo.department = "Отдел разработки"
    profile.basicInfo.position = "Системный аналитик"
    profile.basicInfo.grade = "Middle"
    profile.basicInfo.itExperience = "3 года"
    
    # Заполняем текущую роль
    profile.currentRole.specialization = "Системный аналитик"
    profile.currentRole.functionalRole = "Аналитик требований"
    profile.currentRole.responsibilities = ["Анализ требований", "Создание ТЗ"]
    
    # Заполняем образование
    profile.education.institution = "МГУ им. М.В. Ломоносова"
    profile.education.degree = "master"
    profile.education.specialization = "Прикладная математика и информатика"
    profile.education.graduationYear = "2020"
    
    # Сохраняем профиль
    if save_user_profile(profile):
        logger.info("Профиль успешно сохранен")
    else:
        logger.error("Ошибка при сохранении профиля")
    
    # Проверяем загрузку
    loaded_profile = load_user_profile()
    if loaded_profile:
        logger.info(f"Профиль загружен: {loaded_profile.get_completion_percentage():.1f}% заполнен")
        logger.info(f"Профиль полный: {loaded_profile.is_complete()}")
    else:
        logger.error("Ошибка при загрузке профиля")


def test_user_system():
    """Тест пользовательской системы"""
    logger.info("=== Тест пользовательской системы ===")
    
    # Создаем экземпляр системы
    user_system = UserRequestServer()
    
    # Тест 1: Запрос без профиля
    logger.info("Тест 1: Запрос без профиля")
    response = user_system.process_user_request("Привет! Что ты умеешь?", "test_user_1")
    logger.info(f"Ответ: {response}")
    
    # Тест 2: Запрос на поиск материалов
    logger.info("Тест 2: Поиск материалов")
    response = user_system.process_user_request("Найди курсы по системному анализу", "test_user_2")
    logger.info(f"Ответ: {response}")
    
    # Тест 3: Запрос рекомендаций
    logger.info("Тест 3: Рекомендации")
    response = user_system.process_user_request("Посоветуй что изучить", "test_user_3")
    logger.info(f"Ответ: {response}")
    
    # Тест 4: Вопрос о профиле
    logger.info("Тест 4: Вопрос о профиле")
    response = user_system.process_user_request("Расскажи о моем профиле", "test_user_4")
    logger.info(f"Ответ: {response}")


def test_profile_workflow():
    """Тест пайплайна заполнения профиля"""
    logger.info("=== Тест пайплайна заполнения профиля ===")
    
    user_system = UserRequestServer()
    
    # Тест заполнения основной информации
    logger.info("Тест заполнения основной информации")
    response = user_system.process_user_request(
        "Я работаю в отделе разработки, должность системный аналитик, грейд Middle, опыт в IT 3 года",
        "test_profile_1"
    )
    logger.info(f"Ответ: {response}")
    
    # Тест заполнения роли
    logger.info("Тест заполнения роли")
    response = user_system.process_user_request(
        "Моя специализация - системный аналитик, функциональная роль - аналитик требований, "
        "основные обязанности: анализ требований, создание технических заданий, взаимодействие с заказчиком",
        "test_profile_2"
    )
    logger.info(f"Ответ: {response}")


def test_material_search():
    """Тест поиска материалов"""
    logger.info("=== Тест поиска материалов ===")
    
    from user.material_search import MaterialSearchEngine
    from langchain_openai import ChatOpenAI
    from config import Settings
    
    settings = Settings()
    llm = ChatOpenAI(
        model="Qwen2.5-72B-Instruct-AWQ",
        api_key=settings.scibox_api_key,
        base_url="https://llm.t1v.scibox.tech/v1",
        temperature=0.7,
        max_tokens=512,
    )
    
    search_engine = MaterialSearchEngine(llm)
    
    # Тест поиска по запросу
    logger.info("Тест поиска по запросу 'системный анализ'")
    materials = search_engine.search_materials("системный анализ")
    logger.info(f"Найдено {len(materials)} материалов")
    for material in materials[:3]:
        logger.info(f"- {material.title} ({material.category})")
    
    # Тест получения рекомендаций
    logger.info("Тест получения рекомендаций")
    recommendations = search_engine.get_recommendations("test_user", limit=3)
    logger.info(f"Получено {len(recommendations)} рекомендаций")
    for rec in recommendations:
        logger.info(f"- {rec.title} (⭐ {rec.rating})")


def test_api_endpoints():
    """Тест API endpoints"""
    logger.info("=== Тест API endpoints ===")
    
    from user.profile_api import get_profile, get_all_materials, search_materials
    from user.profile_schema import MaterialSearchRequest
    
    # Тест получения профиля
    logger.info("Тест получения профиля")
    try:
        profile_response = get_profile()
        logger.info(f"Профиль получен: {profile_response.is_complete}")
    except Exception as e:
        logger.error(f"Ошибка при получении профиля: {e}")
    
    # Тест получения материалов
    logger.info("Тест получения всех материалов")
    try:
        materials_response = get_all_materials()
        logger.info(f"Получено {materials_response.total_count} материалов")
    except Exception as e:
        logger.error(f"Ошибка при получении материалов: {e}")
    
    # Тест поиска материалов
    logger.info("Тест поиска материалов")
    try:
        search_request = MaterialSearchRequest(query="системный анализ")
        search_response = search_materials(search_request)
        logger.info(f"Найдено {search_response.total_count} материалов по запросу")
    except Exception as e:
        logger.error(f"Ошибка при поиске материалов: {e}")


def main():
    """Основная функция тестирования"""
    logger.info("Запуск тестирования пользовательской системы")
    
    try:
        # Тест создания профиля
        test_profile_creation()
        
        # Тест пользовательской системы
        test_user_system()
        
        # Тест пайплайна профиля
        test_profile_workflow()
        
        # Тест поиска материалов
        test_material_search()
        
        # Тест API endpoints
        test_api_endpoints()
        
        logger.info("Все тесты завершены успешно!")
        
    except Exception as e:
        logger.error(f"Ошибка при выполнении тестов: {e}")


if __name__ == "__main__":
    main()
