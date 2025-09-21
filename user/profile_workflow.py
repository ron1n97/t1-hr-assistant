"""
LangGraph пайплайн для проверки и заполнения профиля пользователя
"""
import json
import logging
from typing import Dict, Any, List, Optional, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from .profile_schema import (
    UserProfile, BasicInfo, CurrentRole, Education, WorkExperience,
    LanguageSkill, TechnicalSkill, AdditionalRole,
    TECHNICAL_SPECIALTIES, SKILLS_AND_COMPETENCIES, LANGUAGES,
    OTHER_TECHNICAL_SKILLS, PROGRAMMING_LANGUAGES
)
from .profile_api import load_user_profile, save_user_profile, create_empty_profile

logger = logging.getLogger(__name__)


class ProfileWorkflowState(TypedDict):
    messages: Annotated[List, add_messages]
    profile: Optional[UserProfile]
    current_step: str
    profile_complete: bool
    user_input: str
    extracted_data: Dict[str, Any]
    validation_errors: List[str]


class ProfileWorkflow:
    def __init__(self, llm: ChatOpenAI):
        self.llm = llm
        self.workflow = self._create_workflow()
    
    def _create_workflow(self) -> StateGraph:
        """Создает граф пайплайна для работы с профилем"""
        workflow = StateGraph(ProfileWorkflowState)
        
        # Добавляем узлы
        workflow.add_node("check_profile", self.check_profile)
        workflow.add_node("profile_complete", self.profile_complete)
        workflow.add_node("collect_basic_info", self.collect_basic_info)
        workflow.add_node("collect_current_role", self.collect_current_role)
        workflow.add_node("collect_education", self.collect_education)
        workflow.add_node("collect_work_experience", self.collect_work_experience)
        workflow.add_node("collect_skills", self.collect_skills)
        workflow.add_node("collect_languages", self.collect_languages)
        workflow.add_node("save_profile", self.save_profile)
        workflow.add_node("validate_profile", self.validate_profile)
        
        # Добавляем рёбра
        workflow.set_entry_point("check_profile")
        
        workflow.add_conditional_edges(
            "check_profile",
            self.route_after_check,
            {
                "complete": "profile_complete",
                "incomplete": "collect_basic_info"
            }
        )
        
        workflow.add_edge("collect_basic_info", "collect_current_role")
        workflow.add_edge("collect_current_role", "collect_education")
        workflow.add_edge("collect_education", "collect_work_experience")
        workflow.add_edge("collect_work_experience", "collect_skills")
        workflow.add_edge("collect_skills", "collect_languages")
        workflow.add_edge("collect_languages", "validate_profile")
        workflow.add_edge("validate_profile", "save_profile")
        workflow.add_edge("save_profile", END)
        workflow.add_edge("profile_complete", END)
        
        return workflow.compile()
    
    def check_profile(self, state: ProfileWorkflowState) -> ProfileWorkflowState:
        """Проверяет, заполнен ли профиль пользователя"""
        logger.info("Проверка профиля пользователя")
        
        profile = load_user_profile()
        
        if profile is None:
            logger.info("Профиль не найден, создаем новый")
            profile = create_empty_profile()
            state["profile"] = profile
            state["profile_complete"] = False
            state["current_step"] = "basic_info"
            state["messages"].append(AIMessage(
                content="Привет! Я помогу вам заполнить ваш профиль. "
                       "Давайте начнем с основной информации о вас."
            ))
        else:
            completion_percentage = profile.get_completion_percentage()
            logger.info(f"Профиль найден, заполнен на {completion_percentage:.1f}%")
            
            if profile.is_complete():
                state["profile"] = profile
                state["profile_complete"] = True
                state["current_step"] = "complete"
                state["messages"].append(AIMessage(
                    content=f"Отлично! Ваш профиль заполнен на {completion_percentage:.1f}%. "
                           "Хотите ли вы проверить и обновить информацию в профиле?"
                ))
            else:
                state["profile"] = profile
                state["profile_complete"] = False
                state["current_step"] = "incomplete"
                state["messages"].append(AIMessage(
                    content=f"Ваш профиль заполнен на {completion_percentage:.1f}%. "
                           "Давайте продолжим заполнение недостающих данных."
                ))
        
        return state
    
    def profile_complete(self, state: ProfileWorkflowState) -> ProfileWorkflowState:
        """Обрабатывает случай, когда профиль уже заполнен"""
        logger.info("Профиль заполнен, предлагаем проверку")
        
        profile = state["profile"]
        if profile:
            # Предлагаем проверить каждый раздел профиля
            profile_summary = self._generate_profile_summary(profile)
            
            state["messages"].append(AIMessage(
                content=f"Ваш текущий профиль:\n\n{profile_summary}\n\n"
                       "Хотите ли вы обновить какую-либо информацию? "
                       "Просто скажите, что именно вы хотите изменить."
            ))
        
        return state
    
    def collect_basic_info(self, state: ProfileWorkflowState) -> ProfileWorkflowState:
        """Собирает основную информацию о пользователе"""
        logger.info("Сбор основной информации")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Вы помогаете пользователю заполнить основную информацию в профиле.
            
