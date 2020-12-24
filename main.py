import pygame
from random import randint
import os
import sys

pygame.init()


class Board:
    # создание поля
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [[0] * width for _ in range(height)]
        # значения по умолчанию
        self.left = 20
        self.top = 20
        self.cell_size = 40

    def render(self, screen):
        for y in range(self.height):
            for x in range(self.width):
                pygame.draw.rect(screen, pygame.Color(50, 0, 255), (
                    x * self.cell_size + self.left, y * self.cell_size + self.top, self.cell_size,
                    self.cell_size), 1)


class Ships:
    def __init__(self, x_board, y_board, screen):
        self.x_board = x_board
        self.y_board = y_board
        self.screen = screen
        self.ships = []

    def render(self):
        if len(self.ships) == 0:
            for i in range(4):
                x = randint(0, 9)
                y = randint(0, 9)

                pygame.draw.rect(self.screen, 'black', (self.x_board + x * 40, self.y_board + y * 40, 40, 40))
                self.ships.append([x, y])
        else:
            for i in self.ships:
                pygame.draw.rect(self.screen, 'black', (self.x_board + i[0] * 40, self.y_board + i[1] * 40, 40, 40))



# Основная функция
def main():
    pygame.init()
    size = 1000, 700
    screen = pygame.display.set_mode(size)
    pygame.display.set_caption('Sea Battle')

    # игровое поле 10 на 20
    board = Board(10, 10)
    hum_ships = Ships(20, 20, screen)
    clock = pygame.time.Clock()
    f = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill('white')
        board.render(screen)
        hum_ships.render()

        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    main()