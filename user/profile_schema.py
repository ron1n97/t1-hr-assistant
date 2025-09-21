"""
Схема данных профиля пользователя
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class ProficiencyLevel(str, Enum):
    BEGINNER = "Начальный"
    BASIC = "Базовый"
    CONFIDENT = "Уверенный"
    ADVANCED = "Продвинутый"
    EXPERT = "Экспертный"


class EducationLevel(str, Enum):
    BACHELOR = "bachelor"
    SPECIALIST = "specialist"
    MASTER = "master"
    PHD = "phd"


class MaterialType(str, Enum):
    COURSE = "course"
    VIDEO = "video"
    BOOK = "book"
    ARTICLE = "article"


class MaterialLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class WorkExperience(BaseModel):
    position: str = Field(description="Роль/Должность")
    company: str = Field(description="Компания")
    location: str = Field(description="Место работы")
    startDate: str = Field(description="Период работы (начало)")
    endDate: str = Field(description="Период работы (конец)")
    duration: str = Field(description="Длительность")
    responsibilities: List[str] = Field(description="Обязанности")


class Education(BaseModel):
    institution: str = Field(description="Название учебного заведения")
    degree: EducationLevel = Field(description="Уровень образования")
    specialization: str = Field(description="Специальность")
    graduationYear: str = Field(description="Год окончания")


class LanguageSkill(BaseModel):
    language: str = Field(description="Язык")
    level: ProficiencyLevel = Field(description="Уровень владения")


class TechnicalSkill(BaseModel):
    skill: str = Field(description="Навык/Компетенция")
    level: ProficiencyLevel = Field(description="Уровень владения")


class BasicInfo(BaseModel):
    department: str = Field(description="Подразделение")
    position: str = Field(description="Должность")
    grade: str = Field(description="Грейд")
    itExperience: str = Field(description="Опыт работы в IT")


class CurrentRole(BaseModel):
    specialization: str = Field(description="Специализация")
    functionalRole: str = Field(description="Функциональная роль")
    responsibilities: List[str] = Field(description="Обязанности")


class AdditionalRole(BaseModel):
    specialization: str = Field(description="Специализация")
    role: str = Field(description="Роль")
    responsibilities: List[str] = Field(description="Обязанности")


class UserProfile(BaseModel):
    basicInfo: BasicInfo = Field(description="Основная информация")
    currentRole: CurrentRole = Field(description="Текущая роль")
    additionalRole: Optional[AdditionalRole] = Field(None, description="Дополнительная роль")
    workExperience: List[WorkExperience] = Field(default_factory=list, description="Предыдущий опыт работы")
    education: Education = Field(description="Образование")
    skills: List[str] = Field(default_factory=list, description="Навыки")
    competencies: List[str] = Field(default_factory=list, description="Компетенции")
    foreignLanguages: List[LanguageSkill] = Field(default_factory=list, description="Иностранные языки")
    otherCompetencies: List[TechnicalSkill] = Field(default_factory=list, description="Прочие компетенции")
    programmingLanguages: List[TechnicalSkill] = Field(default_factory=list, description="Языки программирования")

    def is_complete(self) -> bool:
        """Проверяет, заполнен ли профиль полностью"""
        required_fields = [
            self.basicInfo.department,
            self.basicInfo.position,
            self.basicInfo.grade,
            self.basicInfo.itExperience,
            self.currentRole.specialization,
            self.currentRole.functionalRole,
            self.education.institution,
            self.education.specialization,
            self.education.graduationYear
        ]
        return all(field.strip() for field in required_fields)

    def get_completion_percentage(self) -> float:
        """Возвращает процент заполнения профиля"""
        total_fields = 9  # основные обязательные поля
        filled_fields = sum(1 for field in [
            self.basicInfo.department,
            self.basicInfo.position,
            self.basicInfo.grade,
            self.basicInfo.itExperience,
            self.currentRole.specialization,
            self.currentRole.functionalRole,
            self.education.institution,
            self.education.specialization,
            self.education.graduationYear
        ] if field.strip())
        
        return (filled_fields / total_fields) * 100


class Material(BaseModel):
    id: str = Field(description="Уникальный идентификатор")
    title: str = Field(description="Название материала")
    description: str = Field(description="Описание")
    type: MaterialType = Field(description="Тип материала")
    duration: str = Field(description="Длительность")
    rating: float = Field(description="Рейтинг")
    level: MaterialLevel = Field(description="Уровень сложности")
    category: str = Field(description="Категория")


# Константы для выбора
TECHNICAL_SPECIALTIES = [
    'Системный аналитик',
    'Бизнес-аналитик', 
    'Аналитик данных',
    'Продуктовый аналитик',
    'Функциональный аналитик',
    'Аналитик информационных систем',
    'Архитектор систем',
    'Проектировщик ИС',
    'Разработчик требований',
    'Специалист по тестированию',
    'DevOps инженер',
    'Frontend разработчик',
    'Backend разработчик',
    'Fullstack разработчик',
    'Мобильный разработчик',
    'UI/UX дизайнер',
    'Scrum Master',
    'Product Manager',
    'Technical Writer',
    'QA инженер'
]

SKILLS_AND_COMPETENCIES = [
    'Участвует в проектировании ИС/ПС',
    'Взаимодействует с бизнес-аналитиками/заказчиками',
    'Участвует в создании и оценке бизнес-требований к ИС/ПС',
    'Разрабатывает и поддерживает в актуальном состоянии функциональные и нефункциональные требования',
    'Осуществляет декомпозицию требований для разработки',
    'Обеспечивает бесконфликтность и полноту требований в части разрабатываемых Артефактов',
    'Пишет технические задания на разработку автоматизированных систем',
    'Взаимодействует с командой разработки',
    'Анализирует пользовательские интерфейсы',
    'Проводит систематическую проверку тест-кейсов',
    'Передает Артефакты в Архив программы',
    'Осуществляет анализ системы по специфическим запросам',
    'Сопровождает накопленную документацию',
    'Организует и проводит демонстрации прототипов',
    'Принимает участие во внедрении ИС/ПС',
    'Анализ бизнес-инициативы',
    'Анализ предметной области',
    'Интервьирование бизнес-заказчика',
    'Выявление рисков и неопределенностей',
    'Анализ возможных решений',
    'Разработка критериев приемки решения',
    'Подготовка бизнес-требований с учетом возможностей ИТ',
    'Анализ бизнес-данных и документов',
    'Визуализация данных',
    'Разработка глоссария для формализации предметной области',
    'Описание артефактов (Функциональность ИС, Требования к ИС)',
    'Участие в проектировании систем',
    'Моделирование бизнес процессов as-is и проектирование процессов to-be',
    'Документирование',
    'Содействие формированию и управление бэклогом',
    'Моделирование состояний и сценариев использования системы'
]

LANGUAGES = [
    'Английский',
    'Немецкий',
    'Французский',
    'Испанский',
    'Итальянский',
    'Китайский',
    'Японский',
    'Корейский',
    'Арабский'
]

OTHER_TECHNICAL_SKILLS = [
    'API',
    'REST',
    'GraphQL',
    'SOAP',
    'Kafka',
    'RabbitMQ',
    'PostgreSQL',
    'MySQL',
    'MongoDB',
    'Redis',
    'Docker',
    'Kubernetes',
    'AWS',
    'Azure',
    'GCP',
    'Git',
    'Jenkins',
    'JIRA',
    'Confluence',
    'Postman',
    'Swagger',
    'Linux',
    'Windows Server',
    'Nginx',
    'Apache'
]

PROGRAMMING_LANGUAGES = [
    'Python',
    'Java',
    'JavaScript',
    'TypeScript', 
    'C#',
    'C++',
    'PHP',
    'Ruby',
    'Go',
    'Rust',
    'Swift',
    'Kotlin',
    'Scala',
    'R',
    'MATLAB',
    'SQL',
    'HTML/CSS',
    'Shell/Bash'
]

# Учебные материалы
LEARNING_MATERIALS = [
    Material(
        id='1',
        title='Основы системного анализа',
        description='Полный курс по методам и практикам системного анализа для начинающих специалистов.',
        type=MaterialType.COURSE,
        duration='12 часов',
        rating=4.8,
        level=MaterialLevel.BEGINNER,
        category='Системный анализ'
    ),
    Material(
        id='2',
        title='UML моделирование на практике',
        description='Практическое руководство по созданию UML диаграмм для проектирования систем.',
        type=MaterialType.VIDEO,
        duration='3 часа',
        rating=4.6,
        level=MaterialLevel.INTERMEDIATE,
        category='Моделирование'
    ),
    Material(
        id='3',
        title='Бизнес-анализ: от требований к решениям',
        description='Комплексное изучение процесса бизнес-анализа и работы с заказчиками.',
        type=MaterialType.BOOK,
        duration='400 страниц',
        rating=4.9,
        level=MaterialLevel.INTERMEDIATE,
        category='Бизнес-анализ'
    ),
    Material(
        id='4',
        title='Agile и Scrum для аналитиков',
        description='Особенности работы аналитика в гибких методологиях разработки.',
        type=MaterialType.COURSE,
        duration='8 часов',
        rating=4.7,
        level=MaterialLevel.INTERMEDIATE,
        category='Методологии'
    ),
    Material(
        id='5',
        title='SQL для анализа данных',
        description='Основы SQL с фокусом на задачи анализа и отчетности.',
        type=MaterialType.COURSE,
        duration='15 часов',
        rating=4.5,
        level=MaterialLevel.BEGINNER,
        category='Технические навыки'
    ),
    Material(
        id='6',
        title='Современные инструменты аналитика',
        description='Обзор и практика работы с JIRA, Confluence, Figma и другими инструментами.',
        type=MaterialType.ARTICLE,
        duration='45 мин',
        rating=4.4,
        level=MaterialLevel.BEGINNER,
        category='Инструменты'
    )
]