Доступные поля:
- Подразделение (department)
- Должность (position) 
- Грейд (grade)
- Опыт работы в IT (itExperience)

Извлеките информацию из сообщения пользователя и верните JSON с полями.
Если какое-то поле не указано, оставьте пустую строку.

Пример ответа:
{
    "department": "Отдел разработки",
    "position": "Системный аналитик",
    "grade": "Middle",
    "itExperience": "3 года"
}"""),
            ("human", "{user_input}")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({"user_input": state["user_input"]})
        
        try:
            # Пытаемся извлечь JSON из ответа
            extracted_data = self._extract_json_from_response(response.content)
            logger.info(f"Извлеченные данные: {extracted_data}")
            
            # Обновляем профиль
            if state["profile"]:
                state["profile"].basicInfo.department = extracted_data.get("department", "")
                state["profile"].basicInfo.position = extracted_data.get("position", "")
                state["profile"].basicInfo.grade = extracted_data.get("grade", "")
                state["profile"].basicInfo.itExperience = extracted_data.get("itExperience", "")
            
            state["messages"].append(AIMessage(
                content="Отлично! Основная информация сохранена. "
                       "Теперь расскажите о вашей текущей роли и специализации."
            ))
            
        except Exception as e:
            logger.error(f"Ошибка при обработке основной информации: {e}")
            state["messages"].append(AIMessage(
                content="Не удалось обработать информацию. Пожалуйста, укажите: "
                       "подразделение, должность, грейд и опыт работы в IT."
            ))
        
        return state
    
    def collect_current_role(self, state: ProfileWorkflowState) -> ProfileWorkflowState:
        """Собирает информацию о текущей роли"""
        logger.info("Сбор информации о текущей роли")
        
        specialties_text = "\n".join([f"- {spec}" for spec in TECHNICAL_SPECIALTIES])
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""Вы помогаете пользователю заполнить информацию о текущей роли.

Доступные специализации:
{specialties_text}

Извлеките информацию из сообщения пользователя и верните JSON с полями:
- specialization: выберите из списка или укажите свою
- functionalRole: функциональная роль
- responsibilities: массив обязанностей

Пример ответа:
{{
    "specialization": "Системный аналитик",
    "functionalRole": "Аналитик требований",
    "responsibilities": ["Анализ требований", "Создание ТЗ", "Взаимодействие с заказчиком"]
}}"""),
            ("human", "{user_input}")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({"user_input": state["user_input"]})
        
        try:
            extracted_data = self._extract_json_from_response(response.content)
            logger.info(f"Извлеченные данные роли: {extracted_data}")
            
            if state["profile"]:
                state["profile"].currentRole.specialization = extracted_data.get("specialization", "")
                state["profile"].currentRole.functionalRole = extracted_data.get("functionalRole", "")
                state["profile"].currentRole.responsibilities = extracted_data.get("responsibilities", [])
            
            state["messages"].append(AIMessage(
                content="Информация о текущей роли сохранена. "
                       "Теперь расскажите о вашем образовании."
            ))
            
        except Exception as e:
            logger.error(f"Ошибка при обработке роли: {e}")
            state["messages"].append(AIMessage(
                content="Не удалось обработать информацию о роли. "
                       "Пожалуйста, укажите специализацию, функциональную роль и основные обязанности."
            ))
        
        return state
    
    def collect_education(self, state: ProfileWorkflowState) -> ProfileWorkflowState:
        """Собирает информацию об образовании"""
        logger.info("Сбор информации об образовании")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Вы помогаете пользователю заполнить информацию об образовании.

