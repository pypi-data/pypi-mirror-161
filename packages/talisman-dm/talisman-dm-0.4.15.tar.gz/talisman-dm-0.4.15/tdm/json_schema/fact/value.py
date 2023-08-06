from typing import Any, Dict

from typing_extensions import Literal

from tdm.abstract.datamodel import AbstractFact, FactType
from tdm.datamodel.fact import ValueFact
from tdm.json_schema.fact.common import AbstractFactModel, FactFactory


class ValueFactModel(AbstractFactModel):
    fact_type: Literal[FactType.VALUE] = FactType.VALUE

    def to_value(self, mapping: Dict[str, AbstractFact]) -> Any:
        return self.value

    @property
    def fact_factory(self) -> FactFactory:
        return ValueFact

    @classmethod
    def build_value(cls, value: Any) -> Any:
        return value
