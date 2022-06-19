# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import pygame
from game import Game

g = Game()

if __name__ == '__main__':
    while g.running:
        g.game_loop()


