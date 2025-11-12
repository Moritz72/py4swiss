from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from py4swiss.dynamicuint import DynamicUint

W = TypeVar("W")

class ComputerBase(Generic[W], ABC):
    """
    This class implements the Blossom algorithm for computing a maximum weight matching in a general graph with
    efficient update of weights in C++.

    The Blossom algorithm finds a matching that maximizes the sum of the edge weights while ensuring that each vertex is
    incident to at most one matched edge. This implementation supports dynamically adding vertices, setting edge
    weights, and retrieving optimal matchings. Note that this implementation treats edge weights of 0 as if there was no
    edge to begin with.
    """

    def __init__(self, size: int, edge_weight: W) -> None:
        """
        Initialize the computer given a maximum size for edge weights as well as a maximum number of vertices. Note that
        this includes a 2-bit margin for the matching routine.
        """
        ...

    @abstractmethod
    def size(self) -> int:
        """Return the number of vertices in the graph."""
        ...

    @abstractmethod
    def add_vertex(self) -> None:
        """Add a new vertex to the graph."""
        ...

    @abstractmethod
    def set_edge_weight(self, u: int, v: int, weight: W) -> None:
        """
        Set the edge weight between the vertices with the given indices to the given edge weight and marks the first
        vertex as 'to be updated' when computing a matching.
        """
        ...

    @abstractmethod
    def compute_matching(self) -> None:
        """
        Compute a maximum weight matching by updating the previous matching for all edges which are marked as
        'to be updated'.
        """
        ...

    @abstractmethod
    def get_matching(self) -> list[int]:
        """
        Return the current matching as a list of integers which has length equal to the number of vertices in the graph.
        For each vertex u, matching[u] is the index of the vertex it is matched with, or its own index if the vertex is
        unmatched.
        """
        ...

class ComputerBurstein(ComputerBase[int]):
    def __init__(self, size: int, edge_weight: int) -> None: ...
    def size(self) -> int: ...
    def add_vertex(self) -> None: ...
    def set_edge_weight(self, u: int, v: int, weight: int) -> None: ...
    def compute_matching(self) -> None: ...
    def get_matching(self) -> list[int]: ...

class ComputerDutchValidity(ComputerBase[int]):
    def __init__(self, size: int, edge_weight: int) -> None: ...
    def size(self) -> int: ...
    def add_vertex(self) -> None: ...
    def set_edge_weight(self, u: int, v: int, weight: int) -> None: ...
    def compute_matching(self) -> None: ...
    def get_matching(self) -> list[int]: ...

class ComputerDutchOptimality(ComputerBase[DynamicUint]):
    def __init__(self, size: int, edge_weight: DynamicUint) -> None: ...
    def size(self) -> int: ...
    def add_vertex(self) -> None: ...
    def set_edge_weight(self, u: int, v: int, weight: DynamicUint) -> None: ...
    def compute_matching(self) -> None: ...
    def get_matching(self) -> list[int]: ...
