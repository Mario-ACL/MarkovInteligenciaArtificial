from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Iterable, Optional, Callable
import random
import copy

State = any
Action = any


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
    def reward(self, state: State, action: Action, new_state: State) -> int:
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
    def discount(self) -> int:
        """
        No idea
        :return: number between 0 and 1
        """


# Notes: Los estados estan dados por el mapa
#         El mapa tiene 4 tipos de "tiles",
#         0 = caminable,
#         > or < 0 es meta,
#         "p" = player,
#         "w" = paredes

class DungeonCrawler(MDP):
    def __init__(self, initial_map: list):
        self.map = self.state_test(initial_map)
        self.old_map = copy.deepcopy(self.map)

        self.player_pos = None
        for i, row in enumerate(self.map):
            for j, cell in enumerate(row):
                if cell == "p":
                    self.player_pos = (i, j)
                    break
            if self.player_pos is not None:
                break
        self.old_player_pos = self.player_pos

        self.goal_pos_dict = {}
        for i, row in enumerate(self.state_test(initial_map)):
            for j, cell in enumerate(row):
                if isinstance(cell, str):
                    continue
                if cell != 0:
                    self.goal_pos_dict.update({(i, j): cell})

        self.reward_save = 0

    def state_test(self, state: State) -> Iterable[State]:
        # yo le mando algo y reviso si es estado
        player = False
        goal = False
        for row in state:
            for cell in row:
                if cell == "p":
                    player = True
                elif cell == "w":
                    continue
                elif cell != 0:
                    goal = True
                    # mas rapido salir del for
                if player and goal:
                    return state

        # worst case
        raise ValueError(f"Invalid state: {state}")

    def initial_state(self) -> State:
        return self.map

    def actions(self, state: State) -> Iterable[Action]:
        return ["north", "south", "west", "east"]

    def chance_action(self, state: State, action: Action, new_state: State) -> float:
        # direccion esperada = .8, lado no esperado = .1, lado no esperado contrario = .1
        # no hay probabilidad de ir hacia atras por accidente
        # Seccion MASOMENOS asistida por ChatGPT hasta el return 0.0:
        # Determine the expected new position based on the action
        expected_chance = 0.8
        unexpected_chance = 0.1
        (i, j) = self.old_player_pos
        if action == "north":
            expected_new_position = (i - 1, j)
            left_deviation_position = (i, j - 1)
            right_deviation_position = (i, j + 1)
        elif action == "south":
            expected_new_position = (i + 1, j)
            left_deviation_position = (i, j + 1)
            right_deviation_position = (i, j - 1)
        elif action == "west":
            expected_new_position = (i, j - 1)
            left_deviation_position = (i + 1, j)
            right_deviation_position = (i - 1, j)
        elif action == "east":
            expected_new_position = (i, j + 1)
            left_deviation_position = (i - 1, j)
            right_deviation_position = (i + 1, j)
        else:
            raise ValueError("Invalid action")

        # get the REAL position of the player
        new_player_pos = None
        for i, row in enumerate(new_state):
            for j, cell in enumerate(row):
                if cell == "p":
                    new_player_pos = i, j
                    break
            if new_player_pos is not None:
                break
        # Revisa si el new_state tiene al jugador en el lugar correcto
        self.old_player_pos = new_player_pos
        if expected_new_position == new_player_pos:
            return expected_chance
        elif (left_deviation_position == new_player_pos) or (right_deviation_position == new_player_pos):
            return unexpected_chance
        # If new_state does not match any expected or deviation positions
        return 0.1

    def reward(self, state: State, action: Action, new_state: State):
        # si el nuevo estado tiene a el jugador en la meta entonces regresa el valor acorde
        if self.player_pos in self.goal_pos_dict:
            self.reward_save = self.goal_pos_dict.get(self.player_pos)

    def goal_test(self, state: State) -> bool:
        if self.reward_save != 0:
            return True
        return False

    def discount(self) -> int:
        return 1


