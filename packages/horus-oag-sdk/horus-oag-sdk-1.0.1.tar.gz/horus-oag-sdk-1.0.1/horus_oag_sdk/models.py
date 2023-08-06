from collections import defaultdict
from typing import List, Callable, Dict
from dataclasses import dataclass, field

from .constants import EXECUTION_STEPS

@dataclass
class HorusOAGEngineRunningConfig:
    ...


@dataclass
class ExtensionInputParams:
    name: str
    type: type
    default: object = None
    required: bool = False

@dataclass
class ExtensionDependencies:
    step: Dict[str, List[str]]

@dataclass
class Extension:
    name: str
    version: str
    description: str
    module_object: object
    package_name: str
    execution_steps: Dict[str, str]
    input_params: List[ExtensionInputParams | dict] = field(default_factory=list)
    dependencies: Dict[str, list] = field(default_factory=dict)
    execution_steps_callables: Dict[str, Callable] = field(default_factory=dict)

    def __post_init__(self):
        if self.input_params and type(self.input_params) is list:
            for p in self.input_params:
                if type(p) is not dict:
                    raise TypeError(f"Input params must be a list of dictionaries, got {type(p)}")

            self.input_params = [ExtensionInputParams(**v) for v in self.input_params]

@dataclass
class HorusConfig:
    extensions: Dict[str, Extension] = field(default_factory=dict)
    running_config: HorusOAGEngineRunningConfig = field(default_factory=HorusOAGEngineRunningConfig)

    def extensions_by_steps(self) -> Dict[str, List[Extension]]:
        """
        Returns a dictionary of extensions by steps.
        """
        extensions_by_steps = defaultdict(list)

        for extension in self.extensions.values():
            for step, _ in extension.execution_steps.items():
                if step not in self.valid_steps():
                    raise ValueError(f"Invalid step {step}")

                extensions_by_steps[step].append(extension)

        return extensions_by_steps

    def valid_steps(self) -> List[str]:
        return EXECUTION_STEPS

current_config = HorusConfig()

__all__ = ("current_config", "HorusConfig", "Extension", "HorusOAGEngineRunningConfig")
