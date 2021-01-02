import pygame
import random
import copy
import os

pygame.init()

pc_blocks_fire = set((a, b) for a in range(1, 11) for b in range(1, 11))
around_pc_hit = set()
hit_blocks = set()
hit_blocks_hum = set()
dot = set()
pc_dot = set()
hit_blocks_for_pc_shoot = set()
last_hits = []
destroyed_ships_hum = []
destroyed_ships_pc = []


# создание поля
class Board:
    def __init__(self, width, height, left, top, signature):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        self.signature = signature

        self.left = left - 40
        self.top = top - 40
        self.cell_size = 40
        self.ybox = [str(i) for i in range(1, 11)]
        self.xbox = ['А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж', 'З', 'И']

    def render(self, screen):
        for y in range(1, self.height + 1):
            for x in range(1, self.width + 1):
                pygame.draw.rect(
                    screen, pygame.Color(50, 0, 255),
                    (x * self.cell_size + self.left, y * self.cell_size + self.top, self.cell_size, self.cell_size), 1)

        # пронумеруем клетки
        for i in range(1, 11):
            font = pygame.font.Font(None, 30)
            text = font.render(self.xbox[i - 1], 2, 'black')
            screen.blit(text, (self.cell_size * i + self.left + 10, self.top + 20))

            font2 = pygame.font.Font(None, 30)
            text2 = font2.render(self.ybox[i - 1], 2, 'black')
            screen.blit(text2, (self.left + 10, self.cell_size * i + self.top + 10))

        # назввание игрока
        font = pygame.font.Font(None, 50)
        text = font.render(self.signature, 2, 'black')
        screen.blit(
            text, ((self.left + 40 + (self.cell_size*10/2)) - text.get_width()//2,
                   self.top + 40 + self.cell_size * 10 + text.get_height()//2))


# класс кораблей
class Ships:
    def __init__(self):
        self.free_place = set((i, j) for i in range(1, 11) for j in range(1, 11))
        self.ships_set = set()
        self.ships = self.populate_board()

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

        if set(ship_coordinates).issubset(self.free_place):
            return ship_coordinates
        return self.add_ship(len_ship, free_place)

    def update_free_place(self, new_ship):
        for elem in new_ship:
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if 0 < (elem[0] + i) < 11 and 0 < (elem[1] + j) < 11:
                        self.free_place.discard((elem[0] + i, elem[1] + j))

    def populate_board(self):
        ships_coordinates = []
        for len_ship in range(4, 0, -1):
            for _ in range(5-len_ship):
                new_ship = self.add_ship(
                    len_ship, self.free_place)
                ships_coordinates.append(new_ship)
                for i in new_ship:
                    self.ships_set.add(i)
                self.update_free_place(new_ship)
        return ships_coordinates


pc_ships = Ships()
hum_ships = Ships()
pc_ships_working = copy.deepcopy(pc_ships.ships)
hum_ships_working = copy.deepcopy(hum_ships.ships)


# рисуем корабли на экране
def draw_ships(screen, ships_coordinates_list, cell_size, left, top, btwn):
    for i in ships_coordinates_list:
        ship = sorted(i)
        x_start = ship[0][0]
        y_start = ship[0][1]

        if len(ship) > 1 and ship[0][0] == ship[1][0]:
            ship_width = cell_size
            ship_height = cell_size * len(ship)

        else:
            ship_width = cell_size * len(ship)
            ship_height = cell_size
        x = cell_size * (x_start - 1) + left
        y = cell_size * (y_start - 1) + top
        if ships_coordinates_list == hum_ships.ships:
            x += 10 * cell_size + btwn
        pygame.draw.rect(
            screen, 'black', ((x, y), (ship_width, ship_height)), width=cell_size//10)


# выстрел компьютера
def pc_shoots(set_to_shoot_from, flag=False):
    pygame.time.delay(500)
    cell_ = random.choice(tuple(set_to_shoot_from))
    pc_blocks_fire.discard(cell_)
    return hit_or_miss(cell_, hum_ships_working, True)


# проверяем попал или промахнулся
def hit_or_miss(fired_cell, opponents_ships, hum_turn, diagonal_only=True):
    for i in opponents_ships:
        if fired_cell in i:
            update_dot_hit(
                fired_cell, hum_turn, diagonal_only=True)
            ind = opponents_ships.index(i)

            if len(i) == 1:
                update_dot_hit(
                    fired_cell, hum_turn, diagonal_only=False)

            i.remove(fired_cell)

            if hum_turn:
                last_hits.append(fired_cell)
                hum_ships.ships_set.discard(fired_cell)
                update_around_pc_hit(fired_cell)
            else:
                pc_ships.ships_set.discard(fired_cell)

            if not i:
                draw_destroyed_ships(ind, opponents_ships, hum_turn)
                if hum_turn:
                    last_hits.clear()
                    around_pc_hit.clear()
                    destroyed_ships_pc.append(hum_ships.ships[ind])
                else:
                    destroyed_ships_hum.append(pc_ships.ships[ind])

            return True
    dot_if_miss(fired_cell, hum_turn)
    if hum_turn:
        update_around_pc_hit(fired_cell, False)
    return False


# добавляем точку если промах
def dot_if_miss(fired_block, hum_turn=False):
    if not hum_turn:
        dot.add(fired_block)
    else:
        dot.add((fired_block[0] + 12, fired_block[1]))
        pc_dot.add(fired_block)


def update_around_pc_hit(shot_block, hum_hits=True):
    global around_pc_hit, pc_blocks_fire
    if hum_hits and shot_block in around_pc_hit:
        new_around_last_hit = set()
        for i in range(len(last_hits)-1):
            if last_hits[i][1] == last_hits[i+1][1]:
                if 1 < last_hits[i][0]:
                    new_around_last_hit.add(
                        (last_hits[i][0] - 1, last_hits[i][1]))
                if 1 < last_hits[i+1][0]:
                    new_around_last_hit.add(
                        (last_hits[i+1][0] - 1, last_hits[i][1]))
                if last_hits[i][0] < 10:
                    new_around_last_hit.add(
                        (last_hits[i][0] + 1, last_hits[i][1]))
                if last_hits[i+1][0] < 10:
                    new_around_last_hit.add(
                        (last_hits[i+1][0] + 1, last_hits[i][1]))
            elif last_hits[i][0] == last_hits[i+1][0]:
                if 1 < last_hits[i][1]:
                    new_around_last_hit.add(
                        (last_hits[i][0], last_hits[i][1] - 1))
                if 1 < last_hits[i+1][1]:
                    new_around_last_hit.add(
                        (last_hits[i][0], last_hits[i+1][1] - 1))
                if last_hits[i][1] < 10:
                    new_around_last_hit.add(
                        (last_hits[i][0], last_hits[i][1] + 1))
                if last_hits[i+1][1] < 10:
                    new_around_last_hit.add(
                        (last_hits[i][0], last_hits[i+1][1] + 1))

        around_pc_hit = new_around_last_hit

    elif hum_hits and shot_block not in around_pc_hit:
        xhit, yhit = shot_block
        if 1 < xhit:
            around_pc_hit.add((xhit-1, yhit))
        if 1 < yhit:
            around_pc_hit.add((xhit, yhit-1))
        if xhit < 10:
            around_pc_hit.add((xhit+1, yhit))
        if yhit < 10:
            around_pc_hit.add((xhit, yhit+1))

    elif not hum_hits:
        around_pc_hit.discard(shot_block)

    around_pc_hit -= pc_dot
    around_pc_hit -= hit_blocks_for_pc_shoot
    pc_blocks_fire -= around_pc_hit
    pc_blocks_fire -= pc_dot


def update_dot_hit(shot_block, hum_turn, diagonal_only=True):
    global dot
    x, y = shot_block
    a, b = 0, 11
    if hum_turn:
        x += 12
        a += 12
        b += 12
        hit_blocks_for_pc_shoot.add(shot_block)
    hit_blocks.add((x, y))
    if x <= 10:
        hit_blocks_hum.add((x, y))
    for i in range(-1, 2):
        for j in range(-1, 2):
            if diagonal_only:
                if i != 0 and j != 0 and a < x + i < b and 0 < y + j < 11:
                    dot.add((x+i, y+j))
                    if hum_turn:
                        pc_dot.add(
                            (shot_block[0]+i, y+j))
            else:
                if a < x + i < b and 0 < y + j < 11:
                    dot.add((x+i, y+j))
                    if hum_turn:
                        pc_dot.add((shot_block[0]+i, y+j))
    dot -= hit_blocks


def draw_destroyed_ships(ind, opponents_ships_list, hum_turn, diagonal_only=False):
    if opponents_ships_list == pc_ships_working:
        ships = pc_ships.ships
    elif opponents_ships_list == hum_ships_working:
        ships = hum_ships.ships
    ship = sorted(ships[ind])
    for i in range(-1, 1):
        update_dot_hit(ship[i], hum_turn, diagonal_only)


def draw_dot(screen, dot, cell_size, left, top):
    for elem in dot:
        pygame.draw.circle(
            screen, 'black', (cell_size*(elem[0]-0.5)+left, cell_size*(elem[1]-0.5)+top), cell_size//6)


def draw_hit(screen, hit_blocks, cell_size, left, top):
    for i in hit_blocks:
        x1 = cell_size * (i[0]-1) + left
        y1 = cell_size * (i[1]-1) + top
        pygame.draw.line(
            screen, 'black', (x1, y1), (x1+cell_size, y1+cell_size), cell_size//6)
        pygame.draw.line(
            screen, 'black', (x1, y1+cell_size), (x1+cell_size, y1), cell_size//6)


def main():
    run = True
    start = True
    game_over = False
    repeat_ = False
    win = False
    hum_turn = True
    cell_size = 40
    left = 40
    top = 20
    btwn = 80
    width = 1100
    height = 700

    size = (width, height)

    screen = pygame.display.set_mode(size)
    pygame.display.set_caption("SeaBattle")

    screen.fill('white')

    pc_board = Board(10, 10, left, top, 'компьютер')
    hum_board = Board(10, 10, left + btwn + cell_size * 10, top, 'вы')
    clock = pygame.time.Clock

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if start:
                    if event.button == 1:
                        if (400 <= x <= 700) and (300 <= y <= 400):
                            start = False
                else:
                    if event.button == 1 and hum_turn:
                        if (left <= x <= left + 10 * cell_size) and (top <= y <= top + 10 * cell_size):
                            fired_block = ((x - left) // cell_size + 1, (y - top) // cell_size + 1)
                            if (fired_block in dot) or (fired_block in hit_blocks_hum):
                                pass
                            else:
                                hum_turn = hit_or_miss(
                                    fired_block, pc_ships_working, not hum_turn)

        if len(destroyed_ships_pc) == 10:
            game_over = True
        if len(destroyed_ships_hum) == 10:
            win = True

        if start:
            screen.fill('white')
            font = pygame.font.Font(None, 100)
            text = font.render('Морской бой', 1, 'blue')
            screen.blit(
                text, (width / 2 - text.get_width() // 2, height / 2 - text.get_height() // 2 - 300))

            font = pygame.font.Font(None, 80)
            text = font.render('Начать', 1, 'black')
            w = text.get_width()
            h = text.get_height()
            screen.blit(
                text, (width / 2 - w // 2, height / 2 - h // 2))
            pygame.draw.rect(
                screen, 'black', (400, 300, 300, 100), 5)
        elif game_over:
            pygame.time.delay(1000)
            screen.fill('white')
            font = pygame.font.Font(None, 100)
            text = font.render('Ты проиграл :(', 1, 'red')
            screen.blit(text, (width / 2 - text.get_width() // 2, height / 2 - text.get_height() // 2))
        elif win:
            pygame.time.delay(1000)
            screen.fill('white')
            font = pygame.font.Font(None, 100)
            text = font.render('Ты победил!', 1, 'green')
            screen.blit(
                text, (width / 2 - text.get_width() // 2, height / 2 - text.get_height() // 2))
        else:
            screen.fill('white')
            if not hum_turn:
                if around_pc_hit:
                    hum_turn = not pc_shoots(around_pc_hit)
                else:
                    hum_turn = not pc_shoots(pc_blocks_fire)

            pc_board.render(screen)
            hum_board.render(screen)

            # draw_ships(screen, pc_ships.ships, cell_size, left, top, btwn)
            draw_ships(screen, hum_ships.ships, cell_size, left, top, btwn)
            # all_sprites.draw(screen)

            draw_dot(screen, dot, cell_size, left, top)
            draw_hit(screen, hit_blocks, cell_size, left, top)
            draw_ships(screen, destroyed_ships_hum, cell_size, left, top, btwn)

        pygame.display.flip()


if __name__ == '__main__':
    main()