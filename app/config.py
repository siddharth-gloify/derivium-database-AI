import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    llm_model: str = os.getenv("LLM_MODEL", "gpt-4o")
    db_host: str = os.getenv("HOST", "")
    db_port: int = int(os.getenv("PORT", 5432))
    db_name: str = os.getenv("DATABASE", "")
    db_user: str = os.getenv("USER", "")
    db_password: str = os.getenv("PASSWORD", "")


settings = Settings()
