from abc import ABC, abstractmethod
from telegrinder.modules import json
from telegrinder.bot.cute_types import MessageCute
import typing
import collections
import vbml

T = typing.TypeVar("T")
patcher = vbml.Patcher()

Message = MessageCute
EventScheme = collections.namedtuple("EventScheme", ["name", "dataclass"])


class ABCRule(ABC, typing.Generic[T]):
    __event__: typing.Optional[EventScheme] = None

    @abstractmethod
    async def check(self, event: T, ctx: dict) -> bool:
        pass

    def __and__(self, other: "ABCRule"):
        return AndRule(self, other)

    def __or__(self, other: "ABCRule"):
        return OrRule(self, other)


class AndRule(ABCRule):
    def __init__(self, *rules: ABCRule):
        self.rules = rules

    async def check(self, event: dict, ctx: dict) -> bool:
        ctx_copy = ctx.copy()
        for rule in self.rules:
            e = event
            if rule.__event__:
                if rule.__event__.name not in event:
                    return False
                e = rule.__event__.dataclass(**event[rule.__event__.name])
            if not await rule.check(e, ctx_copy):
                return False
        ctx.clear()
        ctx.update(ctx_copy)
        return True


class OrRule(ABCRule):
    def __init__(self, *rules: ABCRule):
        self.rules = rules

    async def check(self, event: T, ctx: dict) -> bool:
        ctx_copy = ctx.copy()
        found = False

        for rule in self.rules:
            e = event
            if rule.__event__:
                if rule.__event__.name not in event:
                    continue
                e = rule.__event__.dataclass(**event[rule.__event__.name])
            if await rule.check(e, ctx_copy):
                found = True
                break

        ctx.clear()
        ctx.update(ctx_copy)
        return found


class ABCMessageRule(ABCRule, ABC):
    __event__ = EventScheme("message", Message)

    @abstractmethod
    async def check(self, message: Message, ctx: dict) -> bool:
        ...


class IsMessage(ABCRule):
    async def check(self, event: dict, ctx: dict) -> bool:
        return "message" in event


class Text(ABCMessageRule):
    def __init__(
        self, texts: typing.Union[str, typing.List[str]], ignore_case: bool = False
    ):
        if not isinstance(texts, list):
            texts = [texts]
        self.texts = texts
        self.ignore_case = ignore_case

    async def check(self, message: Message, ctx: dict) -> bool:
        if self.ignore_case:
            return message.text.lower() in list(map(str.lower, self.texts))
        return message.text in self.texts


class IsPrivate(ABCMessageRule):
    async def check(self, message: Message, ctx: dict) -> bool:
        return message.chat.id > 0


class IsChat(ABCRule):
    async def check(self, message: Message, ctx: dict) -> bool:
        return message.chat.id < 0


class Markup(ABCMessageRule):
    def __init__(self, patterns: typing.Union[str, typing.List[str]]):
        if not isinstance(patterns, list):
            patterns = [patterns]
        self.patterns = [
            vbml.Pattern(pattern) if isinstance(pattern, str) else pattern
            for pattern in patterns
        ]

    async def check(self, message: Message, ctx: dict) -> bool:
        for pattern in self.patterns:
            response = patcher.check(pattern, message.text)
            if response is False:
                continue
            ctx.update(response)
            return True
        return False


class FuncRule(ABCRule, typing.Generic[T]):
    def __init__(
        self,
        func: typing.Callable[[T, dict], bool],
        event_scheme: typing.Optional[
            typing.Union[
                EventScheme,
                typing.Tuple[str, typing.Type[T]]
            ]
        ] = None,
    ):
        self.func = func
        if isinstance(event_scheme, tuple):
            event_scheme = EventScheme(*event_scheme)
        self.event_scheme = event_scheme

    async def check(self, event: dict, ctx: dict) -> bool:
        if self.event_scheme:
            if self.event_scheme.name not in event:
                return False
            event = self.event_scheme.dataclass(**event[self.event_scheme.name])
        return self.func(event, ctx)


class CallbackDataEq(ABCRule):
    def __init__(self, value: str):
        self.value = value

    async def check(self, event: dict, ctx: dict) -> bool:
        return event["callback_query"].get("data") == self.value


class CallbackDataJsonEq(ABCRule):
    def __init__(self, d: dict):
        self.d = d

    async def check(self, event: dict, ctx: dict) -> bool:
        if "data" not in event["callback_query"]:
            return False
        try:
            return json.loads(event["callback_query"]["data"]) == self.d
        except:
            return False


__all__ = (
    ABCRule,
    ABCMessageRule,
    AndRule,
    OrRule,
    IsMessage,
    Text,
    Markup,
    IsPrivate,
    IsChat,
    FuncRule,
    CallbackDataEq,
    CallbackDataJsonEq,
)
