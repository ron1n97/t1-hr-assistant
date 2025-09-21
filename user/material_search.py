"""
Логика поиска и рекомендации учебных материалов
"""
import logging
from typing import List, Dict, Any, Optional
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from .profile_schema import Material, LEARNING_MATERIALS, MaterialType, MaterialLevel
from .profile_api import load_user_profile

logger = logging.getLogger(__name__)


class MaterialSearchEngine:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.materials = LEARNING_MATERIALS
    
    def search_materials(self, query: str, filters: Optional[Dict[str, Any]] = None) -> List[Material]:
        """Поиск материалов по запросу с фильтрами"""
        logger.info(f"Поиск материалов по запросу: {query}")
        
        if not query.strip():
            return self.materials
        
        query_lower = query.lower()
        results = []
        
        for material in self.materials:
            # Поиск по названию, описанию и категории
            if (query_lower in material.title.lower() or
                query_lower in material.description.lower() or
                query_lower in material.category.lower()):
                results.append(material)
        
        # Применяем фильтры
        if filters:
            results = self._apply_filters(results, filters)
        
        # Сортируем по рейтингу
        results.sort(key=lambda x: x.rating, reverse=True)
        
        logger.info(f"Найдено {len(results)} материалов")
        return results
    
    def get_recommendations(self, user_id: str = "default", limit: int = 5) -> List[Material]:
        """Получает персональные рекомендации на основе профиля пользователя"""
        logger.info(f"Получение рекомендаций для пользователя {user_id}")
        
        profile = load_user_profile()
        if not profile:
            # Если профиль не заполнен, возвращаем популярные материалы
            return self._get_popular_materials(limit)
        
        # Анализируем профиль для рекомендаций
        recommendations = []
        
        # Рекомендации на основе специализации
        specialization = profile.currentRole.specialization.lower()
        if specialization:
            specialization_materials = [
                m for m in self.materials
                if specialization in m.title.lower() or specialization in m.description.lower()
            ]
            recommendations.extend(specialization_materials[:2])
        
        # Рекомендации на основе компетенций
        competencies = profile.competencies
        if competencies:
            competency_materials = []
            for comp in competencies[:3]:  # Берем первые 3 компетенции
                for material in self.materials:
                    if any(word in material.description.lower() for word in comp.lower().split()):
                        competency_materials.append(material)
            recommendations.extend(competency_materials[:2])
        
        # Рекомендации на основе языков программирования
        prog_languages = [lang.skill.lower() for lang in profile.programmingLanguages]
        if prog_languages:
            for lang in prog_languages[:2]:  # Берем первые 2 языка
                lang_materials = [
                    m for m in self.materials
                    if lang in m.title.lower() or lang in m.description.lower()
                ]
                recommendations.extend(lang_materials[:1])
        
        # Рекомендации на основе уровня опыта
        experience_level = self._determine_experience_level(profile)
        level_materials = [
            m for m in self.materials
            if m.level.value == experience_level
        ]
        recommendations.extend(level_materials[:2])
        
        # Убираем дубликаты и ограничиваем количество
        unique_recommendations = []
        seen_ids = set()
        for material in recommendations:
            if material.id not in seen_ids:
                unique_recommendations.append(material)
                seen_ids.add(material.id)
        
        # Сортируем по рейтингу
        unique_recommendations.sort(key=lambda x: x.rating, reverse=True)
        
        result = unique_recommendations[:limit]
        logger.info(f"Сформировано {len(result)} рекомендаций")
        return result
    
    def get_materials_by_category(self, category: str) -> List[Material]:
        """Получает материалы по категории"""
        logger.info(f"Получение материалов по категории: {category}")
        
        category_materials = [
            m for m in self.materials
            if m.category.lower() == category.lower()
        ]
        
        category_materials.sort(key=lambda x: x.rating, reverse=True)
        return category_materials
    
    def get_materials_by_level(self, level: MaterialLevel) -> List[Material]:
        """Получает материалы по уровню сложности"""
        logger.info(f"Получение материалов по уровню: {level}")
        
        level_materials = [
            m for m in self.materials
            if m.level == level
        ]
        
        level_materials.sort(key=lambda x: x.rating, reverse=True)
        return level_materials
    
    def get_materials_by_type(self, material_type: MaterialType) -> List[Material]:
        """Получает материалы по типу"""
        logger.info(f"Получение материалов по типу: {material_type}")
        
        type_materials = [
            m for m in self.materials
            if m.type == material_type
        ]
        
        type_materials.sort(key=lambda x: x.rating, reverse=True)
        return type_materials
    
    def get_available_categories(self) -> List[str]:
        """Получает список доступных категорий"""
        categories = list(set(m.category for m in self.materials))
        categories.sort()
        return categories
    
    def get_available_levels(self) -> List[str]:
        """Получает список доступных уровней"""
        return [level.value for level in MaterialLevel]
    
    def get_available_types(self) -> List[str]:
        """Получает список доступных типов материалов"""
        return [material_type.value for material_type in MaterialType]
    
    def _apply_filters(self, materials: List[Material], filters: Dict[str, Any]) -> List[Material]:
        """Применяет фильтры к списку материалов"""
        filtered_materials = materials.copy()
        
        if "category" in filters and filters["category"]:
            filtered_materials = [
                m for m in filtered_materials
                if m.category.lower() == filters["category"].lower()
            ]
        
        if "level" in filters and filters["level"]:
            filtered_materials = [
                m for m in filtered_materials
                if m.level.value == filters["level"]
            ]
        
        if "type" in filters and filters["type"]:
            filtered_materials = [
                m for m in filtered_materials
                if m.type.value == filters["type"]
            ]
        
        if "min_rating" in filters and filters["min_rating"]:
            filtered_materials = [
                m for m in filtered_materials
                if m.rating >= filters["min_rating"]
            ]
        
        return filtered_materials
    
    def _get_popular_materials(self, limit: int) -> List[Material]:
        """Получает популярные материалы (с высоким рейтингом)"""
        popular = sorted(self.materials, key=lambda x: x.rating, reverse=True)
        return popular[:limit]
    
    def _determine_experience_level(self, profile) -> str:
        """Определяет уровень опыта пользователя на основе профиля"""
        it_experience = profile.basicInfo.itExperience.lower()
        
        # Анализируем опыт работы
        if "год" in it_experience or "лет" in it_experience:
            if any(word in it_experience for word in ["1", "один", "два", "2"]):
                return MaterialLevel.BEGINNER.value
            elif any(word in it_experience for word in ["3", "три", "4", "четыре", "5", "пять"]):
                return MaterialLevel.INTERMEDIATE.value
            else:
                return MaterialLevel.ADVANCED.value
        
        # Анализируем грейд
        grade = profile.basicInfo.grade.lower()
        if any(word in grade for word in ["junior", "младший", "начальный"]):
            return MaterialLevel.BEGINNER.value
        elif any(word in grade for word in ["middle", "средний", "middle"]):
            return MaterialLevel.INTERMEDIATE.value
        elif any(word in grade for word in ["senior", "старший", "ведущий"]):
            return MaterialLevel.ADVANCED.value
        
        # По умолчанию - начальный уровень
        return MaterialLevel.BEGINNER.value


