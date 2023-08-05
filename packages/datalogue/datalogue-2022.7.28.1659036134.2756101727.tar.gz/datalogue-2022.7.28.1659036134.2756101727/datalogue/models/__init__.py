from typing import Union
from datalogue.dtl_utils import SerializableStringEnum

from datalogue.errors import _enum_parse_error, DtlError


class ComparisonOperator(SerializableStringEnum):
    @staticmethod
    def parse_error(s: str) -> str:
        return _enum_parse_error("operator", s)

    @staticmethod
    def _from_payload(json: str) -> Union[DtlError, "ComparisonOperator"]:
        return SerializableStringEnum.from_str(ComparisonOperator)(json)

    @staticmethod
    def from_str(string: str) -> Union[DtlError, "ComparisonOperator"]:
        return ComparisonOperator._from_payload(string)

    LT = "<"
    LTE = "<="
    EQ = "=="
    GT = ">"
    GTE = ">="
    NE = "!="

    # aliases, from the old class "CompareOperators"
    Eq = "=="
    Heq = ">="
    Leq = "<="
    Les = "<"
    Hig = ">"
    Neq = "!="
