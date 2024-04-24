from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Iterable, Optional, Callable

State = Any
Action = Any


class SearchProblem(ABC):
    @abstractmethod
    def state_test(self, value: Any) -> bool:
        """
        Tests if the given value is a state.
        """
        ...

    @abstractmethod
    def action_test(self, value: Any) -> bool:
        """
        Test if the given value is an action.
        """
        ...

    @abstractmethod
    def initial_state(self) -> State:
        """
        Returns the initial state.
        """
        ...

    @abstractmethod
    def goal_test(self, state: State) -> bool:
        """
        Test if the given state is final
        """
        ...

    @abstractmethod
    def actions(self, state: State) -> Iterable[Action]:
        """
        Returns the actions that can be
        performed in the given state.
        """
        ...

    @abstractmethod
    def state_from(self, state: State, action: Action) -> State:
        """
        Returns the state that results from
        performing the given action in the
        given state.
        """
        ...

    @abstractmethod
    def cost_from(self, state: State, action: Action) -> float:
        """
        Returns the cost that results from
        performing the given action in the
        given state.
        """
        ...

    def path_cost(
            self, accumulated: float, state1: State, action: Action, state2: State
    ) -> float:
        return accumulated + self.cost_from(state1, action)

    def state_value(self, state: State) -> Any:
        raise NotImplementedError


class MagicBusProblem(SearchProblem):
    def __init__(self, n: int):
        assert n >= 1, "Number of blocks should be at least one"
        self.n = n

    def state_test(self, value: Any) -> bool:
        """
        Tests if the given value is a state.
        """
        return isinstance(value, int) and 1 <= value <= self.n

    def action_test(self, value: Any) -> bool:
        """
        Test if the given value is an action.
        """
        return value in ["walk", "ride"]

    def initial_state(self) -> State:
        """
        Returns the initial state.
        """
        return 1

    def goal_test(self, state: State) -> bool:
        """
        Test if the given state is final
        """
        return state == self.n

    def actions(self, state: State) -> Iterable[Action]:
        """
        Returns the actions that can be
        performed in the given state.
        """
        a = []
        if state < self.n:
            a.append("walk")
        if 2 * state <= self.n:
            a.append("ride")
        return a

    def state_from(self, state: State, action: Action) -> State:
        """
        Returns the state that results from
        performing the given action in the
        given state.
        """
        if action == "walk":
            return state + 1
        if action == "ride":
            return 2 * state
        raise ValueError("Malformed action")

    def cost_from(self, state: State, action: Action) -> float:
        """
        Returns the cost that results from
        performing the given action in the
        given state.
        """
        if action == "walk":
            return 1
        if action == "ride":
            return 2
        raise ValueError("Malformed action")


class SearchNode:
    def __init__(
            self,
            state: State,
            parent: Optional[SearchNode] = None,
            action: Optional[Action] = None,
            cost: float = 0,
    ):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost
        self.depth = 0 if parent is None else parent.depth + 1

    def __repr__(self) -> str:
        return f"<Node {self.action} -> {self.state}>"

    def expand(self, problem: SearchProblem) -> Iterable[SearchNode]:
        def child_node(action: Action) -> SearchNode:
            next_state = problem.state_from(self.state, action)
            next_cost = problem.path_cost(
                self.cost,
                self.state,
                action,
                next_state,
            )
            return SearchNode(
                next_state,
                self,
                action,
                next_cost,
            )

        return [child_node(action) for action in problem.actions(self.state)]

    def path(self) -> list[SearchNode]:
        node = self
        trace = []
        while node is not None:
            trace.append(node)
            node = node.parent
        trace.reverse()
        return trace

    def actions(self) -> list[Action]:
        return [node.action for node in self.path()[1:]]

    def __lt__(self, other):
        return self.state < other.state


def backtracking_tree_search(problem: SearchProblem) -> Optional[SearchNode]:
    best_node = SearchNode(None, cost=float("inf"))

    def expand_all(node):
        nonlocal best_node
        if problem.goal_test(node.state) and node.cost < best_node.cost:
            best_node = node
            return None
        for next_node in node.expand(problem):
            expand_all(next_node)

    expand_all(SearchNode(problem.initial_state()))
    if best_node.state is None:
        return None
    return best_node


def depth_first_tree_search(problem: SearchProblem) -> Optional[SearchNode]:
    frontier = [SearchNode(problem.initial_state())]
    while frontier:
        node = frontier.pop()
        if problem.goal_test(node.state):
            return node
        frontier.extend(node.expand(problem))
    return None