Извлеките информацию из сообщения пользователя и верните JSON с полями:
- institution: название учебного заведения
- degree: уровень образования (bachelor/specialist/master/phd)
- specialization: специальность
- graduationYear: год окончания

Пример ответа:
{
    "institution": "МГУ им. М.В. Ломоносова",
    "degree": "master",
    "specialization": "Прикладная математика и информатика",
    "graduationYear": "2020"
}"""),
            ("human", "{user_input}")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({"user_input": state["user_input"]})
        
        try:
            extracted_data = self._extract_json_from_response(response.content)
            logger.info(f"Извлеченные данные образования: {extracted_data}")
            
            if state["profile"]:
                state["profile"].education.institution = extracted_data.get("institution", "")
                state["profile"].education.degree = extracted_data.get("degree", "bachelor")
                state["profile"].education.specialization = extracted_data.get("specialization", "")
                state["profile"].education.graduationYear = extracted_data.get("graduationYear", "")
            
            state["messages"].append(AIMessage(
                content="Информация об образовании сохранена. "
                       "Теперь расскажите о вашем предыдущем опыте работы (если есть)."
            ))
            
        except Exception as e:
            logger.error(f"Ошибка при обработке образования: {e}")
            state["messages"].append(AIMessage(
                content="Не удалось обработать информацию об образовании. "
                       "Пожалуйста, укажите учебное заведение, уровень образования, "
                       "специальность и год окончания."
            ))
        
        return state
    
    def collect_work_experience(self, state: ProfileWorkflowState) -> ProfileWorkflowState:
        """Собирает информацию об опыте работы"""
        logger.info("Сбор информации об опыте работы")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Вы помогаете пользователю заполнить информацию об опыте работы.

Если пользователь не указывает опыт работы, верните пустой массив.

Извлеките информацию из сообщения пользователя и верните JSON с массивом опыта работы.
Каждый элемент должен содержать:
- position: должность
- company: компания
- location: место работы
- startDate: дата начала (YYYY-MM)
- endDate: дата окончания (YYYY-MM или "настоящее время")
- duration: длительность
- responsibilities: массив обязанностей

Пример ответа:
{
    "workExperience": [
        {
            "position": "Junior аналитик",
            "company": "ООО Рога и копыта",
            "location": "Москва",
            "startDate": "2020-01",
            "endDate": "2022-03",
            "duration": "2 года 3 месяца",
            "responsibilities": ["Анализ данных", "Создание отчетов"]
        }
    ]
}"""),
            ("human", "{user_input}")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({"user_input": state["user_input"]})
        
        try:
            extracted_data = self._extract_json_from_response(response.content)
            work_experience = extracted_data.get("workExperience", [])
            logger.info(f"Извлеченный опыт работы: {len(work_experience)} позиций")
            
            if state["profile"]:
                state["profile"].workExperience = [
                    WorkExperience(**exp) for exp in work_experience
                ]
            
            state["messages"].append(AIMessage(
                content="Информация об опыте работы сохранена. "
                       "Теперь расскажите о ваших навыках и компетенциях."
            ))
            
        except Exception as e:
            logger.error(f"Ошибка при обработке опыта работы: {e}")
            state["messages"].append(AIMessage(
                content="Не удалось обработать информацию об опыте работы. "
                       "Если у вас нет опыта работы, просто скажите 'нет опыта'."
            ))
        
        return state
    
    def collect_skills(self, state: ProfileWorkflowState) -> ProfileWorkflowState:
        """Собирает информацию о навыках и компетенциях"""
        logger.info("Сбор информации о навыках")
        
        competencies_text = "\n".join([f"- {comp}" for comp in SKILLS_AND_COMPETENCIES[:10]])  # Показываем первые 10
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""Вы помогаете пользователю заполнить информацию о навыках и компетенциях.

