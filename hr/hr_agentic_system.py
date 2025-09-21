import json
import logging
import re
from typing import Annotated, Dict, Any, Optional

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from config import Settings
from hr.state import HRState
from hr.candidates_data import MOCK_CANDIDATES

logger = logging.getLogger(__name__)


def extract_json_from_response(response_content: str) -> Optional[Dict[Any, Any]]:
    """
    Универсальный парсер JSON из ответа LLM.
    Обрабатывает различные форматы:
    1. Чистый JSON
    2. JSON в markdown блоке ```json
    3. JSON в обычном markdown блоке ```
    4. JSON с дополнительным текстом
    """
    if not response_content:
        return None
    
    content = response_content.strip()
    logger.info(f"🔧 JSON парсер: Исходный контент: {content[:200]}...")
    
    # Случай 1: Чистый JSON (начинается с { или [)
    if content.startswith(('{', '[')):
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
    
    # Случай 2: JSON в markdown блоке ```json
    json_pattern = r'```json\s*\n?(.*?)\n?```'
    match = re.search(json_pattern, content, re.DOTALL | re.IGNORECASE)
    if match:
        json_content = match.group(1).strip()
        logger.info(f"🔧 JSON парсер: Найден JSON в markdown блоке: {json_content[:100]}...")
        try:
            return json.loads(json_content)
        except json.JSONDecodeError:
            pass
    
    # Случай 3: JSON в обычном markdown блоке ```
    code_pattern = r'```\s*\n?(.*?)\n?```'
    match = re.search(code_pattern, content, re.DOTALL)
    if match:
        json_content = match.group(1).strip()
        # Проверяем, что это похоже на JSON
        if json_content.startswith(('{', '[')):
            logger.info(f"🔧 JSON парсер: Найден JSON в обычном блоке: {json_content[:100]}...")
            try:
                return json.loads(json_content)
            except json.JSONDecodeError:
                pass
    
    # Случай 4: Поиск JSON в тексте (между фигурными скобками)
    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    matches = re.findall(json_pattern, content, re.DOTALL)
    for match in matches:
        logger.info(f"🔧 JSON парсер: Найден JSON в тексте: {match[:100]}...")
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue
    
    # Случай 5: Поиск JSON массива
    array_pattern = r'\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]'
    matches = re.findall(array_pattern, content, re.DOTALL)
    for match in matches:
        logger.info(f"🔧 JSON парсер: Найден JSON массив: {match[:100]}...")
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue
    
    logger.error(f"🔧 JSON парсер: Не удалось извлечь JSON из контента")
    return None


