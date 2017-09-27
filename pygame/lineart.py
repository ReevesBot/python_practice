#!/usr/bin/python3

import random
import pygame as pg
from pygame.locals import *
import time

pg.init()

BLACK = (0, 0, 0,)
GREEN = (0xB7CE42)
BLUE = (0x66AABB)
RED = (0xE84F4F)
YELLOW = (0xF07746)
MAGENTA = (0xB7416E)
CYAN = (0x6D878D)
COLOR_LIST = [GREEN, BLUE, RED, YELLOW, MAGENTA, CYAN]

screen_size = pg.display.Info()
screen = pg.display.set_mode((screen_size.current_w, screen_size.current_h))
pg.mouse.set_visible(False)

done = False
clock = pg.time.Clock()

def draw_lines():

    t_end = time.time() + 10
    lower_x = -screen_size.current_w
    lower_y = -screen_size.current_h
    upper_x = screen_size.current_w
    upper_y = screen_size.current_h
    done = False

    while time.time() < t_end:
        rand_color = random.randrange(0, 6)
        color = COLOR_LIST[rand_color]
        x_start = random.randrange(lower_x, upper_x)
        x_end = random.randrange(lower_x, upper_x)
        y_start = random.randrange(lower_y, upper_y)
        y_end = random.randrange(lower_y, upper_y)
        pg.draw.line(screen, color, [x_start, y_start], [x_end, y_end], 3)
        pg.display.flip()
        time.sleep(.06)
        if done == True:
            pg.quit()
        for event in pg.event.get():
            if event.type == pg.QUIT or (
                    event.type == KEYDOWN and (
                        event.key == K_ESCAPE
                        )):
                done = True

while not done:

    for event in pg.event.get():
        if event.type == pg.QUIT or (
                event.type == KEYDOWN and (
                    event.key == K_ESCAPE
                    )):
            done = True

    screen.fill(BLACK)
    draw_lines()

pg.quit()
