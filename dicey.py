from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Iterable, Optional, Callable
import random

State = str
Action = str


# class MDP(ABC):
#     @abstractmethod
#     def state_test(self, state: State) -> Iterable[State]:
#         """
#         Generates all possible states
#         :return: Iterable[State]
#         """
#     @abstractmethod
#     def initial_state(self) -> State:
#         """
#         :return: Initial state
#         """
#     @abstractmethod
#     def actions(self, state: State) -> Iterable[Action]:
#         """
#         Generates all possible actions from given state
#         :return: Iterable[Action]
#         """
#     @abstractmethod
#     def chance_action(self, state: State, action: Action, new_state: State) -> float:
#         """
#         Chance to get to new_state from state if action is taken
#         :param state: Current state
#         :param action: Action to take
#         :param new_state: Goal state
#         :return: chance to get to new_state
#         """
#     @abstractmethod
#     def reward(self, state: State, action: Action, new_state: State) -> float:
#         """
#         Reward given if new_state is reached
#         :param state: Current state
#         :param action: Action to take
#         :param new_state: Goal state
#         :return: reward if reached new_state
#         """
#     @abstractmethod
#     def goal_test(self, state: State) -> bool:
#         """
#         Test if state is goal
#         :param state: Given state
#         :return: True if state is goal, False otherwise
#         """
#     @abstractmethod
#     def discount(self) -> int:
#         """
#         No idea
#         :return: number between 0 and 1
#         """


class Dice_Game(MDP):
    def state_test(self, state) -> Iterable[State]:
        if state == "juega" or state == "fin":
            return state
        raise ValueError(f"Invalid state: {state}")

    def initial_state(self) -> State:
        return State("juega")

    def actions(self, state: State) -> Iterable[Action]:
        return [Action("quedarte"), Action("salir")]

    def chance_action(self, state: State, action: Action, new_state: State) -> float:
        if state == "juega" and action == "quedarte" and new_state == "juega":
            return 2/3
        if state == "juega" and action == "quedarte" and new_state == "fin":
            return 1/3
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

    def discount(self) -> int:
        return 1

# El profe lo escribio con esos argumentos
# def politica_quedarte(mdp, s):
#     return "quedarte"


def politica_quedarte():
    return "quedarte"

def politica_salir():
    return "salir"


def play(score, politica, dicey):
    state = dicey.initial_state()
    while not dicey.goal_test(state):
        score += dicey.reward(state, politica, "fin")
        choice = random.random()
        if dicey.chance_action(state, politica, "juega") >= choice:
            state = "juega"
        else:
            state = "fin"
    return score


def game(politica):
    dicey = Dice_Game()
    score = 0
    score = play(score, politica, dicey)
    return score


print(game(politica_quedarte()))
median_quedarte = 0
median_salir = 0
for _ in range(100):
    median_quedarte += game(politica_quedarte())
    median_salir += game(politica_salir())

print(f"Promedio: Quedarte:{median_quedarte/100}, Salir:{median_salir/100}")

