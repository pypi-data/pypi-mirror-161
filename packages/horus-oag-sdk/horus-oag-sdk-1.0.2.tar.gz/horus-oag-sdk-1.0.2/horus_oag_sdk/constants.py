from enum import Enum

class ExecutionSteps(Enum):
    """
    Enum for the execution steps.
    """
    INPUT = "input"
    AGGREGATE = "aggregate"
    MODIFY = "modify"
    DROP = "drop"
    GENERATION = "generation"


EXECUTION_STEPS = [
    "input",
    "aggregation",
    "modify",
    "drop",
    "generation"
]
