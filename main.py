import pygame
import random
import os
import sys

pygame.init()


block_size = 40
left_hum = 20
top_hum = 20
left_pc = 500


class Board:
    # создание поля
    def __init__(self, width, height, left, top):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]

        self.left = left
        self.top = top
        self.cell_size = 40

    def render(self, screen):
        for y in range(1, self.height + 1):
            for x in range(1, self.width + 1):
                pygame.draw.rect(screen, pygame.Color(50, 0, 255), (
                    x * self.cell_size + self.left, y * self.cell_size + self.top, self.cell_size,
                    self.cell_size), 1)


# класс кораблей
class Ships:
    def __init__(self):
        self.free_place = set((i, j) for i in range(1, 11) for j in range(1, 11))
        self.ships_set = set()
        self.ships = self.populate_grid()

    # начальна позиция
    def start_pos(self, free_place):
        x_or_y = random.randint(0, 1)
        str_rev = random.choice((-1, 1))
        x, y = random.choice(tuple(free_place))
        return x, y, x_or_y, str_rev

    # добавить корабль
    def add_ship(self, len_ship, free_place):
        ship_coordinates = []
        x, y, ver_or_hor, str_rev = self.start_pos(free_place)
        for _ in range(len_ship):
            ship_coordinates.append((x, y))
            if not ver_or_hor:
                if (x <= 1 and str_rev == -1) or (x >= 10 and str_rev == 1):
                    str_rev *= -1
                    x = ship_coordinates[0][0] + str_rev
                else:
                    x = ship_coordinates[-1][0] + str_rev
            else:
                if (y <= 1 and str_rev == -1) or (y >= 10 and str_rev == 1):
                    str_rev *= -1
                    y = ship_coordinates[0][1] + str_rev
                else:
                    y = ship_coordinates[-1][1] + str_rev
        if self.is_ship_valid(ship_coordinates):
            return ship_coordinates
        return self.add_ship(len_ship, free_place)

    # проверка свободная ли клетка
    def is_ship_valid(self, new_ship):
        ship = set(new_ship)
        return ship.issubset(self.free_place)

    def update_free_place(self, new_ship):
        for elem in new_ship:
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if 0 < (elem[0] + i) < 11 and 0 < (elem[1] + j) < 11:
                        self.free_place.discard((elem[0] + i, elem[1] + j))

    def populate_grid(self):
        ships_coordinates_list = []
        for len_ship in range(4, 0, -1):
            for _ in range(5-len_ship):
                new_ship = self.add_ship(
                    len_ship, self.free_place)
                ships_coordinates_list.append(new_ship)
                for i in new_ship:
                    self.ships_set.add(i)
                self.update_free_place(new_ship)
        return ships_coordinates_list


# рисование кораблей
def draw_ships(ships, screen, vid):
    for i in ships:
        ship = sorted(i)
        x_start = ship[0][0]
        y_start = ship[0][1]
        if len(ship) > 1 and ship[0][0] == ship[1][0]:
            ship_width = block_size
            ship_height = block_size * len(ship)
        else:
            ship_width = block_size * len(ship)
            ship_height = block_size
        if vid == 'hum':
            x = block_size * x_start + left_hum
            y = block_size * y_start + top_hum
        else:
            x = block_size * x_start + left_pc
            y = block_size * y_start + top_hum

        pygame.draw.rect(screen, 'BLACK', ((x, y), (ship_width, ship_height)), width=block_size // 10)


# Основная функция
def main():
    pygame.init()

    size = 1000, 700
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Sea Battle')

    # игровое поле 10 на 20
    hum_board = Board(10, 10, 20, 20)
    pc_board = Board(10, 10, 500, 20)
    hum_ships = Ships()
    pc_ships = Ships()
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if
        screen.fill('white')
        hum_board.render(screen)
        pc_board.render(screen)
        draw_ships(hum_ships.ships, screen, 'hum')
        draw_ships(pc_ships.ships, screen, 'pc')

        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    main()