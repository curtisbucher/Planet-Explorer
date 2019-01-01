import pygame,sys
from pygame.locals import *
from random import randint
from hashlib import sha1
from copy import deepcopy
import random

import math

## Defining Variables
WIDTH = 1200
HEIGHT  = 800
PI = math.pi

## Initiating pygame
pygame.init()
pygame.font.init()
myfont = pygame.font.SysFont('Roboto', 24)

clock = pygame.time.Clock()
size = (WIDTH, HEIGHT)
screen = pygame.display.set_mode(size)
print("Loading Procedurally Generated Map")

def rot_center(image, angle):
    """ Rotates image around its center by `angle` radians"""
    angle = math.degrees(angle)
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image

def myhash(var, seed):
    """ Generates a random hash given any variable and a string"""
    data = tuple(sha1((repr(var) + repr(seed)).encode()).digest())
    return data

def planet_gen(coords, seed):
    """ Generates planetary data including color, size, and whether or
        or not a planet is present given coords and a seed"""
    data = myhash(coords, seed)
    color = (data[1],data[2],data[3])
    size = data[4]//2
    is_planet = data[5] == data[6] and not data[7]##not data[5] and not data[6] and not data[7]%2 and not data[8]%2
    is_star = not is_planet and data[5] == data[6]
    return(is_planet, is_star, color, size)

def key_input():
    """ Returns a tuple of the most relevant keys and their state"""
    pygame.event.get()
    keys = pygame.key.get_pressed()
    left = keys[pygame.K_a] or keys[pygame.K_LEFT]
    right = keys[pygame.K_d] or keys[pygame.K_RIGHT]
    up = keys[pygame.K_w] or keys[pygame.K_UP]
    down = keys[pygame.K_s] or keys[pygame.K_DOWN]
    done = False## keys[pygame.K_s] or keys[pygame.K_DOWN]
    
    return(left, right, up, down, done)

def render_frame(ship):
    
    for x in range(int(round(ship.coords[0],-1)) , WIDTH + int(round(ship.coords[0], -1)), 10):
        for y in range(int(round(ship.coords[1], -1)), HEIGHT + int(round(ship.coords[1], -1)), 10):
            is_planet, star, color, size = planet_gen((x,y),"daosfuh")
            if is_planet:
                planet.instances.append(planet((x,y),size,color))
class planet:
    """ Planet objects have a size, color, and coords and can draw to the screen"""
    instances = []
    def __init__(self, coords, size,color):
        self.size = size
        self.color = color
        self.coords = coords
        planet.instances.append(self)
                    
    def draw(self, ship_coords):
        x,y = self.coords
        sx,sy = ship_coords
        
        new_coords = round(x - sx),round(y - sy)
        
        pygame.draw.circle(screen,self.color, new_coords, self.size,0)

class spaceship:
    """ Contains a velocity, acceleration, coordinates, and rotaation to control movement
        around the universe. Methods for drawing to the screen as well as moving"""
    def __init__(self, coords, velocity, acceleration):
        self.coords = coords ## A tuple reprisenting ships x,y coords
        self.velocity = velocity ## A tuple reprisenting ships movement in space

        ## A Boolean reprisenting wether or not the ship is accelerating
        self.acceleration = acceleration
        self.rotation = PI

        self.img = pygame.transform.rotate(
                pygame.transform.scale(pygame.image.load("spaceship.png"),(50,50)),-90)
        
    def draw(self):
        """ Draws itself to the middle of the screen"""
        center = (WIDTH//2, HEIGHT//2)
        new_img = rot_center(self.img, self.rotation)

        x,y = self.coords
        round_coords = round(x),round(y)

        textsurface = myfont.render(str(round_coords), False, (255,255,255))
        screen.blit(textsurface, (0,0))
        
        screen.blit(new_img,center)
        

    def move(self):
        """ Moves the screen in the proper direction given the ships velocity and rotation"""
        x,y = self.coords
        
        ## change Y = sin(theta) * r
        self.velocity[1] += -math.sin(self.rotation) * self.acceleration
        ## change X = cos(theta) * r
        self.velocity[0] += math.cos(self.rotation) * self.acceleration
        
        self.coords = x + self.velocity[0], y + self.velocity[1]

        left_bound = round(self.coords[0]) - 128
        top_bound = round(self.coords[1]) - 128
        right_bound = round(self.coords[0]) + WIDTH+ 128
        bottom_bound = round(self.coords[1]) + HEIGHT+128
        
        render_frame(self)
 
        for _planet in planet.instances:
                if left_bound < _planet.coords[0] < right_bound and top_bound < _planet.coords[1] < bottom_bound :
                    _planet.draw(self.coords)

def main():
    """ Main program loop """
    ## Filling in blank screen
    screen.fill((0,0,0))
    pygame.display.flip()

    ## Generating the first frame. Creates image of stars for background and
    ## creates all the planets in the first frame
    for x in range(-WIDTH//2, WIDTH//2):
        for y in range(-HEIGHT//2, HEIGHT//2):
            is_planet, star, color, size = planet_gen((x + WIDTH//2,y+HEIGHT//2),"daosfuh")
##            if is_planet:
##                planet.instances.append(planet((x + WIDTH//2,y + HEIGHT//2),size,color))
            if star:
                screen.set_at((x + WIDTH//2,y + HEIGHT//2),(color[0],color[0],color[0]))
                
    ## Creating star background surface
    stars = screen.copy()
    done = False

    ## Ship movement vectors
    ship = spaceship([0,0],[0,0],False) 
    
    while not done:
        screen.blit(stars, (0,0))

        ## Modifying Ship Velocity based on keyboard input
        left, right, up, down, done = key_input()

        if left:
            ship.rotation += PI/15
        elif right:
            ship.rotation -= PI/15

        if down:
            ship.acceleration = -1
        elif up:
            ship.acceleration = 1
        else:
            ship.acceleration = 0

        ship.move()
        ship.draw()
        
        ## Generating planets on outskirts of screen    

        pygame.display.flip()
        clock.tick(30)
    


        
if __name__ == '__main__':
    main()

