from plugins.base import ToolPlugin


class AskUserPlugin(ToolPlugin):
    name = "ask_user"
    description = "Ask the user a question. Use when you need clarification, a decision, or additional information."
    category = "interaction"

    def get_parameters_schema(self):
        return {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The question to ask the user",
                },
            },
            "required": ["question"],
        }

    def execute(self, question: str) -> dict:
        response = input(f"\n\033[33m🤔 {question}\033[0m\n\033[32mYour answer: \033[0m")
        return {"question": question, "response": response}
