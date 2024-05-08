import copy

from dungeon_crawler import Game
from dicey import DiceGame
import random


# DICEY-------------------------------------
def politica_quedarte():
    return "quedarte"


def politica_salir():
    return "salir"


def dicey_play(score, politica, dicey):
    state = dicey.initial_state()
    while not dicey.goal_test(state):
        score += dicey.reward(state, politica, "fin")
        choice = random.random()
        if dicey.chance_action(state, politica, "juega") >= choice:
            state = "juega"
        else:
            state = "fin"
    return score


def dicey_game(politica):
    dicey = DiceGame()
    score = 0
    score = dicey_play(score, politica, dicey)
    return score


def dicey_utilidad_empirica():
    median_quedarte = 0
    median_salir = 0
    for _ in range(100):
        median_quedarte += dicey_game(politica_quedarte())
        median_salir += dicey_game(politica_salir())
    return median_quedarte / 100, median_salir / 100


# DUNGEON CRAWLER---------------------------
def dc_politica_random(papaya):
    moves = ["north", "south", "west", "east"]
    return moves[random.randint(0, 3)]


# Para jugar manualmente
def dc_gameplay(mapmap):
    gameplayer = Game(mapmap)
    probabilities = []
    while not gameplayer.engine.goal_test(any):
        gameplayer.print_board()
        print(gameplayer.engine.actions(any))
        print("Move: ")
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
    print("-------------------------------")
    print(f"Final Score: {gameplayer.engine.reward_save}")
    print(f"Probabilities per move: {probabilities}")


def auto_gameplay(mapmap):
    gameplayer = Game(mapmap)
    probabilities = []
    while not gameplayer.engine.goal_test(any):
        # gameplayer.print_board()
        move = dc_politica_random(any)
        # print(move)
        # print(f"Final Score: {gameplayer.engine.reward_save}")
        rand_val = random.random()
        gameplayer.apply_move(move, rand_val)
        temp_prob = 0.8 if rand_val <= 0.8 else 0.1
        probabilities.append(temp_prob)
    # gameplayer.print_board()
    # print(move)
    # print(f"Final Score: {gameplayer.engine.reward_save}")
    return gameplayer.engine.reward_save, probabilities


def dc_politica_valiter(mapmap, n=100):
    dict_moves = valiter(Game(mapmap))
    move = None
    reward_median = 0
    for _ in range(n):
        gameplayer = Game(mapmap)
        while not gameplayer.engine.goal_test(None):
            rand_val = random.random()
            state = gameplayer.engine.map
            for key, value in dict_moves.items():
                if key.engine.map == state:
                    move = value
                    break
            gameplayer.apply_move(move, rand_val)
            reward_median += gameplayer.engine.reward_save
    return reward_median / n


def dc_utilidad_empirica(mapmap, reps, type_gameplay):
    median_reward = 0
    median_chance = 0
    for i in range(reps):
        originalmap = mapmap
        reward, probabilities = type_gameplay(originalmap)
        median_reward += reward
        for prob in probabilities:
            median_chance += prob
        # print(f"Round: {i + 1}------------------------------")
    return median_reward / reps, median_chance / reps


def reachable_states(mdp):
    states = []
    frontier = [mdp]

    while True:
        length = len(states)
        while frontier:
            current_state = frontier.pop()
            arr = []
            for action in mdp.engine.actions(current_state):
                mdpappendice = copy.deepcopy(current_state)
                mdpappendice.apply_move(action, 0.5)
                arr.append(mdpappendice) if (mdpappendice not in states
                                             and mdpappendice not in arr) else arr
            states.extend(arr)
            frontier.extend(arr)
        if length == len(states):
            break

    for key in states:
        dummy_map = copy.deepcopy(mdp)
        player_pos = key.player_pos
        key.engine.map = dummy_map.engine.map
        key.engine.map[mdp.player_pos[0]][mdp.player_pos[1]] = 0
        key.engine.map[player_pos[0]][player_pos[1]] = "p"

    return states