Доступные компетенции (показаны первые 10):
{competencies_text}

Извлеките информацию из сообщения пользователя и верните JSON с полями:
- competencies: массив выбранных компетенций из списка
- programmingLanguages: массив языков программирования с уровнями
- otherCompetencies: массив других технических навыков с уровнями

Пример ответа:
{{
    "competencies": ["Участвует в проектировании ИС/ПС", "Взаимодействует с бизнес-аналитиками"],
    "programmingLanguages": [
        {{"skill": "Python", "level": "Уверенный"}},
        {{"skill": "SQL", "level": "Базовый"}}
    ],
    "otherCompetencies": [
        {{"skill": "JIRA", "level": "Уверенный"}},
        {{"skill": "Docker", "level": "Начальный"}}
    ]
}}"""),
            ("human", "{user_input}")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({"user_input": state["user_input"]})
        
        try:
            extracted_data = self._extract_json_from_response(response.content)
            logger.info(f"Извлеченные навыки: {extracted_data}")
            
            if state["profile"]:
                state["profile"].competencies = extracted_data.get("competencies", [])
                
                # Обрабатываем языки программирования
                prog_langs = extracted_data.get("programmingLanguages", [])
                state["profile"].programmingLanguages = [
                    TechnicalSkill(**lang) for lang in prog_langs
                ]
                
                # Обрабатываем другие компетенции
                other_comp = extracted_data.get("otherCompetencies", [])
                state["profile"].otherCompetencies = [
                    TechnicalSkill(**comp) for comp in other_comp
                ]
            
            state["messages"].append(AIMessage(
                content="Информация о навыках сохранена. "
                       "Теперь расскажите о знании иностранных языков."
            ))
            
        except Exception as e:
            logger.error(f"Ошибка при обработке навыков: {e}")
            state["messages"].append(AIMessage(
                content="Не удалось обработать информацию о навыках. "
                       "Пожалуйста, укажите ваши основные компетенции и технические навыки."
            ))
        
        return state
    
    def collect_languages(self, state: ProfileWorkflowState) -> ProfileWorkflowState:
        """Собирает информацию об иностранных языках"""
        logger.info("Сбор информации об иностранных языках")
        
        languages_text = "\n".join([f"- {lang}" for lang in LANGUAGES])
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""Вы помогаете пользователю заполнить информацию об иностранных языках.

Доступные языки:
{languages_text}

Уровни владения: Начальный, Базовый, Уверенный, Продвинутый, Экспертный

Извлеките информацию из сообщения пользователя и верните JSON с массивом языков.
Если языки не указаны, верните пустой массив.

Пример ответа:
{{
    "foreignLanguages": [
        {{"language": "Английский", "level": "Уверенный"}},
        {{"language": "Немецкий", "level": "Базовый"}}
    ]
}}"""),
            ("human", "{user_input}")
        ])
        
        chain = prompt | self.llm
        response = chain.invoke({"user_input": state["user_input"]})
        
        try:
            extracted_data = self._extract_json_from_response(response.content)
            languages = extracted_data.get("foreignLanguages", [])
            logger.info(f"Извлеченные языки: {len(languages)} языков")
            
            if state["profile"]:
                state["profile"].foreignLanguages = [
                    LanguageSkill(**lang) for lang in languages
                ]
            
            state["messages"].append(AIMessage(
                content="Информация об иностранных языках сохранена. "
                       "Завершаем заполнение профиля..."
            ))
            
        except Exception as e:
            logger.error(f"Ошибка при обработке языков: {e}")
            state["messages"].append(AIMessage(
                content="Не удалось обработать информацию о языках. "
                       "Если вы не знаете иностранных языков, просто скажите 'нет'."
            ))
        
        return state
    
    def validate_profile(self, state: ProfileWorkflowState) -> ProfileWorkflowState:
        """Валидирует заполненный профиль"""
        logger.info("Валидация профиля")
        
        profile = state["profile"]
        if not profile:
            state["validation_errors"] = ["Профиль не найден"]
            return state
        
        errors = []
        
        # Проверяем обязательные поля
        if not profile.basicInfo.department.strip():
            errors.append("Не указано подразделение")
        if not profile.basicInfo.position.strip():
            errors.append("Не указана должность")
        if not profile.basicInfo.grade.strip():
            errors.append("Не указан грейд")
        if not profile.basicInfo.itExperience.strip():
            errors.append("Не указан опыт работы в IT")
        if not profile.currentRole.specialization.strip():
            errors.append("Не указана специализация")
        if not profile.currentRole.functionalRole.strip():
            errors.append("Не указана функциональная роль")
        if not profile.education.institution.strip():
            errors.append("Не указано учебное заведение")
        if not profile.education.specialization.strip():
            errors.append("Не указана специальность")
        if not profile.education.graduationYear.strip():
            errors.append("Не указан год окончания")
        
        state["validation_errors"] = errors
        
        if errors:
            state["messages"].append(AIMessage(
                content=f"Обнаружены ошибки в профиле: {', '.join(errors)}. "
                       "Пожалуйста, исправьте их."
            ))
        else:
            state["messages"].append(AIMessage(
                content="Профиль успешно заполнен и проверен!"
            ))
        
        return state
    
    def save_profile(self, state: ProfileWorkflowState) -> ProfileWorkflowState:
        """Сохраняет профиль пользователя"""
        logger.info("Сохранение профиля")
        
        profile = state["profile"]
        if profile and not state["validation_errors"]:
            if save_user_profile(profile):
                completion_percentage = profile.get_completion_percentage()
                state["messages"].append(AIMessage(
                    content=f"Профиль успешно сохранен! Заполнение: {completion_percentage:.1f}%"
                ))
            else:
                state["messages"].append(AIMessage(
                    content="Ошибка при сохранении профиля. Попробуйте еще раз."
                ))
        else:
            state["messages"].append(AIMessage(
                content="Профиль не может быть сохранен из-за ошибок валидации."
            ))
        
        return state
    
    def route_after_check(self, state: ProfileWorkflowState) -> str:
        """Определяет следующий шаг после проверки профиля"""
        if state["profile_complete"]:
            return "complete"
        else:
            return "incomplete"
    
    def _extract_json_from_response(self, response_text: str) -> Dict[str, Any]:
        """Извлекает JSON из ответа LLM"""
        try:
            # Ищем JSON в ответе
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                logger.warning("JSON не найден в ответе")
                return {}
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
            return {}
    
    def _generate_profile_summary(self, profile: UserProfile) -> str:
        """Генерирует краткое описание профиля"""
        summary = f"""
**Основная информация:**
- Подразделение: {profile.basicInfo.department}
- Должность: {profile.basicInfo.position}
- Грейд: {profile.basicInfo.grade}
- Опыт в IT: {profile.basicInfo.itExperience}

**Текущая роль:**
- Специализация: {profile.currentRole.specialization}
- Функциональная роль: {profile.currentRole.functionalRole}

**Образование:**
- Учебное заведение: {profile.education.institution}
- Специальность: {profile.education.specialization}
- Год окончания: {profile.education.graduationYear}

**Опыт работы:** {len(profile.workExperience)} позиций
**Компетенции:** {len(profile.competencies)} навыков
**Языки программирования:** {len(profile.programmingLanguages)} языков
**Иностранные языки:** {len(profile.foreignLanguages)} языков
"""
        return summary.strip()
    
    async def process_message(self, message: str, user_id: str = "default") -> str:
        """Обрабатывает сообщение пользователя в контексте профиля"""
        logger.info(f"Обработка сообщения пользователя: {message[:100]}...")
        
        # Создаем начальное состояние
        initial_state = ProfileWorkflowState(
            messages=[HumanMessage(content=message)],
            profile=None,
            current_step="",
            profile_complete=False,
            user_input=message,
            extracted_data={},
            validation_errors=[]
        )
        
        # Запускаем пайплайн
        result = await self.workflow.ainvoke(initial_state)
        
        # Возвращаем последнее сообщение от AI
        if result["messages"]:
            last_message = result["messages"][-1]
            if isinstance(last_message, AIMessage):
                return last_message.content
        
        return "Произошла ошибка при обработке сообщения."
