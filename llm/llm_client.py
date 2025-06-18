import yaml
from langchain_community.chat_models import ChatOpenAI

def load_llm():
    with open("config/settings.yaml", "r") as f:
        settings = yaml.safe_load(f)
    return ChatOpenAI(temperature=settings["llm"]["temperature"], model=settings["llm"]["model"], openai_api_key=settings["llm"]["openai_api_key"])
