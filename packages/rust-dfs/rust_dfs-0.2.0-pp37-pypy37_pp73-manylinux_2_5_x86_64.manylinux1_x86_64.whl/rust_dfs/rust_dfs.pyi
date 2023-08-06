from typing import List, Tuple, Union, Optional

T_InputSet = List[Tuple[Union[str, None], Union[str, None]]]

class InputSet(object):
    def __init__(self, inputs: T_InputSet) -> None: ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...

class Primitive(object):
    def __init__(
        self,
        name: str,
        module: str,
        function_type: str,
        commutative: bool,
        input_sets: T_InputSet,
        return_type: Tuple[str, str],
    ) -> None: ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...

class Feature(object):
    def __init__(
        self,
        name: str,
        lt: str,
        st: str,
        base_features: Optional[List[Feature]] = None,
        generating_primitive: Optional[Primitive] = None,
    ) -> None: ...
    def __str__(self) -> str: ...
    def __repr__(self) -> str: ...

def generate_features(
    features: List[Feature], primitives: List[Primitive]
) -> List[Feature]: ...
def compare_featuresets(
    features1: List[Feature], features2: List[Feature]
) -> Tuple[List[Feature], List[Feature]]: ...
