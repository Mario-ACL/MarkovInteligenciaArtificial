from __future__ import annotations
from typing import Iterable
from MDP import MDP

State = any
Action = any


class DiceGame(MDP):
    def state_test(self, state) -> Iterable[State]:
        if state == "juega" or state == "fin":
            return state
        raise ValueError(f"Invalid state: {state}")

    def initial_state(self) -> State:
        return "juega"

    def actions(self, state: State) -> Iterable[Action]:
        return [Action("quedarte"), Action("salir")]

    def chance_action(self, state: State, action: Action, new_state: State) -> float:
        if state == "juega" and action == "quedarte" and new_state == "juega":
            return 2 / 3
        if state == "juega" and action == "quedarte" and new_state == "fin":
            return 1 / 3
        if state == "juega" and action == "salir" and new_state == "fin":
            return 1
        if state == "juega" and action == "salir" and new_state == "juega":
            return 0
        raise ValueError(f"Chance action error")

    def reward(self, state: State, action: Action, new_state: State) -> float:
        if action == "quedarte":
            return 4
        if action == "salir":
            return 10
        raise ValueError(f"Reward action error")

    def goal_test(self, state: State) -> bool:
        return True if state == "fin" else False

    def discount(self) -> float:
        return 1


# El profe lo escribió con esos argumentos
# def politica_quedarte(mdp, s):
#     return "quedarte"


