from typing import SupportsInt
from ._numeric import AbstractBaseNumericTag

class AbstractBaseIntTag(AbstractBaseNumericTag):
    def __init__(self, value: SupportsInt = 0): ...
    @property
    def py_int(self) -> int: ...

class ByteTag(AbstractBaseIntTag): ...
class ShortTag(AbstractBaseIntTag): ...
class IntTag(AbstractBaseIntTag): ...
class LongTag(AbstractBaseIntTag): ...
