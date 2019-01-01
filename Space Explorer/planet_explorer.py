import pygame
import random
import opensimplex
from space_explorer import planet_gen, key_input
import time
from functools import lru_cache

pygame.init()
clock = pygame.time.Clock()

screen = pygame.display.set_mode((0,0),pygame.RESIZABLE,16)
size = screen.get_size()
SEED = "curtis"

planet = planet_gen((random.randint(0,9999999),random.randint(0,9999999)),SEED,True)

simplex = opensimplex.OpenSimplex(1)


zoom = 1000
exp = 1

colorA = planet.colora
colorB = planet.colorb

class Vector:
	__slots__ = ('x', 'y')
	def __init__(self, x, y):
	    self.x = x
	    self.y = y
	    
coords = Vector(0,0)
velocity = Vector(0,0)

@lru_cache(size[0]*size[1])
def get_alt(x,y):
    return (simplex.noise2d(x/zoom,y/zoom) + 1)/2 ** exp

def render_screen():
    for x in range(coords.x, size[0] + coords.x):
        for y in range(size[1]):
            alt = get_alt(x,y)
    ##        alt = (simplex.noise2d(x/zoom,y/zoom) + 1)/2 ** exp
            pixel = (alt*colorA[0],alt*colorA[1], alt*colorA[2])
    ##        if pixel[0]<128 and pixel[1]<128 and pixel[2]<128:
    ##            pixel = ((1-alt)*colorB[0],(1-alt)*colorB[1], (1-alt)*colorB[2])
            screen.set_at((x - coords.x,y), pixel)
            
def move():
    coords.x -= velocity.x
    coords.y -= velocity.y
    screen.blit(screen,(velocity.x,velocity.y))

    if velocity.x < 0:
        for x in range(abs(velocity.x)):
            for y in range(size[1]):
                alt = (simplex.noise2d((coords.x + size[0])/zoom,(coords.y + y)/zoom) + 1)/2 ** exp
                pixel = (alt*colorA[0],alt*colorA[1], alt*colorA[2])
                screen.set_at((size[0]-x-1,y), pixel)
        screen.convert(screen)

    elif velocity.x > 0:
        for x in range(velocity.x):
            for y in range(size[1]):
                alt = (simplex.noise2d((coords.x)/zoom,(coords.y + y)/zoom) + 1)/2 ** exp
                pixel = (alt*colorA[0],alt*colorA[1], alt*colorA[2])
                screen.set_at((x,y), pixel)
        screen.convert(screen)

    if velocity.y < 0:
        for x in range(size[0]):
            for y in range(abs(velocity.y)):
                alt = (simplex.noise2d((coords.x + x)/zoom,(coords.y+size[1])/zoom) + 1)/2 ** exp
                pixel = (alt*colorA[0],alt*colorA[1], alt*colorA[2])
                screen.set_at((x,size[1]-y-1), pixel)
        screen.convert(screen)

    elif velocity.y > 0:
        for x in range(size[0]):
            for y in range(velocity.y):
                alt = (simplex.noise2d((coords.x + x)/zoom,coords.y/zoom) + 1)/2 ** exp
                pixel = (alt*colorA[0],alt*colorA[1], alt*colorA[2])
                screen.set_at((x,y), pixel)
        screen.convert(screen)



render_screen()
done = False
speed = 3
while not done:
    move()

    clock.tick(30)
    
    keys, done = key_input()
    if(keys[pygame.K_RIGHT]):
        velocity.x = -3
    elif(keys[pygame.K_LEFT]):
        velocity.x = 3
    else:
        velocity.x = 0
            
    if(keys[pygame.K_UP]):
        velocity.y = 3
    elif(keys[pygame.K_DOWN]):
        velocity.y = -3
    else:
        velocity.y = 0

##    for event in pygame.event.get():
##        if event.type == pygame.MOUSEBUTTONUP: 
##            pygame.event.wait()
##        elif event.type == pygame.VIDEORESIZE:
##            size = event.size
##        elif event.type == pygame.QUIT:
##            done = True
            
    pygame.display.flip()
pygame.display.quit()

        
        