class MaterialSearchAssistant:
    def __init__(self, search_engine: MaterialSearchEngine, llm: ChatOpenAI):
        self.search_engine = search_engine
        self.llm = llm
    
    async def process_search_request(self, query: str, user_id: str = "default") -> str:
        """Обрабатывает запрос на поиск материалов"""
        logger.info(f"Обработка запроса на поиск: {query}")
        
        # Определяем тип запроса
        if self._is_search_request(query):
            return await self._handle_search(query, user_id)
        elif self._is_recommendation_request(query):
            return await self._handle_recommendations(user_id)
        else:
            return await self._handle_general_query(query, user_id)
    
    def _is_search_request(self, query: str) -> bool:
        """Определяет, является ли запрос поисковым"""
        search_keywords = [
            "найди", "поиск", "ищу", "покажи", "материалы", "курсы", 
            "видео", "книги", "статьи", "обучение", "изучение"
        ]
        return any(keyword in query.lower() for keyword in search_keywords)
    
    def _is_recommendation_request(self, query: str) -> bool:
        """Определяет, является ли запрос запросом рекомендаций"""
        rec_keywords = [
            "рекомендуй", "посоветуй", "что изучить", "с чего начать",
            "подходящие", "для меня", "персональные"
        ]
        return any(keyword in query.lower() for keyword in rec_keywords)
    
    async def _handle_search(self, query: str, user_id: str) -> str:
        """Обрабатывает поисковый запрос"""
        # Извлекаем поисковые термины
        search_terms = self._extract_search_terms(query)
        
        # Выполняем поиск
        materials = self.search_engine.search_materials(search_terms)
        
        if not materials:
            return "К сожалению, по вашему запросу ничего не найдено. Попробуйте изменить поисковые термины."
        
        # Формируем ответ
        response = f"Найдено {len(materials)} материалов по запросу '{search_terms}':\n\n"
        
        for i, material in enumerate(materials[:5], 1):  # Показываем первые 5
            response += f"{i}. **{material.title}**\n"
            response += f"   📝 {material.description}\n"
            response += f"   🏷️ {material.category} | ⭐ {material.rating} | ⏱️ {material.duration}\n"
            response += f"   📊 Уровень: {material.level.value} | Тип: {material.type.value}\n\n"
        
        if len(materials) > 5:
            response += f"... и еще {len(materials) - 5} материалов."
        
        return response
    
    async def _handle_recommendations(self, user_id: str) -> str:
        """Обрабатывает запрос рекомендаций"""
        recommendations = self.search_engine.get_recommendations(user_id, limit=5)
        
        if not recommendations:
            return "Не удалось сформировать персональные рекомендации. Заполните профиль для получения более точных рекомендаций."
        
        response = "🎯 **Персональные рекомендации для вас:**\n\n"
        
        for i, material in enumerate(recommendations, 1):
            response += f"{i}. **{material.title}**\n"
            response += f"   📝 {material.description}\n"
            response += f"   🏷️ {material.category} | ⭐ {material.rating} | ⏱️ {material.duration}\n"
            response += f"   📊 Уровень: {material.level.value} | Тип: {material.type.value}\n\n"
        
        return response
    
    async def _handle_general_query(self, query: str, user_id: str) -> str:
        """Обрабатывает общий запрос о материалах"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Вы - помощник по поиску учебных материалов для IT-специалистов.

Доступные категории материалов:
- Системный анализ
- Моделирование  
- Бизнес-анализ
- Методологии
- Технические навыки
- Инструменты

Доступные типы материалов:
- Курсы
- Видео
- Книги
- Статьи

Доступные уровни:
- Начальный
- Средний
- Продвинутый

Помогите пользователю найти подходящие материалы или дайте совет по обучению."""),
            ("human", "{query}")
        ])
        
        chain = prompt | self.llm
        response = await chain.ainvoke({"query": query})
        
        return response.content
    
    def _extract_search_terms(self, query: str) -> str:
        """Извлекает поисковые термины из запроса"""
        # Убираем служебные слова
        stop_words = ["найди", "поиск", "ищу", "покажи", "материалы", "про", "для", "по"]
        
        words = query.lower().split()
        search_terms = [word for word in words if word not in stop_words]
        
        return " ".join(search_terms)