def breadth_first_tree_search(problem: SearchProblem) -> Optional[SearchNode]:
    frontier = [SearchNode(problem.initial_state())]
    while frontier:
        node = frontier.pop(0)
        if problem.goal_test(node.state):
            return node
        frontier.extend(node.expand(problem))
    return None


class SearchFrontier(ABC):
    @abstractmethod
    def is_empty(self) -> bool:
        ...

    @abstractmethod
    def insert(self, node: SearchNode) -> None:
        ...

    @abstractmethod
    def extract(self) -> SearchNode:
        ...

    def insert_many(self, nodes: Iterable[SearchNode]) -> None:
        for node in nodes:
            self.insert(node)


def tree_search(
        problem: SearchProblem, make_frontier: Callable[[], SearchFrontier]
) -> Optional[SearchNode]:
    frontier = make_frontier()
    frontier.insert(SearchNode(problem.initial_state()))
    while not frontier.is_empty():
        node = frontier.extract()
        if problem.goal_test(node.state):
            return node
        frontier.insert_many(node.expand(problem))
    return None


class StackFrontier(SearchFrontier):
    def __init__(self):
        self.stack = []

    def is_empty(self) -> bool:
        return len(self.stack) == 0

    def insert(self, node: SearchNode) -> None:
        self.stack.append(node)

    def extract(self) -> SearchNode:
        return self.stack.pop()

    def insert_many(self, nodes: Iterable[SearchNode]) -> None:
        self.stack.extend(nodes)


class QueueFrontier(SearchFrontier):
    def __init__(self):
        self.queue = []

    def is_empty(self) -> bool:
        return len(self.queue) == 0

    def insert(self, node: SearchNode) -> None:
        self.queue.append(node)

    def extract(self) -> SearchNode:
        return self.queue.pop(0)

    def insert_many(self, nodes: Iterable[SearchNode]) -> None:
        self.queue.extend(nodes)


import heapq


class PriorityFrontier(SearchFrontier):
    def __init__(self, eval: Callable[[SearchNode], float]):
        self.pq = []
        self.eval = eval

    def is_empty(self) -> bool:
        return len(self.pq) == 0

    def insert(self, node: SearchNode) -> None:
        priority = self.eval(node)
        heapq.heappush(self.pq, (priority, node))

    def extract(self) -> SearchNode:
        _, node = heapq.heappop(self.pq)
        return node


class DepthFirstFrontier(PriorityFrontier):
    def __init__(self):
        super().__init__(lambda node: -node.depth)


class BreadthFirstFrontier(PriorityFrontier):
    def __init__(self):
        super().__init__(lambda node: node.depth)


class UniformCostFrontier(PriorityFrontier):
    def __init__(self):
        super().__init__(lambda node: node.cost)


from timeit import default_timer as timer


def elapsed(thunk):
    start = timer()
    val = thunk()
    end = timer()
    return end - start, val


def test(
        problem: SearchProblem, solve: Callable[[SearchProblem], Optional[SearchNode]]
) -> None:
    secs, sol = elapsed(lambda: solve(problem))
    print(f"Ellapsed: {secs}s")
    if sol is None:
        print(f"No solutions exist!")
        return
    print(f"Actions: {sol.actions()}")
    print(f"Cost: {sol.cost}")
    return


if __name__ == "__main__":
    p = MagicBusProblem(50)
    print("\nBACKTRACKING")
    test(p, lambda p: backtracking_tree_search(p))

    print("\nDEPTH-FIRST (hardcoded stack)")
    test(p, lambda p: depth_first_tree_search(p))

    print("\nBREADTH-FIRST (hardcoded queue)")
    test(p, lambda p: breadth_first_tree_search(p))

    print("\nDEPTH-FIRST (simple frontier)")
    test(p, lambda p: tree_search(p, StackFrontier))

    print("\nBREADTH-FIRST (simple frontier)")
    test(p, lambda p: tree_search(p, QueueFrontier))

    print("\nDEPTH-FIRST (priority frontier)")
    test(p, lambda p: tree_search(p, DepthFirstFrontier))

    print("\nBREADTH-FIRST (priority frontier)")
    test(p, lambda p: tree_search(p, BreadthFirstFrontier))

    print("\nDIJKSTRA (uniform cost frontier)")
    test(p, lambda p: tree_search(p, UniformCostFrontier))
