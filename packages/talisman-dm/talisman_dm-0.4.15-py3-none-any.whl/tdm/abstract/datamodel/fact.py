import uuid
from abc import ABCMeta, abstractmethod
from copy import deepcopy
from enum import Enum
from functools import total_ordering
from typing import Any, Callable, Dict, Generic, Iterable, NamedTuple, Optional, Tuple, TypeVar, Union

from tdm.abstract.datamodel.span import AbstractTalismanSpan


@total_ordering
class FactStatus(str, Enum):

    def __new__(cls, name: str, priority: int):
        obj = str.__new__(cls, name)
        obj._value_ = name
        obj.priority = priority
        return obj

    APPROVED = ("approved", 0)
    DECLINED = ("declined", 1)
    AUTO = ("auto", 2)
    HIDDEN = ("hidden", 3)
    NEW = ("new", 4)

    def __lt__(self, other: 'FactStatus'):
        if not isinstance(other, FactStatus):
            return NotImplemented
        return self.priority < other.priority


class FactType(str, Enum):
    PROPERTY = "property"
    RELATION = "relation"
    CONCEPT = "concept"
    VALUE = "value"


FactMetadata = Dict[str, Any]
FACT_CONFIDENCE = 'fact_confidence'
VALUE_CONFIDENCE = 'value_confidence'

_FactValue = TypeVar('_FactValue')
_AbstractFact = TypeVar('_AbstractFact', bound='AbstractFact')


# TODO: add Generic[_FactValue] when python >= 3.7
class ValueWithConfidence(NamedTuple):
    value: _FactValue
    confidence: Optional[float]


