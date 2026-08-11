from plugins.base import ToolPlugin


class ShrugPlugin(ToolPlugin):
    name = "shrug"
    description = "Return the shrug emoji — for dramatic effect."
    category = "fun"

    def execute(self) -> dict[str, str]:
        return {"text": "¯\\_(ツ)_/¯"}
