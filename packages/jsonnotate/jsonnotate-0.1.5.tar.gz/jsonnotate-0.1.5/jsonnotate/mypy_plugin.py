from typing import Callable, Optional
from mypy.plugin import ClassDefContext, Plugin


class JsonSchemaPlugin(Plugin):
    def get_class_decorator_hook_2(self, fullname: str) -> Optional[Callable[[ClassDefContext], bool]]:
        return None


def plugin(*a, **k):
    # print("plugin", a, k)
    return JsonSchemaPlugin
