from abc import ABC, abstractmethod
import ast
from typing import Tuple, Optional


class CodeValidator(ABC):

    @abstractmethod
    def validate(self, text: str, *args, **kwargs) -> Tuple[bool, Optional[Exception]]:
        pass


class AstValidator(CodeValidator):

    def validate(self, text: str, *args, **kwargs) -> Tuple[bool, Optional[SyntaxError]]:
        try:
            ast.parse(text)
            return (True, None)
        except SyntaxError as e:
            return (False, e)
