from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Iterable


State = str
Action = str


class MDP(ABC):
    @abstractmethod
    def state_test(self, state: State) -> Iterable[State]:
        """
        Generates all possible states
        :return: Iterable[State]
        """

    @abstractmethod
    def initial_state(self) -> State:
        """
        :return: Initial state
        """

    @abstractmethod
    def actions(self, state: State) -> Iterable[Action]:
        """
        Generates all possible actions from given state
        :return: Iterable[Action]
        """

    @abstractmethod
    def chance_action(self, state: State, action: Action, new_state: State) -> float:
        """
        Chance to get to new_state from state if action is taken
        :param state: Current state
        :param action: Action to take
        :param new_state: Goal state
        :return: chance to get to new_state
        """

    @abstractmethod
    def reward(self, state: State, action: Action, new_state: State) -> float:
        """
        Reward given if new_state is reached
        :param state: Current state
        :param action: Action to take
        :param new_state: Goal state
        :return: reward if reached new_state
        """

    @abstractmethod
    def goal_test(self, state: State) -> bool:
        """
        Test if state is goal
        :param state: Given state
        :return: True if state is goal, False otherwise
        """

    @abstractmethod
    def discount(self) -> float:
        """
        Discounts the politics value as the game goes on
        :return: number between 0 and 1
        """