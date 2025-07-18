
from pydantic import BaseModel, Field

RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "chat_summary",
        "title": "chat_summary",
        "description": "Структурированный отчет по чату за неделю",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "main_fragments": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "maxItems": 5,
                    "description": "Главные фрагменты недели (всё, что обсуждалось, смешило или бесило)"
                },
                "failures_and_rage": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "maxItems": 5,
                    "description": "Где всё пошло по п***е"
                },
                "topics_to_discuss": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "maxItems": 5,
                    "description": "Темы, которые точно надо добить/обсудить"
                }
            },
            "required": ["main_fragments", "failures_and_rage", "topics_to_discuss"],
            "additionalProperties": False
        }
    }
}

class LLMResponse(BaseModel):
    main_fragments: list = Field(description="Главные фрагменты отчета")
    failures_and_rage: list = Field(description="Ошибки и негативные моменты")
    topics_to_discuss: list = Field(description="Темы для обсуждения")