class AbstractFact(Generic[_FactValue], metaclass=ABCMeta):
    __slots__ = ('_id', '_mention', '_fact_type', '_status', '_type_id', '_value', '_metadata')

    def __init__(self, id_: Optional[str], fact_type: FactType, status: FactStatus, type_id: str,
                 value: Optional[Union[_FactValue, Tuple[_FactValue, ...]]] = None,
                 mention: Iterable[AbstractTalismanSpan] = None, metadata: Optional[FactMetadata] = None):
        self._id = id_ or self.generate_id()
        self._mention = tuple(mention) if mention is not None else None
        self._fact_type = fact_type
        self._status = status
        self._type_id = type_id
        self._value = deepcopy(value)
        self._metadata = deepcopy(metadata)

    @property
    def id(self) -> str:
        return self._id

    @property
    def mention(self) -> Optional[Tuple[AbstractTalismanSpan, ...]]:
        return self._mention

    @property
    def fact_type(self) -> FactType:
        return self._fact_type

    @property
    def status(self) -> FactStatus:
        return self._status

    @property
    def type_id(self) -> str:
        return self._type_id

    @property
    def value(self) -> Union[_FactValue, Tuple[_FactValue, ...]]:
        return deepcopy(self._value)

    def value_with_confidence(self) -> Union[ValueWithConfidence, Tuple[ValueWithConfidence, ...], None]:
        if not self._metadata or VALUE_CONFIDENCE not in self._metadata:
            return None

        if not isinstance(self._value, tuple):
            return ValueWithConfidence(deepcopy(self.value), self._metadata[VALUE_CONFIDENCE])
        return tuple(ValueWithConfidence(v, c) for v, c in zip(deepcopy(self._value), self._metadata[VALUE_CONFIDENCE]))

    @property
    def has_value(self) -> bool:
        return bool(self._value)

    @property
    def metadata(self) -> FactMetadata:
        return deepcopy(self._metadata)

    @property
    def fact_confidence(self) -> Optional[float]:
        return self._metadata.get(FACT_CONFIDENCE) if self._metadata is not None else None

    @property
    def has_fact_confidence(self) -> bool:
        return self.fact_confidence is not None

    @staticmethod
    def generate_id() -> str:
        return str(uuid.uuid4())

    def __eq__(self, other):
        if not isinstance(other, AbstractFact):
            return NotImplemented
        return self._id == other._id and self._mention == other._mention and self._fact_type == other._fact_type \
            and self._status == other._status and self._type_id == other._type_id and self._value == other._value

    def __hash__(self):
        return hash((self._id, self._mention, self._fact_type, self._status, self._type_id))

    @abstractmethod
    def with_changes(self: _AbstractFact, *, status: FactStatus = None, type_id: str = None,
                     value: Union[_FactValue, Tuple[_FactValue, ...]] = None,
                     mention: Tuple[AbstractTalismanSpan, ...] = None,
                     metadata: FactMetadata = None,
                     # metadata fields
                     fact_confidence: float = None,
                     value_confidence: Union[float, Tuple[float, ...]] = None) -> _AbstractFact:
        pass

    def __repr__(self):
        return f"Fact({self._id}, {self._fact_type}, {self._status}, {self._type_id}, {self._value}, " \
               f"{self._metadata}, {self._mention})"

    @staticmethod
    def update_metadata(f: Callable[..., _AbstractFact]):
        def check(self: _AbstractFact, *args, value: Union[_FactValue, Tuple[_FactValue, ...]] = None, metadata: FactMetadata = None,
                  fact_confidence: float = None,
                  value_confidence: Union[float, Tuple[float, ...]] = None,
                  **kwargs
                  ) -> _AbstractFact:
            _metadata = deepcopy(metadata) if metadata else {}

            if fact_confidence is not None:
                _metadata[FACT_CONFIDENCE] = fact_confidence

            if value_confidence is not None and value is not None:
                if isinstance(value_confidence, tuple) and isinstance(value, tuple) and (len(value_confidence) == len(value)):
                    _metadata[VALUE_CONFIDENCE] = value_confidence
                elif not isinstance(value_confidence, tuple) and not isinstance(value, tuple):
                    _metadata[VALUE_CONFIDENCE] = value_confidence
                else:
                    raise ValueError(f'value confidence length `{value_confidence}` != value length `{value}`')
            elif self._metadata and VALUE_CONFIDENCE in self._metadata:
                _metadata[VALUE_CONFIDENCE] = None if value is not None else self._metadata[VALUE_CONFIDENCE]

            return f(self, *args, value=value, metadata=_metadata if _metadata else None, **kwargs)

        return check


_SourceFactType = TypeVar('_SourceFactType', bound=AbstractFact)
_TargetFactType = TypeVar('_TargetFactType', bound=AbstractFact)


class AbstractLinkValue(Generic[_SourceFactType, _TargetFactType], metaclass=ABCMeta):
    def __init__(self, property_id: Optional[str], from_fact: _SourceFactType, to_fact: _TargetFactType):
        self.validate_slots(from_fact, to_fact)
        self._property_id = property_id
        self._from_fact = from_fact
        self._to_fact = to_fact

    @property
    def property_id(self) -> Optional[str]:
        return self._property_id

    @property
    def from_fact(self) -> _SourceFactType:
        return self._from_fact

    @property
    def to_fact(self) -> _TargetFactType:
        return self._to_fact

    def update_value(self, id2fact: Dict[str, AbstractFact]):
        return type(self)(self._property_id, id2fact[self._from_fact.id], id2fact[self._to_fact.id])

    @classmethod
    @abstractmethod
    def validate_slots(cls, source: _SourceFactType, target: _TargetFactType):
        pass

    def __eq__(self, other):
        if not isinstance(other, AbstractLinkValue):
            return NotImplemented
        return self._property_id == other._property_id and self._from_fact == other._from_fact and self._to_fact == self._to_fact

    def __hash__(self):
        return hash((self._property_id, self._from_fact, self._to_fact))

    def __repr__(self):
        return f"PropertyLinkValue({self._property_id}, {self.from_fact.id}, {self.to_fact.id})"
