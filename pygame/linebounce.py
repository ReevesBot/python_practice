#!/usr/bin/python3

import random
import pygame as pg
from pygame.locals import *
import time

BLACK = (0, 0, 0,)
GREEN = (0xB7CE42)
BLUE = (0x66AABB)
RED = (0xE84F4F)
YELLOW = (0xF07746)
MAGENTA = (0xB7416E)
CYAN = (0x6D878D)
COLOR_LIST = [GREEN, BLUE, RED, YELLOW, MAGENTA, CYAN]
SCREEN_SIZE = pg.display.Info()
LOWER_X = -SCREEN_SIZE.current_w
LOWER_Y = -SCREEN_SIZE.current_h
UPPER_X = SCREEN_SIZE.current_w
LOWER_X = SCREEN_SIZE.current_h


class Line(pg.sprite.Sprite):

    def __init__(self):
        super().__init__()
        self.color = COLOR_LIST[(random.randrange(0,6))]
        self.x_start = random.randrange(LOWER_X, UPPER_X + 1)
        self.x_end = (LOWER_X, UPPER_X + 1)
        self.y_start = (LOWER_Y, UPPER_Y + 1)
        self.y_end = (LOWER_Y, UPPER_Y + 1)
        self.thickness = 3
        self.speed = random.randrange(3,8)


    def draw_lines(self):

        #set runtime
        t_end = time.time() + 60
        done = False

        #run while the time is less that the set runtime
        while time.time() < t_end:

            # < and <
            if self.x_start < self.x_end and self.y_start < self.y_end:
                while self.x_start <= self.x_end and self.y_start <= self.y_end:
                    pg.draw.line(screen, self.color, [self.x_start, self.y_start], [self.x_start + self.speed, self.y_start + self.speed], 3)
                    self.x_start = self.x_start + self.speed
                    self.y_start = self.y_start + self.speed
                    pg.display.flip()

            # > and >
            elif self.x_start > self.x_end and self.y_start > self.y_end:
                while self.x_start >= self.x_end and self.y_start >= self.y_end:
                    pg.draw.line(screen, self.color, [self.x_start, self.y_start], [self.x_start - self.speed, self.y_start - self.speed], 3)
                    self.x_start = self.x_start - self.speed
                    self.y_start = self.y_start - self.speed
                    pg.display.flip()

            # < and >
            elif self.x_start < self.x_end and self.y_start > self.y_end:
                while self.x_start <= self.x_end and self.y_start >= self.y_end:
                    pg.draw.line(screen, self.color, [self.x_start, self.y_start], [self.x_start + self.speed, self.y_start - self.speed], 3)
                    self.x_start = self.x_start + self.speed
                    self.y_start = self.y_start - self.speed
                    pg.display.flip()

            # > and <
            elif self.x_start > self.x_end and self.y_start < self.y_end:
                while self.x_start >= self.x_end and self.y_start <= self.y_end:
                    pg.draw.line(screen, self.color, [self.x_start, self.y_start], [self.x_start - self.speed, self.y_start + self.speed], 3)
                    self.x_start = self.x_start - self.speed
                    self.y_start = self.y_start + self.speed
                    pg.display.flip()

            # = and <
            elif self.x_start == self.x_end and self.y_start < self.y_end:
                while self.x_start == self.x_end and self.y_start < self.y_end:
                    pg.draw.line(screen, self.color, [self.x_start, self.y_start], [self.x_start, self.y_start + self.speed], 3)
                    self.y_start = self.y_start + self.speed
                    pg.display.flip()

            # = and >
            elif self.x_start == self.x_end and self.y_start > self.y_end:
                while self.x_start == self.x_end and self.y_start < self.y_end:
                    pg.draw.line(screen, self.color, [self.x_start, self.y_start], [self.x_start, self.y_start - self.speed], 3)
                    self.y_start = self.y_start - self.speed
                    pg.display.flip()

            # < and =
            elif self.x_start < self.x_end and self.y_start == self.y_end:
                while self.x_start > self.x_end and self.y_start == self.y_end:
                    pg.draw.line(screen, self.color, [self.x_start, self.y_start], [self.x_start + self.speed, self.y_start], 3)
                    self.x_start = self.x_start + self.speed
                    pg.display.flip()

            # > and =
            elif self.x_start > self.x_end and self.y_start == self.y_end:
                while self.x_start > self.x_end and self.y_start == self.y_end:
                    pg.draw.line(screen, self.color, [self.x_start, self.y_start], [self.x_start - self.speed, self.y_start], 3)
                    self.x_start = self.x_start - self.speed
                    pg.display.flip()

            if done == True:
                pg.quit()
            for event in pg.event.get():
                if event.type == pg.QUIT or (
                    event.type == KEYDOWN and (
                        event.key == K_ESCAPE
                        )):
                    done = True

class Game(object):

    def __init__(self):
        self.all_sprites_list = pg.sprites.Group()
        self.line = Line()
        self.all_sprites_list.add(self.line)

    def process_events(self):
        for event in pg.event.get():
            if event.type == KEYDOWN and (
                    event.key == K_ESCAPE
                    ):
                done = True

    def run_logic(self):


    def display_frames(self, screen):
        screen.fill(BLACK)
        pg.display.flip

def main():
    pg.init()

    screen = pg.display.set_mode(SCREEN_SIZE.current_w, SCREEN_SIZE.current_h)
    pg.mouse.set_visible(False)

    done = False
    clock = pygame.time.Clock

    game = Game()

    while not done:

        done = game.process_events()

        game.run_logic()

        game.display_frame(screen)

    pg.quit()


while __name__ == "__main__";
    main()

    #screen.fill(BLACK)
    #draw_lines()

