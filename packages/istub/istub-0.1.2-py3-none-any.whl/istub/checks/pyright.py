import json

from istub.checks.base import BaseCheck


class PyrightCheck(BaseCheck):
    NAME = "pyright"

    def run(self) -> str:
        command = ["npx", "pyright", self.package.path.as_posix(), "--outputjson"]
        output = self.get_call_output(command, capture_stderr=False)
        try:
            errors = json.loads(output).get("generalDiagnostics", [])
        except json.JSONDecodeError:
            return self.get_call_output(command, capture_stderr=True)

        if not errors:
            return ""

        messages = []
        for error in errors:
            messages.append(
                f'{error["file"]}:{error["range"]["start"]["line"]} {error.get("message", "")}'
            )
        return "\n".join(messages)