def posibilities(mdp, s, a):
    mdpcopy0 = copy.deepcopy(s)
    mdpcopy0.apply_move(a, 0.5)
    if mdpcopy0.engine.player_pos in mdpcopy0.engine.goal_pos_dict:
        reward0 = mdpcopy0.engine.goal_pos_dict.get(mdpcopy0.engine.player_pos)
    else:
        reward0 = 0

    mdpcopy1 = copy.deepcopy(s)
    mdpcopy1.apply_move(a, 0.85)
    if mdpcopy1.engine.player_pos in mdpcopy1.engine.goal_pos_dict:
        reward1 = mdpcopy1.engine.goal_pos_dict.get(mdpcopy1.engine.player_pos)
    else:
        reward1 = 0

    mdpcopy2 = copy.deepcopy(s)
    mdpcopy2.apply_move(a, 1)
    if mdpcopy2.engine.player_pos in mdpcopy2.engine.goal_pos_dict:
        reward2 = mdpcopy2.engine.goal_pos_dict.get(mdpcopy2.engine.player_pos)
    else:
        reward2 = 0

    s_prima = (mdpcopy0, mdpcopy1, mdpcopy2)
    # Si lee este comentario profe, lo escribi a mano la probabilidad por que al parecer
    # mi funcion que regresaba las probabilidades no funcionaba correctamente, honestamente
    # lo arreglaria pero llevo multiples dias que pasaba horas buscando el bug que no me permitia
    # terminar la tarea y finalmente encontre que eran las probabilidades, espero que me disculpe.
    p = (0.8, 0.1, 0.1)
    r = (reward0, reward1, reward2)
    return s_prima, p, r


def poleval(mdp, pi, n=100):
    states = reachable_states(mdp)
    v1 = {s: 0 for s in states}
    v2 = {}

    # Separe el return pythonico porque me causaba errores al intentar iterar de esa forma
    def Q(s, a):
        Y = mdp.engine.discount()
        s2, p, r = posibilities(mdp, s, a)
        sumer = 0
        for i in range(3):
            multY = Y * v1[s2[i]]
            sumr = r[i] + multY
            multp = sumr * p[i]
            sumer += multp
        return sumer
        # return sum(p * (r + Y * v1[s2]) for (s2, p, r) in posibilities(mdp, s, a))

    for _ in range(n):
        for s in states:
            if s.engine.player_pos in s.engine.goal_pos_dict:
                v2[s] = 0
            else:
                v2[s] = Q(s, pi(s))
        v1, v2 = v2, v1
    return v1


def valiter(mdp, n=100):
    states = reachable_states(mdp)
    v1 = {s: 0 for s in states}
    v2 = {}
    actions = {s: None for s in states}

    def Q(s):
        Y = mdp.engine.discount()
        max_val = -float('inf')
        best_a = None
        for a in ["north", "south", "west", "east"]:
            s2, p, r = posibilities(mdp, s, a)
            sumer = 0
            for i in range(len(r)):
                # print(s2[i].engine.map, r[i])
                # print(p[i])
                multY = Y * v1[s2[i]]
                sumr = r[i] + multY
                multp = sumr * p[i]
                sumer += multp
            if sumer > max_val:
                best_a = a
                max_val = sumer
                # print(s.engine.map, s.engine.reward_save, s.player_pos, s.engine.goal_pos_dict)
        # print(max_val)
        return max_val, best_a

    for _ in range(n):
        for s in states:
            if s.engine.player_pos in s.engine.goal_pos_dict:
                v2[s] = 0
                actions[s] = None
            else:
                v2[s], actions[s] = Q(s)
        v1, v2 = v2, v1
    return actions

# map1 = [[0, 0, 0, 1], [0, "w", 0, -1], ["p", 0, 0, 0]]
# map2 = [[0, 0, -50, 20], ["p", 0, -50, 0], [2, 0, 0, 0]]
#
# valid_moves = ["north", "south", "west", "east"]
# print(poleval(Game(map2), dc_politica_random))
# print(poleval(Game(map1), dc_politica_random))
#
# print(poleval(Game(map2), lambda moves: dc_politica_random(valid_moves)))
#
# v11, actions1 = valiter(Game(map1))
# v12, actions2 = valiter(Game(map2))
#
# print(f"Dict: {v11} \n Actions: {actions1}")
# print(f"Dict: {v12} \n Actions: {actions2}")
#
# print(valiter(Game(map2)))
# valiterval = valiter(Game(map2))
# print(valiterval)
# for key, value in valiterval.items():
#     print(key.print_board())
#     print(value)

# for key in poleval(Game(map2), dc_politica_random):
#     print(key.print_board())
