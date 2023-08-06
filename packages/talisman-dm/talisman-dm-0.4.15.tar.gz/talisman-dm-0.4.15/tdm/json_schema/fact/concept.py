from typing import Any, Dict

from typing_extensions import Literal

from tdm.abstract.datamodel import AbstractFact, FactType
from tdm.datamodel.fact import ConceptFact
from tdm.json_schema.fact.common import AbstractFactModel, FactFactory


class ConceptFactModel(AbstractFactModel):
    fact_type: Literal[FactType.CONCEPT] = FactType.CONCEPT

    def to_value(self, mapping: Dict[str, AbstractFact]) -> Any:
        return self.value

    @property
    def fact_factory(self) -> FactFactory:
        return ConceptFact

    @classmethod
    def build_value(cls, value: Any) -> Any:
        return value