class HRRequestServer:
    settings = Settings()

    @staticmethod
    def process_hr_request(request: str):
        logger.info(f"🚀 HR мультиагентная система: Начало обработки запроса '{request}'")
        
        graph = HRRequestServer.build_graph()
        logger.info(f"🚀 HR мультиагентная система: Граф построен, запуск выполнения")
        
        response = graph.invoke({
            "messages": [{"role": "user", "content": request}],
            "candidates": None,
            "request_type": None,
            "search_query": None,
            "selected_candidates": None,
            "reasoning": None
        })
        
        final_response = response["messages"][-1].content
        logger.info(f"🚀 HR мультиагентная система: Обработка завершена, длина ответа: {len(final_response)} символов")
        
        return final_response

    @staticmethod
    def build_graph():
        graph_builder = StateGraph(HRState)

        llm = ChatOpenAI(
            model="Qwen2.5-72B-Instruct-AWQ",
            api_key=HRRequestServer.settings.scibox_api_key,
            base_url="https://llm.t1v.scibox.tech/v1",
            temperature=0.7,
            max_tokens=1024,
        )

        def router(state: HRState):
            """Роутер для определения типа запроса"""
            user_message = state["messages"][-1].content
            user_message_lower = user_message.lower()
            
            logger.info(f"🔀 Роутер: Анализ запроса '{user_message}'")
            
            # Ключевые слова для поиска кандидатов
            candidate_keywords = [
                "кандидат", "candidate", "найди", "поиск", "ищу", "ищем",
                "разработчик", "developer", "программист", "инженер", "engineer",
                "менеджер", "manager", "дизайнер", "designer", "аналитик", "analyst",
                "devops", "frontend", "backend", "fullstack", "python", "javascript",
                "react", "angular", "vue", "java", "c#", "php", "ruby", "go",
                "опыт", "experience", "навыки", "skills", "технологии", "technologies"
            ]
            
            # Проверяем, содержит ли запрос ключевые слова для поиска кандидатов
            found_keywords = [keyword for keyword in candidate_keywords if keyword in user_message_lower]
            is_candidate_search = len(found_keywords) > 0
            
            logger.info(f"🔀 Роутер: Найдены ключевые слова: {found_keywords}")
            logger.info(f"🔀 Роутер: Тип запроса: {'поиск кандидатов' if is_candidate_search else 'общий вопрос'}")
            
            if is_candidate_search:
                logger.info(f"🔀 Роутер: Перенаправление на агент поиска кандидатов")
                return {
                    "request_type": "candidate_search",
                    "search_query": user_message,
                    "candidates": MOCK_CANDIDATES
                }
            else:
                logger.info(f"🔀 Роутер: Перенаправление на агент общих вопросов")
                return {
                    "request_type": "general_question"
                }

        def candidate_search_agent(state: HRState):
            """Агент для поиска и выбора кандидатов"""
            logger.info(f"🔍 Агент поиска кандидатов: Начало обработки запроса '{state['search_query']}'")
            logger.info(f"🔍 Агент поиска кандидатов: Доступно кандидатов: {len(state['candidates'])}")
            
            candidates_json = json.dumps([candidate.dict() for candidate in state["candidates"]], ensure_ascii=False, indent=2)
            
            prompt = f"""
Ты HR-специалист, который помогает найти подходящих кандидатов.

Запрос пользователя: {state["search_query"]}

Доступные кандидаты:
{candidates_json}

Проанализируй запрос и найди наиболее подходящих кандидатов. Учти:
1. Технические навыки и опыт
2. Желаемую позицию
3. Уровень зарплаты
4. Местоположение
5. Статус кандидата

ИНСТРУКЦИИ:
- Верни результат в формате JSON
- Если кандидаты не найдены, верни пустой массив selected_candidates
- Обоснование должно быть кратким и понятным
- total_found должно соответствовать количеству найденных кандидатов

Формат ответа:
{{
    "selected_candidates": [список ID подходящих кандидатов],
    "reasoning": "обоснование выбора",
    "total_found": количество_найденных
}}
"""

            logger.info(f"🔍 Агент поиска кандидатов: Отправка запроса к LLM")
            response = llm.invoke([{"role": "user", "content": prompt}])
            logger.info(f"🔍 Агент поиска кандидатов: Получен ответ от LLM")
            
            try:
                # Используем универсальный парсер JSON
                result = extract_json_from_response(response.content)
                
                if result is None:
                    logger.error(f"🔍 Агент поиска кандидатов: Не удалось извлечь JSON из ответа")
                    return {
                        "messages": [{"role": "assistant", "content": "Извините, произошла ошибка при обработке запроса. Попробуйте переформулировать ваш запрос."}]
                    }
                
                selected_ids = result.get("selected_candidates", [])
                reasoning = result.get("reasoning", "")
                total_found = result.get("total_found", 0)
                
                logger.info(f"🔍 Агент поиска кандидатов: LLM выбрал кандидатов с ID: {selected_ids}")
                logger.info(f"🔍 Агент поиска кандидатов: Обоснование: {reasoning[:100]}...")
                
                # Находим кандидатов по ID
                selected_candidates = [
                    candidate for candidate in state["candidates"] 
                    if candidate.id in selected_ids
                ]
                
                logger.info(f"🔍 Агент поиска кандидатов: Найдено кандидатов: {len(selected_candidates)}")
                for candidate in selected_candidates:
                    logger.info(f"🔍 Агент поиска кандидатов: - {candidate.name} ({candidate.position})")
                
                # Формируем ответ для пользователя
                if selected_candidates:
                    response_text = f"Найдено {total_found} подходящих кандидатов:\n\n"
                    for i, candidate in enumerate(selected_candidates, 1):
                        response_text += f"{i}. **{candidate.name}**\n"
                        response_text += f"   Позиция: {candidate.position}\n"
                        response_text += f"   Зарплата: {candidate.salary}\n"
                        response_text += f"   Навыки: {', '.join(candidate.skills)}\n"
                        response_text += f"   Опыт: {candidate.experience[0].company if candidate.experience else 'Не указан'}\n"
                        response_text += f"   Статус: {candidate.status}\n\n"
                    
                    response_text += f"**Обоснование выбора:**\n{reasoning}"
                else:
                    response_text = f"К сожалению, по вашему запросу не найдено подходящих кандидатов.\n\n**Обоснование:**\n{reasoning}"
                
                logger.info(f"🔍 Агент поиска кандидатов: Формирование ответа завершено")
                
                return {
                    "selected_candidates": selected_candidates,
                    "reasoning": reasoning,
                    "messages": [{"role": "assistant", "content": response_text}]
                }
                
            except Exception as e:
                logger.error(f"🔍 Агент поиска кандидатов: Неожиданная ошибка: {e}")
                logger.error(f"🔍 Агент поиска кандидатов: Исходный ответ LLM: {response.content}")
                # Если произошла неожиданная ошибка, возвращаем простой ответ
                return {
                    "messages": [{"role": "assistant", "content": "Извините, произошла ошибка при обработке запроса. Попробуйте переформулировать ваш запрос."}]
                }

        def general_question_agent(state: HRState):
            """Агент для ответов на общие HR вопросы"""
            user_question = state["messages"][-1].content
            logger.info(f"💼 Агент общих вопросов: Обработка вопроса '{user_question}'")
            
            prompt = f"""
Ты HR-специалист компании. Отвечай на вопросы о HR-процессах, политиках компании, 
трудовом законодательстве, найме, адаптации сотрудников и других HR-вопросах.

Вопрос: {user_question}

Дай развернутый и полезный ответ на русском языке.
"""

            logger.info(f"💼 Агент общих вопросов: Отправка запроса к LLM")
            response = llm.invoke([{"role": "user", "content": prompt}])
            logger.info(f"💼 Агент общих вопросов: Получен ответ от LLM")
            logger.info(f"💼 Агент общих вопросов: Длина ответа: {len(response.content)} символов")
            
            return {"messages": [{"role": "assistant", "content": response.content}]}

        # Добавляем узлы
        graph_builder.add_node("router", router)
        graph_builder.add_node("candidate_search", candidate_search_agent)
        graph_builder.add_node("general_question", general_question_agent)

        # Добавляем условные переходы
        def should_search_candidates(state: HRState):
            return state["request_type"] == "candidate_search"

        def should_answer_general(state: HRState):
            return state["request_type"] == "general_question"

        # Настраиваем граф
        graph_builder.add_edge(START, "router")
        graph_builder.add_conditional_edges(
            "router",
            should_search_candidates,
            {
                True: "candidate_search",
                False: "general_question"
            }
        )
        graph_builder.add_edge("candidate_search", END)
        graph_builder.add_edge("general_question", END)

        graph = graph_builder.compile()
        return graph
