from enum import Enum

class ExecutionSteps(Enum):
    """
    Enum for the execution steps.
    """
    AGGREGATE = "aggregate"
    MODIFY = "modify"
    DROP = "drop"
    GENERATION = "generation"


EXECUTION_STEPS = [
    "aggregation",
    "modify",
    "drop",
    "generation"
]
