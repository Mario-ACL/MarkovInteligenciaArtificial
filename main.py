from politicasYcalculadores import (
    dc_utilidad_empirica,
    dc_politica_random,
    auto_gameplay,
    poleval,
    dicey_utilidad_empirica,
    dc_politica_valiter,
    Game)


# DICEY-------------------------------------

print("Juego de dados-----------------------")
reward1, reward2 = dicey_utilidad_empirica()
print(f"Promedio de politicas: Quedarse: {reward1}, Salir: {reward2}\n\n")


# DUNGEON CRAWLER---------------------------
# Poleval y valiter se encuentran en politicasYcalculadores.py
print("Dungeon Crawler----------------------")
map1 = [[0, 0, 0, 1], [0, "w", 0, -1], ["p", 0, 0, 0]]
map2 = [[0, 0, -50, 20], ["p", 0, -50, 0], [2, 0, 0, 0]]

reward1, chance1 = dc_utilidad_empirica(map1, 100, auto_gameplay)
reward2, chance2 = dc_utilidad_empirica(map2, 100, auto_gameplay)

print("Politica Random:")
print(f"Utilidad promedio mapa 1 en 100 repeticiones: (Puntaje: {reward1})")
print(f"Utilidad promedio mapa 2 en 100 repeticiones: (Puntaje: {reward2})\n")

reward1 = dc_politica_valiter(map1, 100)
reward2 = dc_politica_valiter(map2, 100)
# Si quiere cambiar el discount tiene que ir a dungeon_crawler.py y en DungeonCrawler(MDP)
# Ir al return de discount
print("Politica Valiter con discount = 1:")
print(f"Utilidad promedio mapa 1 en 100 repeticiones: (Puntaje: {reward1})")
print(f"Utilidad promedio mapa 2 en 100 repeticiones: (Puntaje: {reward2})\n")

poleval_dict1 = poleval(Game(map1), dc_politica_random)
poleval_dict2 = poleval(Game(map2), dc_politica_random)

# print("Uso de poleval con politica random:")
# print(f"Utilidad de random con mapa 1: {poleval_dict1}")
# print(f"Utilidad de random con mapa 2: {poleval_dict2}")

# Si quieres jugar el juego a mano
# dc_gameplay(map1)