class Game:
    def __init__(self, initial_map: list):
        self.engine = DungeonCrawler(initial_map)
        self.player_pos = self.engine.player_pos
        self.old_player_pos = self.player_pos

    def make_move(self, action: Action, chance: float) -> None:
        self.old_player_pos = self.player_pos
        if action == "north":
            if chance <= 0.8:
                self.player_pos = (self.player_pos[0] - 1, self.player_pos[1])
            else:
                # check side to move if chance failed
                if 0.9 >= chance > 0.8:
                    self.player_pos = (self.player_pos[0], self.player_pos[1] - 1)
                else:
                    self.player_pos = (self.player_pos[0], self.player_pos[1] + 1)

        if action == "south":
            if chance <= 0.8:
                self.player_pos = (self.player_pos[0] + 1, self.player_pos[1])
            else:
                # check side to move if chance failed
                if 0.9 >= chance > 0.8:
                    self.player_pos = (self.player_pos[0], self.player_pos[1] - 1)
                else:
                    self.player_pos = (self.player_pos[0], self.player_pos[1] + 1)

        if action == "west":
            if chance <= 0.8:
                self.player_pos = (self.player_pos[0], self.player_pos[1] - 1)
            else:
                # check side to move if chance failed
                if 0.9 >= chance > 0.8:
                    self.player_pos = (self.player_pos[0] - 1, self.player_pos[1])
                else:
                    self.player_pos = (self.player_pos[0] + 1, self.player_pos[1])

        if action == "east":
            if chance <= 0.8:
                self.player_pos = (self.player_pos[0], self.player_pos[1] + 1)
            else:
                # check side to move if chance failed
                if 0.9 >= chance > 0.8:
                    self.player_pos = (self.player_pos[0] - 1, self.player_pos[1])
                else:
                    self.player_pos = (self.player_pos[0] + 1, self.player_pos[1])

    def inbounds(self):
        if self.player_pos is not None and self.player_pos[0] >= 0 and self.player_pos[1] >= 0 \
                and self.player_pos[0] < 3 and self.player_pos[1] < 5 and self.engine.map[self.player_pos[0]][self.player_pos[1]] != "w":
            return True
        return False

    def apply_move(self, action: Action, chance: float):
        self.make_move(action, chance)
        if self.inbounds():
            self.engine.map[self.player_pos[0]][self.player_pos[1]] = "p"
            self.engine.map[self.old_player_pos[0]][self.old_player_pos[1]] = 0
            self.engine.player_pos = self.player_pos
            self.engine.reward(self.engine.map, action, self.engine.old_map)
        # Si el movimiento no es valido
        else:
            self.player_pos = self.old_player_pos

    def print_board(self):
        print('\n'.join('\t'.join(map(str, row)) for row in self.engine.map))


def gameplay(mapmap):
    gameplayer = Game(mapmap)
    probabilities = []
    while not gameplayer.engine.goal_test(any):
        gameplayer.print_board()
        print(gameplayer.engine.actions(any))
        move = input().lower()
        if move == "exit":
            break
        if move not in gameplayer.engine.actions(any):
            print("Invalid move")
            continue
        rand_val = random.random()
        gameplayer.apply_move(move, rand_val)
        temp_prob = gameplayer.engine.chance_action(gameplayer.engine.old_map, move, gameplayer.engine.map)
        probabilities.append(temp_prob)
        print(f"Probability: {temp_prob}")
    print("-------------------------------nor")
    print(f"Final Score: {gameplayer.engine.reward_save}")
    print(f"Probabilities per move: {probabilities}")


map1 = [[0, 0, 0, 1], [0, "w", 0, -1], ["p", 0, 0, 0]]
gameplay(map1)


# def run(MDP, pi):
#     s = MDP.initial_state()
#     rs = []
#     while not MDP.goal_test(s):
#         a = pi(s)
#         s, r = MDP.next_state(MDP, s, a)
#         rs.append(r)
#     return rs
#
#
# def next_state(MDP, s, a):
#     dardo = random.random()
#     cum_prob = 0
#     for s, r, p in MDP.transitions(s, a):
#         if dardo < cum_prob:
#             return s, r
#     raise ValueError(f"Something went wrong")
#
# MDP.transitions -> list [(s, r, p), (s, r, p), ...]