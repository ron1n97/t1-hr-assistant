"""
Обработчик запросов пользователя с учетом профиля
"""
import logging
from typing import Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from .profile_schema import UserProfile
from .profile_api import load_user_profile
from .material_search import MaterialSearchEngine, MaterialSearchAssistant

logger = logging.getLogger(__name__)


class UserQueryProcessor:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.search_engine = MaterialSearchEngine(llm)
        self.search_assistant = MaterialSearchAssistant(self.search_engine, llm)
    
    async def process_query(self, query: str, user_id: str = "default") -> str:
        """Обрабатывает запрос пользователя с учетом его профиля"""
        logger.info(f"Обработка запроса пользователя: {query[:100]}...")
        
        # Загружаем профиль пользователя
        profile = load_user_profile()
        
        # Определяем тип запроса
        query_type = self._classify_query(query)
        logger.info(f"Тип запроса: {query_type}")
        
        if query_type == "material_search":
            return await self._handle_material_search(query, user_id)
        elif query_type == "profile_related":
            return await self._handle_profile_related_query(query, profile)
        elif query_type == "general_question":
            return await self._handle_general_question(query, profile)
        else:
            return await self._handle_unknown_query(query)
    
    def _classify_query(self, query: str) -> str:
        """Классифицирует тип запроса пользователя"""
        query_lower = query.lower()
        
        # Ключевые слова для поиска материалов
        material_keywords = [
            "найди", "поиск", "ищу", "покажи", "материалы", "курсы", 
            "видео", "книги", "статьи", "обучение", "изучение", "рекомендуй",
            "посоветуй", "что изучить", "с чего начать"
        ]
        
        # Ключевые слова для вопросов о профиле
        profile_keywords = [
            "профиль", "анкета", "информация обо мне", "мои данные",
            "специализация", "опыт", "навыки", "компетенции", "образование"
        ]
        
        if any(keyword in query_lower for keyword in material_keywords):
            return "material_search"
        elif any(keyword in query_lower for keyword in profile_keywords):
            return "profile_related"
        else:
            return "general_question"
    
    async def _handle_material_search(self, query: str, user_id: str) -> str:
        """Обрабатывает запросы на поиск материалов"""
        logger.info("Обработка запроса на поиск материалов")
        return await self.search_assistant.process_search_request(query, user_id)
    
    async def _handle_profile_related_query(self, query: str, profile: Optional[UserProfile]) -> str:
        """Обрабатывает вопросы о профиле пользователя"""
        logger.info("Обработка вопроса о профиле")
        
        if not profile:
            return "Ваш профиль не заполнен. Давайте заполним его вместе!"
        
        # Генерируем описание профиля для контекста
        profile_context = self._generate_profile_context(profile)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""Вы - помощник по работе с профилем пользователя.

Информация о профиле пользователя:
{profile_context}

Отвечайте на вопросы пользователя о его профиле, используя эту информацию.
Если пользователь хочет изменить что-то в профиле, предложите ему это сделать."""),
            ("human", "{query}")
        ])
        
        chain = prompt | self.llm
        response = await chain.ainvoke({"query": query})
        
        return response.content
    
    async def _handle_general_question(self, query: str, profile: Optional[UserProfile]) -> str:
        """Обрабатывает общие вопросы с учетом профиля пользователя"""
        logger.info("Обработка общего вопроса")
        
        # Создаем контекст на основе профиля
        profile_context = ""
        if profile:
            profile_context = self._generate_profile_context(profile)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""Вы - помощник IT-специалиста. Отвечайте на вопросы, учитывая профиль пользователя.

Информация о пользователе:
{profile_context}

Используйте эту информацию для персонализации ответов и рекомендаций.
Если профиль не заполнен, предложите его заполнить для более точных рекомендаций."""),
            ("human", "{query}")
        ])
        
        chain = prompt | self.llm
        response = await chain.ainvoke({"query": query})
        
        return response.content
    
    async def _handle_unknown_query(self, query: str) -> str:
        """Обрабатывает неопознанные запросы"""
        logger.info("Обработка неопознанного запроса")
        
        return ("Я не совсем понял ваш запрос. Вы можете:\n"
                "• Найти учебные материалы (например: 'найди курсы по системному анализу')\n"
                "• Получить рекомендации ('посоветуй что изучить')\n"
                "• Задать вопрос о вашем профиле\n"
                "• Задать общий вопрос по IT-тематике")
    
    def _generate_profile_context(self, profile: UserProfile) -> str:
        """Генерирует контекст профиля для LLM"""
        context = f"""
**Основная информация:**
- Подразделение: {profile.basicInfo.department}
- Должность: {profile.basicInfo.position}
- Грейд: {profile.basicInfo.grade}
- Опыт в IT: {profile.basicInfo.itExperience}

**Текущая роль:**
- Специализация: {profile.currentRole.specialization}
- Функциональная роль: {profile.currentRole.functionalRole}
- Обязанности: {', '.join(profile.currentRole.responsibilities[:3])}

**Образование:**
- Учебное заведение: {profile.education.institution}
- Специальность: {profile.education.specialization}
- Год окончания: {profile.education.graduationYear}

**Опыт работы:** {len(profile.workExperience)} позиций
"""
        
        if profile.workExperience:
            context += "\n**Последний опыт работы:**\n"
            latest_exp = profile.workExperience[0]
            context += f"- Должность: {latest_exp.position}\n"
            context += f"- Компания: {latest_exp.company}\n"
            context += f"- Период: {latest_exp.startDate} - {latest_exp.endDate}\n"
        
        if profile.competencies:
            context += f"\n**Основные компетенции:** {', '.join(profile.competencies[:5])}\n"
        
        if profile.programmingLanguages:
            context += f"\n**Языки программирования:** "
            prog_langs = [f"{lang.skill} ({lang.level})" for lang in profile.programmingLanguages[:3]]
            context += f"{', '.join(prog_langs)}\n"
        
        if profile.foreignLanguages:
            context += f"\n**Иностранные языки:** "
            foreign_langs = [f"{lang.language} ({lang.level})" for lang in profile.foreignLanguages]
            context += f"{', '.join(foreign_langs)}\n"
        
        return context.strip()


class QueryRouter:
    """Маршрутизатор запросов пользователя"""
    
    def __init__(self, query_processor: UserQueryProcessor):
        self.query_processor = query_processor
    
    async def route_query(self, query: str, user_id: str = "default") -> str:
        """Маршрутизирует запрос к соответствующему обработчику"""
        logger.info(f"Маршрутизация запроса: {query[:50]}...")
        
        try:
            response = await self.query_processor.process_query(query, user_id)
            logger.info("Запрос успешно обработан")
            return response
        except Exception as e:
            logger.error(f"Ошибка при обработке запроса: {e}")
            return "Произошла ошибка при обработке вашего запроса. Попробуйте еще раз."
    
    def get_available_commands(self) -> Dict[str, str]:
        """Возвращает список доступных команд"""
        return {
            "поиск материалов": "Найти учебные материалы по запросу",
            "рекомендации": "Получить персональные рекомендации",
            "профиль": "Информация о профиле пользователя",
            "помощь": "Показать доступные команды"
        }
