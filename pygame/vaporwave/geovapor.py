#!/usr/bin/python3

import random
import pygame as pg
from pygame.locals import *
import time

pg.init()

BLACK = (0, 0, 0,)
WHITE = (0xFFFFFF)
GREEN = (0x05FFA1)
PURPLE = (0xB967FF)
ORANGE = (0xFFA407)
YELLOW = (0xFFFB96)
PINK = (0xFF71CE)
CYAN = (0x01CDFE)
COLOR_LIST = [GREEN, PURPLE, ORANGE, YELLOW, PINK, CYAN]

screen_size = pg.display.Info()
screen = pg.display.set_mode((screen_size.current_w, screen_size.current_h))
pg.mouse.set_visible(False)

background = pg.image.load("/home/ksultanx/python_exercises/pygame/vaporwave/vaporwave.png")
background = pg.transform.scale(background, (screen_size.current_w, screen_size.current_h))
background_rect = background.get_rect()

done = False
clock = pg.time.Clock()

def draw_lines():

    #set runtime and find the edges of the screen
    t_end = time.time() + 40
    lower_x = -10 #-screen_size.current_w
    lower_y = -10 #-screen_size.current_h
    upper_x = screen_size.current_w
    upper_y = screen_size.current_h - ((screen_size.current_h // 5) + 75)
    done = False

    #run while the time is less that the set runtime
    while time.time() < t_end:
        rand_color = random.randrange(0, 6)
        color = COLOR_LIST[rand_color]
        #rand_slope = random.randrange(1, 3)
        x_slope = random.randrange(1, 2)
        y_slope = random.randrange(1, 2)
        thickness = random.randrange(1, 3)
        #generate random start and stop locations for the line
        x_start = random.randrange(lower_x, upper_x)
        x_end = random.randrange(lower_x, upper_x)
        y_start = random.randrange(lower_y, upper_y)
        y_end = random.randrange(lower_y, upper_y)

        # < and <
        if x_start < x_end and y_start < y_end:
            while x_start <= x_end and y_start <= y_end:
                pg.draw.line(screen, color, [x_start, y_start], [x_start + x_slope, y_start + y_slope], thickness)
                x_start = x_start + x_slope
                y_start = y_start + y_slope
                pg.display.flip()

        # > and >
        elif x_start > x_end and y_start > y_end:
             while x_start >= x_end and y_start >= y_end:
                pg.draw.line(screen, color, [x_start, y_start], [x_start - x_slope, y_start - y_slope], thickness)
                x_start = x_start - x_slope
                y_start = y_start - y_slope
                pg.display.flip()

        # < and >
        elif x_start < x_end and y_start > y_end:
             while x_start <= x_end and y_start >= y_end:
                pg.draw.line(screen, color, [x_start, y_start], [x_start + x_slope, y_start - y_slope], thickness)
                x_start = x_start + x_slope
                y_start = y_start - y_slope
                pg.display.flip()

        # > and <
        elif x_start > x_end and y_start < y_end:
             while x_start >= x_end and y_start <= y_end:
                pg.draw.line(screen, color, [x_start, y_start], [x_start - x_slope, y_start + y_slope], thickness)
                x_start = x_start - x_slope
                y_start = y_start + y_slope
                pg.display.flip()

        # = and <
        elif x_start == x_end and y_start < y_end:
             while x_start == x_end and y_start < y_end:
                pg.draw.line(screen, color, [x_start, y_start], [x_start, y_start + y_slope], thickness)
                y_start = y_start + y_slope
                pg.display.flip()

        # = and >
        elif x_start == x_end and y_start > y_end:
             while x_start == x_end and y_start < y_end:
                pg.draw.line(screen, color, [x_start, y_start], [x_start, y_start - y_slope], thickness)
                y_start = y_start - y_slope
                pg.display.flip()

        # < and =
        elif x_start < x_end and y_start == y_end:
             while x_start > x_end and y_start == y_end:
                pg.draw.line(screen, color, [x_start, y_start], [x_start + x_slope, y_start], thickness)
                x_start = x_start + x_slope
                pg.display.flip()

        # > and =
        elif x_start > x_end and y_start == y_end:
             while x_start > x_end and y_start == y_end:
                pg.draw.line(screen, color, [x_start, y_start], [x_start - x_slope, y_start], thickness)
                x_start = x_start - x_slope
                pg.display.flip()

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

    screen.blit(background, background_rect)
    pg.display.flip()
    draw_lines()

pg.quit()
