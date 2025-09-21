from typing import Annotated

from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from config import Settings


class HRRequestServer:
    settings = Settings()

    @staticmethod
    def process_hr_request(request: str):
        graph = HRRequestServer.build_graph()
        response = graph.invoke({"messages": [{"role": "user", "content": request}]})
        return response["messages"][-1].content

    @staticmethod
    def build_graph():
        class State(TypedDict):
            messages: Annotated[list, add_messages]

        graph_builder = StateGraph(State)

        llm = ChatOpenAI(
            model="Qwen2.5-72B-Instruct-AWQ",
            api_key=HRRequestServer.settings.scibox_api_key,
            base_url="https://llm.t1v.scibox.tech/v1",
            temperature=0.7,
            max_tokens=512,
        )

        def chatbot(state: State):
            return {"messages": [llm.invoke(state["messages"])]}

        graph_builder.add_node("chatbot", chatbot)
        graph_builder.add_edge(START, "chatbot")
        graph_builder.add_edge("chatbot", END)
        graph = graph_builder.compile()

        return graph
