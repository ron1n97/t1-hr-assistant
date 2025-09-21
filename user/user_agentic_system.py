"""
Пользовательская агентная система с поддержкой профиля и поиска материалов
"""
import logging
from typing import Annotated, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage

from config import Settings
from .profile_workflow import ProfileWorkflow
from .query_processor import UserQueryProcessor, QueryRouter
from .profile_api import load_user_profile, save_user_profile, create_empty_profile

logger = logging.getLogger(__name__)


class UserSystemState(TypedDict):
    messages: Annotated[list, add_messages]
    user_id: str
    profile_checked: bool
    profile_complete: bool
    current_mode: str  # "profile_setup", "profile_review", "normal_chat"
    extracted_data: Dict[str, Any]
    validation_errors: list


class UserRequestServer:
    settings = Settings()

    def __init__(self):
        self.llm = ChatOpenAI(
            model="Qwen2.5-72B-Instruct-AWQ",
            api_key=self.settings.scibox_api_key,
            base_url="https://llm.t1v.scibox.tech/v1",
            temperature=0.7,
            max_tokens=1024,
        )
        self.profile_workflow = ProfileWorkflow(self.llm)
        self.query_processor = UserQueryProcessor(self.llm)
        self.query_router = QueryRouter(self.query_processor)

    def process_user_request(self, request: str, user_id: str = "default") -> str:
        """Обрабатывает запрос пользователя с полным пайплайном"""
        logger.info(f"Обработка запроса пользователя {user_id}: {request[:100]}...")
        
        try:
            graph = self.build_graph()
            initial_state = UserSystemState(
                messages=[HumanMessage(content=request)],
                user_id=user_id,
                profile_checked=False,
                profile_complete=False,
                current_mode="",
                extracted_data={},
                validation_errors=[]
            )
            
            response = graph.invoke(initial_state)
            return response["messages"][-1].content
            
        except Exception as e:
            logger.error(f"Ошибка при обработке запроса: {e}")
            return "Произошла ошибка при обработке вашего запроса. Попробуйте еще раз."

    def build_graph(self) -> StateGraph:
        """Создает граф пользовательской системы"""
        graph_builder = StateGraph(UserSystemState)
        
        # Добавляем узлы
        graph_builder.add_node("check_profile_status", self.check_profile_status)
        graph_builder.add_node("route_request", self.route_request)
        graph_builder.add_node("handle_profile_setup", self.handle_profile_setup)
        graph_builder.add_node("handle_profile_review", self.handle_profile_review)
        graph_builder.add_node("handle_normal_chat", self.handle_normal_chat)
        
        # Добавляем рёбра
        graph_builder.add_edge(START, "check_profile_status")
        
        graph_builder.add_conditional_edges(
            "check_profile_status",
            self.route_after_profile_check,
            {
                "profile_setup": "handle_profile_setup",
                "profile_review": "handle_profile_review", 
                "normal_chat": "route_request"
            }
        )
        
        graph_builder.add_conditional_edges(
            "route_request",
            self.route_after_request_analysis,
            {
                "material_search": "handle_normal_chat",
                "general_question": "handle_normal_chat",
                "profile_related": "handle_profile_review"
            }
        )
        
        graph_builder.add_edge("handle_profile_setup", END)
        graph_builder.add_edge("handle_profile_review", END)
        graph_builder.add_edge("handle_normal_chat", END)
        
        return graph_builder.compile()

    def check_profile_status(self, state: UserSystemState) -> UserSystemState:
        """Проверяет статус профиля пользователя"""
        logger.info("Проверка статуса профиля пользователя")
        
        user_id = state["user_id"]
        profile = load_user_profile()
        
        if profile is None:
            # Профиль не существует - начинаем заполнение
            state["profile_checked"] = True
            state["profile_complete"] = False
            state["current_mode"] = "profile_setup"
            state["messages"].append(AIMessage(
                content="👋 Привет! Я помогу вам заполнить ваш профиль. "
                       "Это поможет мне давать более точные рекомендации и отвечать на ваши вопросы."
            ))
            logger.info("Профиль не найден, начинаем заполнение")
            
        elif not profile.is_complete():
            # Профиль существует, но не заполнен полностью
            # Всегда переходим в normal_chat, даже если профиль частично заполнен
            state["profile_checked"] = True
            state["profile_complete"] = True
            state["current_mode"] = "normal_chat"
            logger.info("Профиль частично заполнен, переходим к обычному режиму")
            
        else:
            # Профиль заполнен полностью
            state["profile_checked"] = True
            state["profile_complete"] = True
            state["current_mode"] = "normal_chat"
            logger.info("Профиль заполнен, переходим к обычному режиму")
        
        return state

    def route_request(self, state: UserSystemState) -> UserSystemState:
        """Анализирует запрос и определяет тип обработки"""
        logger.info("Анализ запроса пользователя")
        
        user_message = self._get_last_user_message(state)
        query_type = self.query_processor._classify_query(user_message)
        
        state["current_mode"] = query_type
        logger.info(f"Тип запроса определен: {query_type}")
        
        return state

    def handle_profile_setup(self, state: UserSystemState) -> UserSystemState:
        """Обрабатывает заполнение профиля"""
        logger.info("Обработка заполнения профиля")
        
        user_message = self._get_last_user_message(state)
        
        try:
            # Простое заполнение профиля без сложного workflow
            response = self._simple_profile_setup(user_message, state["user_id"])
            state["messages"].append(AIMessage(content=response))
            
        except Exception as e:
            logger.error(f"Ошибка при заполнении профиля: {e}")
            state["messages"].append(AIMessage(
                content="Произошла ошибка при обработке информации профиля. "
                       "Попробуйте еще раз или укажите информацию более подробно."
            ))
        
        return state

    def handle_profile_review(self, state: UserSystemState) -> UserSystemState:
        """Обрабатывает проверку и обновление профиля"""
        logger.info("Обработка проверки профиля")
        
        user_message = self._get_last_user_message(state)
        
        try:
            # Простая обработка вопросов о профиле
            response = self._simple_profile_review(user_message)
            state["messages"].append(AIMessage(content=response))
            
        except Exception as e:
            logger.error(f"Ошибка при проверке профиля: {e}")
            state["messages"].append(AIMessage(
                content="Произошла ошибка при обработке запроса о профиле. "
                       "Попробуйте еще раз."
            ))
        
        return state

    def handle_normal_chat(self, state: UserSystemState) -> UserSystemState:
        """Обрабатывает обычные запросы (поиск материалов, общие вопросы)"""
        logger.info("Обработка обычного запроса")
        
        user_message = self._get_last_user_message(state)
        
        try:
            # Простая обработка запросов
            response = self._simple_query_processing(user_message, state["user_id"])
            state["messages"].append(AIMessage(content=response))
            
        except Exception as e:
            logger.error(f"Ошибка при обработке обычного запроса: {e}")
            state["messages"].append(AIMessage(
                content="Произошла ошибка при обработке вашего запроса. "
                       "Попробуйте еще раз или переформулируйте вопрос."
            ))
        
        return state

    def route_after_profile_check(self, state: UserSystemState) -> str:
        """Определяет следующий шаг после проверки профиля"""
        mode = state["current_mode"]
        
        if mode == "profile_setup":
            return "profile_setup"
        elif mode == "profile_review":
            return "profile_review"
        else:
            return "normal_chat"

    def route_after_request_analysis(self, state: UserSystemState) -> str:
        """Определяет следующий шаг после анализа запроса"""
        mode = state["current_mode"]
        
        if mode == "material_search":
            return "material_search"
        elif mode == "profile_related":
            return "profile_related"
        else:
            return "general_question"

    async def process_user_request_async(self, request: str, user_id: str = "default") -> str:
        """Асинхронная версия обработки запроса"""
        logger.info(f"Асинхронная обработка запроса пользователя {user_id}: {request[:100]}...")
        
        try:
            graph = self.build_graph()
            initial_state = UserSystemState(
                messages=[HumanMessage(content=request)],
                user_id=user_id,
                profile_checked=False,
                profile_complete=False,
                current_mode="",
                extracted_data={},
                validation_errors=[]
            )
            
            response = await graph.ainvoke(initial_state)
            return response["messages"][-1].content
            
        except Exception as e:
            logger.error(f"Ошибка при асинхронной обработке запроса: {e}")
            return "Произошла ошибка при обработке вашего запроса. Попробуйте еще раз."

    def get_user_commands(self) -> Dict[str, str]:
        """Возвращает список доступных команд для пользователя"""
        return {
            "поиск материалов": "Найти учебные материалы по запросу",
            "рекомендации": "Получить персональные рекомендации",
            "профиль": "Информация о профиле пользователя",
            "заполнить профиль": "Начать заполнение профиля",
            "обновить профиль": "Обновить информацию в профиле",
            "помощь": "Показать доступные команды"
        }

    def get_profile_status(self, user_id: str = "default") -> Dict[str, Any]:
        """Возвращает статус профиля пользователя"""
        try:
            profile = load_user_profile()
            
            if profile is None:
                return {
                    "exists": False,
                    "complete": False,
                    "completion_percentage": 0.0,
                    "missing_fields": []
                }
            
            return {
                "exists": True,
                "complete": profile.is_complete(),
                "completion_percentage": profile.get_completion_percentage(),
                "missing_fields": self._get_missing_fields(profile)
            }
            
        except Exception as e:
            logger.error(f"Ошибка при получении статуса профиля: {e}")
            return {
                "exists": False,
                "complete": False,
                "completion_percentage": 0.0,
                "missing_fields": [],
                "error": str(e)
            }

    def _get_missing_fields(self, profile) -> list:
        """Получает список незаполненных полей профиля"""
        missing = []
        
        if not profile.basicInfo.department.strip():
            missing.append("department")
        if not profile.basicInfo.position.strip():
            missing.append("position")
        if not profile.basicInfo.grade.strip():
            missing.append("grade")
        if not profile.basicInfo.itExperience.strip():
            missing.append("itExperience")
        if not profile.currentRole.specialization.strip():
            missing.append("specialization")
        if not profile.currentRole.functionalRole.strip():
            missing.append("functionalRole")
        if not profile.education.institution.strip():
            missing.append("institution")
        if not profile.education.specialization.strip():
            missing.append("education_specialization")
        if not profile.education.graduationYear.strip():
            missing.append("graduationYear")
        
        return missing
    
    def _get_last_user_message(self, state: UserSystemState) -> str:
        """Получает последнее сообщение от пользователя"""
        logger.info(f"Всего сообщений в состоянии: {len(state['messages'])}")
        
        # Получаем последнее сообщение от пользователя (не от AI)
        for i, message in enumerate(reversed(state["messages"])):
            logger.info(f"Сообщение {i}: {type(message)} - {getattr(message, 'content', str(message))[:100]}...")
            
            if hasattr(message, 'type') and message.type == 'human':
                logger.info(f"Найдено сообщение от пользователя: {message.content[:100]}...")
                return message.content
            elif isinstance(message, dict) and message.get('role') == 'user':
                content = message.get('content', '')
                logger.info(f"Найдено сообщение от пользователя (dict): {content[:100]}...")
                return content
        
        # Fallback - берем последнее сообщение
        last_message = state["messages"][-1].content
        logger.info(f"Fallback - берем последнее сообщение: {last_message[:100]}...")
        return last_message
    
    def _simple_profile_setup(self, message: str, user_id: str) -> str:
        """Простое заполнение профиля без асинхронных вызовов"""
        logger.info("Простое заполнение профиля")
        
        # Загружаем или создаем профиль
        profile = load_user_profile()
        if profile is None:
            profile = create_empty_profile()
        
        # Простая обработка сообщения для заполнения профиля
        message_lower = message.lower()
        logger.info(f"Обрабатываем сообщение: '{message}'")
        
        # Проверяем, что пользователь хочет заполнить
        if any(word in message_lower for word in ["привет", "здравствуй", "начать", "заполнить"]):
            logger.info("Обнаружено приветствие, возвращаем инструкции")
            return ("👋 Привет! Я помогу вам заполнить ваш профиль. "
                   "Расскажите о себе: в каком подразделении работаете, "
                   "какая у вас должность, грейд и опыт работы в IT?")
        
        logger.info("Сообщение не является приветствием, пытаемся извлечь информацию")
        
        # Пытаемся извлечь информацию из сообщения
        extracted_info = self._extract_profile_info(message)
        logger.info(f"Извлеченная информация из '{message}': {extracted_info}")
        
        if extracted_info:
            # Обновляем профиль
            updated_fields = []
            if "department" in extracted_info:
                profile.basicInfo.department = extracted_info["department"]
                updated_fields.append(f"подразделение: {extracted_info['department']}")
            if "position" in extracted_info:
                profile.basicInfo.position = extracted_info["position"]
                updated_fields.append(f"должность: {extracted_info['position']}")
            if "grade" in extracted_info:
                profile.basicInfo.grade = extracted_info["grade"]
                updated_fields.append(f"грейд: {extracted_info['grade']}")
            if "experience" in extracted_info:
                profile.basicInfo.itExperience = extracted_info["experience"]
                updated_fields.append(f"опыт: {extracted_info['experience']}")
            if "specialization" in extracted_info:
                profile.currentRole.specialization = extracted_info["specialization"]
                updated_fields.append(f"специализация: {extracted_info['specialization']}")
            if "functional_role" in extracted_info:
                profile.currentRole.functionalRole = extracted_info["functional_role"]
                updated_fields.append(f"функциональная роль: {extracted_info['functional_role']}")
            
            # Сохраняем профиль
            logger.info(f"Пытаемся сохранить профиль с данными: {updated_fields}")
            if save_user_profile(profile):
                logger.info("Профиль успешно сохранен")
                
                # После первого успешного извлечения считаем профиль заполненным
                return (f"✅ Отлично! Ваш профиль создан: {', '.join(updated_fields)}. "
                       f"Теперь я могу помочь вам с поиском материалов, рекомендациями и ответами на вопросы!")
            else:
                return "Произошла ошибка при сохранении информации. Попробуйте еще раз."
        else:
            # Если не удалось извлечь информацию, даем более конкретные инструкции
            missing_fields = []
            if not profile.basicInfo.department.strip():
                missing_fields.append("подразделение/компанию")
            if not profile.basicInfo.position.strip():
                missing_fields.append("должность")
            if not profile.basicInfo.grade.strip():
                missing_fields.append("грейд")
            if not profile.basicInfo.itExperience.strip():
                missing_fields.append("опыт работы в IT")
            
            if missing_fields:
                return (f"Пожалуйста, укажите {', '.join(missing_fields)}. "
                       f"Например: 'Я работаю в Яндексе, фронтенд разработчиком, грейд Middle, опыт 5 лет'")
            else:
                # Если все основные поля заполнены, переходим к следующему этапу
                completion = profile.get_completion_percentage()
                if completion >= 50:
                    return (f"Профиль заполнен на {completion:.1f}%. "
                           f"Теперь расскажите о вашей специализации и функциональной роли.")
                else:
                    return "Информация не распознана. Попробуйте указать данные в формате: 'Я работаю в [компания], [должность], грейд [уровень], опыт [количество] лет'"
    
    def _simple_profile_review(self, message: str) -> str:
        """Простая обработка вопросов о профиле"""
        logger.info("Простая обработка вопросов о профиле")
        
        profile = load_user_profile()
        if not profile:
            return "Ваш профиль не заполнен. Давайте заполним его вместе!"
        
        # Генерируем описание профиля
        profile_info = f"""
**Ваш профиль:**
- Подразделение: {profile.basicInfo.department}
- Должность: {profile.basicInfo.position}
- Грейд: {profile.basicInfo.grade}
- Опыт в IT: {profile.basicInfo.itExperience}
- Специализация: {profile.currentRole.specialization}
- Функциональная роль: {profile.currentRole.functionalRole}
- Образование: {profile.education.institution}, {profile.education.specialization}
- Заполнение: {profile.get_completion_percentage():.1f}%
"""
        
        return profile_info.strip()
    
    def _simple_query_processing(self, message: str, user_id: str) -> str:
        """Простая обработка запросов"""
        logger.info("Простая обработка запросов")
        
        # Сначала пытаемся обновить профиль из сообщения
        profile = load_user_profile()
        if profile:
            extracted_info = self._extract_profile_info(message)
            if extracted_info:
                # Обновляем профиль
                updated_fields = []
                if "department" in extracted_info:
                    profile.basicInfo["department"] = extracted_info["department"]
                    updated_fields.append(f"подразделение: {extracted_info['department']}")
                if "position" in extracted_info:
                    profile.basicInfo["position"] = extracted_info["position"]
                    updated_fields.append(f"должность: {extracted_info['position']}")
                if "grade" in extracted_info:
                    profile.basicInfo["grade"] = extracted_info["grade"]
                    updated_fields.append(f"грейд: {extracted_info['grade']}")
                if "experience" in extracted_info:
                    profile.basicInfo["itExperience"] = extracted_info["experience"]
                    updated_fields.append(f"опыт: {extracted_info['experience']}")
                if "specialization" in extracted_info:
                    profile.currentRole["specialization"] = extracted_info["specialization"]
                    updated_fields.append(f"специализация: {extracted_info['specialization']}")
                if "functional_role" in extracted_info:
                    profile.currentRole["functionalRole"] = extracted_info["functional_role"]
                    updated_fields.append(f"функциональная роль: {extracted_info['functional_role']}")
                
                if updated_fields:
                    save_user_profile(profile)
                    logger.info(f"Профиль обновлен: {', '.join(updated_fields)}")
        
        message_lower = message.lower()
        
        # Проверяем тип запроса
        if any(word in message_lower for word in ["найди", "поиск", "ищу", "покажи", "материалы", "курсы", "какие"]):
            return self._handle_material_search_simple(message)
        elif any(word in message_lower for word in ["рекомендуй", "посоветуй", "что изучить"]):
            return self._handle_recommendations_simple()
        else:
            return self._handle_general_question_simple(message)
    
    def _handle_material_search_simple(self, query: str) -> str:
        """Простой поиск материалов"""
        from .material_search import MaterialSearchEngine
        
        search_engine = MaterialSearchEngine(self.llm)
        
        # Если запрос общий (типа "какие материалы доступны"), показываем все
        query_lower = query.lower()
        if any(word in query_lower for word in ["какие", "доступны", "есть", "покажи все", "список"]):
            materials = search_engine.materials
        else:
            materials = search_engine.search_materials(query)
        
        if not materials:
            return "К сожалению, по вашему запросу ничего не найдено. Попробуйте изменить поисковые термины."
        
        response = f"Найдено {len(materials)} материалов по запросу '{query}':\n\n"
        
        for i, material in enumerate(materials[:5], 1):
            response += f"{i}. **{material.title}**\n"
            response += f"   📝 {material.description}\n"
            response += f"   🏷️ {material.category} | ⭐ {material.rating} | ⏱️ {material.duration}\n"
            response += f"   📊 Уровень: {material.level.value} | Тип: {material.type.value}\n\n"
        
        if len(materials) > 5:
            response += f"... и еще {len(materials) - 5} материалов."
        
        return response
    
    def _handle_recommendations_simple(self) -> str:
        """Простые рекомендации"""
        from .material_search import MaterialSearchEngine
        
        search_engine = MaterialSearchEngine(self.llm)
        recommendations = search_engine.get_recommendations("default", limit=5)
        
        if not recommendations:
            return "Не удалось сформировать персональные рекомендации. Заполните профиль для получения более точных рекомендаций."
        
        response = "🎯 **Персональные рекомендации для вас:**\n\n"
        
        for i, material in enumerate(recommendations, 1):
            response += f"{i}. **{material.title}**\n"
            response += f"   📝 {material.description}\n"
            response += f"   🏷️ {material.category} | ⭐ {material.rating} | ⏱️ {material.duration}\n"
            response += f"   📊 Уровень: {material.level.value} | Тип: {material.type.value}\n\n"
        
        return response
    
    def _handle_general_question_simple(self, message: str) -> str:
        """Простая обработка общих вопросов"""
        profile = load_user_profile()
        
        if profile:
            profile_context = f"""
Информация о пользователе:
- Должность: {profile.basicInfo.position}
- Специализация: {profile.currentRole.specialization}
- Опыт в IT: {profile.basicInfo.itExperience}
"""
        else:
            profile_context = "Профиль пользователя не заполнен."
        
        # Простой ответ с учетом профиля
        return (f"Я понимаю ваш вопрос. {profile_context}\n\n"
               "Вы можете:\n"
               "• Найти учебные материалы (например: 'найди курсы по системному анализу')\n"
               "• Получить рекомендации ('посоветуй что изучить')\n"
               "• Заполнить профиль для персонализированных ответов")
    
    def _extract_profile_info(self, message: str) -> dict:
        """Извлекает информацию профиля из сообщения"""
        logger.info(f"Начинаем извлечение информации из: '{message}'")
        info = {}
        message_lower = message.lower()
        
        # Улучшенное извлечение информации
        import re
        
        # Извлекаем подразделение/компанию
        logger.info("Пытаемся извлечь подразделение/компанию")
        if any(word in message_lower for word in ["работаю", "в", "компании", "отдел", "подразделение", "отделении"]):
            logger.info("Найдены ключевые слова для подразделения")
            # Ищем паттерны типа "работаю в яндексе", "в отделе разработки", "в отделении поддержки"
            patterns = [
                r"работаю\s+в\s+([а-яё\w\s]+?)(?:\s|$|,|\.)",
                r"в\s+([а-яё\w\s]+?)(?:\s+отдел|\s+подразделение|\s+департамент|\s+отделении)",
                r"отделении\s+([а-яё\w\s]+?)(?:\s|$|,|\.)",
                r"отдел\s+([а-яё\w\s]+?)(?:\s|$|,|\.)",
                r"подразделение\s+([а-яё\w\s]+?)(?:\s|$|,|\.)"
            ]
            
            for i, pattern in enumerate(patterns):
                match = re.search(pattern, message_lower)
                if match:
                    department = match.group(1).strip()
                    logger.info(f"Паттерн {i+1} найден: '{department}'")
                    if len(department) > 2:  # Минимальная длина
                        info["department"] = department
                        logger.info(f"Подразделение сохранено: '{department}'")
                        break
        
        # Извлекаем должность
        if any(word in message_lower for word in ["разработчик", "аналитик", "менеджер", "дизайнер", "тестировщик"]):
            # Ищем должности
            position_patterns = [
                r"([а-яё\w\s\-]*?(?:разработчик|аналитик|менеджер|дизайнер|тестировщик|инженер))",
                r"должность\s+([а-яё\w\s\-]+?)(?:\s|$|,|\.)",
                r"позиция\s+([а-яё\w\s\-]+?)(?:\s|$|,|\.)",
                r"(?:я\s+)?([a-z]+\s+[а-яё\w\s\-]*?(?:разработчик|аналитик|менеджер|дизайнер|тестировщик|инженер))"
            ]
            
            for pattern in position_patterns:
                match = re.search(pattern, message_lower)
                if match:
                    position = match.group(1).strip()
                    if len(position) > 2:
                        info["position"] = position
                        break
        
        # Извлекаем грейд
        grade_patterns = [
            r"грейд\s*[:\-]?\s*([a-z0-9к]+)",
            r"уровень\s*[:\-]?\s*([a-z0-9к]+)",
            r"([a-z0-9к]+)\s+уровень",
            r"([a-z0-9к]+)\s+грейд"
        ]
        
        for pattern in grade_patterns:
            match = re.search(pattern, message_lower)
            if match:
                grade = match.group(1).strip()
                if len(grade) > 0:
                    info["grade"] = grade
                    break
        
        # Извлекаем опыт работы
        experience_patterns = [
            r"опыт\s+работы\s+в\s+it\s*[:\-]?\s*(\d+)\s*(?:лет|год|года)",
            r"опыт\s+в\s+it\s*[:\-]?\s*(\d+)\s*(?:лет|год|года)",
            r"работаю\s+в\s+it\s*[:\-]?\s*(\d+)\s*(?:лет|год|года)",
            r"(\d+)\s*(?:лет|год|года)\s*опыта",
            r"(\d+)\s*(?:лет|год|года)\s*в\s+it"
        ]
        
        for pattern in experience_patterns:
            match = re.search(pattern, message_lower)
            if match:
                years = match.group(1)
                info["experience"] = f"{years} лет"
                break
        
        # Если не нашли опыт, но есть число лет
        if "experience" not in info:
            years_match = re.search(r"(\d+)\s*(?:лет|год|года)", message_lower)
            if years_match:
                years = years_match.group(1)
                info["experience"] = f"{years} лет"
        
        # Извлекаем специализацию
        if any(word in message_lower for word in ["специализируюсь", "специализация", "работаю в области"]):
            specialization_patterns = [
                r"специализируюсь\s+на\s+([а-яё\w\s\-]+?)(?:\s|$|,|\.)",
                r"специализация\s*[:\-]?\s*([а-яё\w\s\-]+?)(?:\s|$|,|\.)",
                r"работаю\s+в\s+области\s+([а-яё\w\s\-]+?)(?:\s|$|,|\.)"
            ]
            
            for pattern in specialization_patterns:
                match = re.search(pattern, message_lower)
                if match:
                    specialization = match.group(1).strip()
                    if len(specialization) > 2:
                        info["specialization"] = specialization
                        break
        
        # Извлекаем функциональную роль
        if any(word in message_lower for word in ["функциональная роль", "роль", "я"]):
            role_patterns = [
                r"функциональная\s+роль\s*[:\-]?\s*([а-яё\w\s\-]+?)(?:\s|$|,|\.)",
                r"роль\s*[:\-]?\s*([а-яё\w\s\-]+?)(?:\s|$|,|\.)",
                r"я\s+([а-яё\w\s\-]*?(?:программист|аналитик|менеджер|дизайнер|тестировщик|инженер))"
            ]
            
            for pattern in role_patterns:
                match = re.search(pattern, message_lower)
                if match:
                    role = match.group(1).strip()
                    if len(role) > 2:
                        info["functional_role"] = role
                        break
        
        logger.info(f"Извлеченная информация: {info}")
        return info
