"""Provides exceptions related to Query"""

from typing import Any, Literal


class InvalidQueryStepTypeException(Exception):
    """Raised by \'validate_query_step\' if type of Query step is not 'dict'"""

    status = 400

    def __init__(self, *, step_type: Any):
        super().__init__(
            f"Query step type should be of type 'dict'. Got '{step_type}' instead"
        )


class InvalidQueryStepLenException(Exception):
    """Raised by \'validate_query_step\' if Query step has more than one item"""

    status = 400

    def __init__(self, *, step_items: tuple[str, ...]):
        super().__init__(f"Query step must have one item. Got '{step_items}' instead")


class InvalidQueryStepAttrTypeException(Exception):
    """Raised by \'validate_query_step\' if type of Query step attr is not 'dict'"""

    status = 400

    def __init__(self, *, step_attr_type: Any):
        super().__init__(
            f"Query step attr value should be of type 'dict'. Got '{step_attr_type}' instead"
        )


class InvalidQueryStepAttrLenException(Exception):
    """Raised by \'validate_query_step\' if Query step attr has more than one item"""

    status = 400

    def __init__(self, *, step_attr_items: tuple[str, ...]):
        super().__init__(
            f"Query step attr can only have one item. Got '{step_attr_items}' instead"
        )


class InvalidQueryOperTypeException(Exception):
    """Raised by \'validate_query_step\' if value of Query step attr is invalid"""

    status = 400

    def __init__(
        self,
        *,
        attr_name: str,
        attr_oper: Literal[
            "$ne",
            "$eq",
            "$gt",
            "$gte",
            "$lt",
            "$lte",
            "$all",
            "$in",
            "$nin",
            "$regex",
        ],
        attr_type: Any,
        attr_val: Any,
    ):
        super().__init__(
            f"Invalid value for Query Arg '{attr_name}' with Query Arg Oper '{attr_oper}'"
            f" expecting type '{attr_type}' but got '{attr_val}'"
        )


class UnknownQueryOperException(Exception):
    """Raised by \'validate_query_step\' if an unknown \'Query Arg\' is detected"""

    status = 400

    def __init__(
        self,
        *,
        attr_name: str,
        attr_oper: Literal[
            "$ne",
            "$eq",
            "$gt",
            "$gte",
            "$lt",
            "$lte",
            "$all",
            "$in",
            "$nin",
            "$regex",
        ],
    ):
        super().__init__(
            f"Unknown Query Arg Oper '{attr_oper}' for Query Arg '{attr_name}'"
        )
