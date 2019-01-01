import pygame,sys
from pygame.locals import *
import math

from hashlib import sha1
from opensimplex import OpenSimplex
from functools import lru_cache
import time

## Defining Variables
PI = math.pi
SEED = "Curtis"

## Initiating pygame
pygame.init()
pygame.font.init()
myfont = pygame.font.SysFont('Roboto Mono', 24)

infoObject = pygame.display.Info()
WIDTH = 1200 #infoObject.current_w
HEIGHT  =  800 #infoObject.current_h

clock = pygame.time.Clock()
size = (WIDTH, HEIGHT)
screen = pygame.display.set_mode(size,pygame.RESIZABLE)#FULLSCREEN)

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

def planet_gen(coords, seed, test = False):
    """ Generates planetary data including color, size, and whether or
        or not a planet is present given coords and a seed"""
    data = myhash(coords, seed)

    ID = data[0] + data[1] + data[3] + data[4]## A number specific to each planet
    is_planet = data[5] == data[6] and not data[4]%100 #A bool that states if that specific pixel contains a planet
    size = data[7]//2
    
    colora = (data[8],data[9],data[10])
    colorb = (data[11],data[12],data[13]) ## Will be replaced by weather conditions and biomes

    temperature_mid = data[13]/255 # Between -1 and 1## Determines biomes, determines the midpoint for the heatmap and the scalar
    temperature_scalar = data[14]/255 # Between 0 and 1
    humidity_mid = data[15]/255
    humidity_scalar = data[16]/255
    
    alt_mid = data[17]/255
    alt_scalar = data[18]/255
    alt_y_zoom = data[19]/255
    alt_x_zoom = data[19]/255

    if test:
        is_planet = True
    
    if(is_planet and ID not in planet.IDS):
        return planet(coords, ID, size, colora, colorb, temperature_mid, temperature_scalar, humidity_mid, humidity_scalar, alt_mid, alt_scalar, alt_x_zoom, alt_y_zoom)
    
    return False

def key_input():
    """ Returns a tuple of the most relevant keys and their state"""
    done = False
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONUP: 
            pygame.event.wait()
        elif event.type == pygame.VIDEORESIZE:
            size = event.size
        elif event.type == pygame.QUIT:
            done = True
            
    keys = pygame.key.get_pressed()

    return(keys, done)

def render_stars():
    """ Creates an image of stars for the background. Returns a surface of stars"""
    stars = pygame.Surface((WIDTH,HEIGHT))
    for x in range(-WIDTH//2, WIDTH//2):
        for y in range(-HEIGHT//2, HEIGHT//2):
            data = myhash((x + WIDTH//2,y+HEIGHT//2), SEED)
            if data[0] == data[1]: ## Place Star
                stars.set_at((x + WIDTH//2,y + HEIGHT//2),(data[2],data[2],data[2]))
    return(stars)

def render_frame(coords):
    """ Generates planet objects that are within the range of the screen"""
    for x in range(int(round(coords[0],-1)) , WIDTH + int(round(coords[0], -1)), 10):
        for y in range(int(round(coords[1], -1)), HEIGHT + int(round(coords[1], -1)), 10):
                planet_gen((x,y), SEED)

class planet:
    """ Planet objects have a size, color, and coords and can draw to the screen"""
    instances = []
    IDS = []
    ## Key = (humidity, temp, elevation)
    biomes = {(False,False,False) : "Tundra", (True,False,False) : "Ocean",(False,True,False) : "Desert",(True,True,False) : "Ocean",
              (False,False,True) : "Grass", (True,False,True) : "Mountains", (False,True,True) : "Forest", (True,True,True) : "Rainforest"}
    biome_colors = {"Tundra" : (255,255,255), "Ocean" : (0,0,255), "Desert" : (255,255,0) , "Grass" : (154,205,50), "Mountains" : (128,128,128),
                    "Forest" : (128,128,0), "Rainforest" : (0,255,0)}
              
    #       ^H ############################################
    #       |U # Ocean  | Ocean  # Mountains | Rainforest #
    #       |M #--------|--------#-----------|------------#
    #       |I # Tundra | Desert # Grass     | Forest     #
    #       |D ############################################
    #       |I #    Temp -->     #       Temp -->         #
    #       |T #-----------------#-------------------------
    #       |Y #             Elevation --->               #
    #          ############################################

    def __init__(self, coords, ID, size, colora, colorb,
                 temperature_mid, humidity_mid, temperature_scalar, humidity_scalar, altitude_mid, altitude_scalar, alt_x_zoom, alt_y_zoom):
        self.coords = coords
        self.id = ID
        self.size = size
        
        self.colora = colora
        self.colorb = colorb

        self.temperature_mid = temperature_mid
        self.humidity_mid = humidity_mid
        self.temperature_scalar = temperature_scalar
        self.humidity_scalar = humidity_scalar
        self.altitude_mid = altitude_mid
        self.altitude_scalar = altitude_scalar
        self.altitude_y_zoom = alt_y_zoom
        self.altitude_x_zoom = alt_x_zoom
        
        self.planet_surface = self._gen_image()

        planet.instances.append(self)
        planet.IDS.append(self.id)

    def _gen_image(self):
        """ Creates a planet image based on self variables. Employs `self._texture` to add land mass"""
        resolution = 50 ## Self.size for full resolution
        zoom = 4 ## How Zoomed in the noise is for texturing the planet, the higher the closer
        
        ## Setting up the planet image
        planet_surface = pygame.Surface((resolution *2, resolution*2))
        pygame.draw.circle(planet_surface,self.colora, (resolution,resolution),resolution,0)
        planet_surface.set_colorkey((0,0,0))

        ## Texturing the image
        planet_surface = self._biome_texture(planet_surface, resolution, zoom)
        planet_surface = pygame.transform.scale(planet_surface, (self.size*2, self.size*2))
        
        return planet_surface

    def _biome_texture(self, surface, resolution, zoom):
        """ Textures an image using simplex noise, blends the origional color with self.colorb"""
        simplex = OpenSimplex(self.id)
        start = time.time()
        zoomX = 4##self.altitude_x_zoom * 2 + 4
        zoomY = 4##self.altitude_y_zoom * 2 + 4
        diff= 10 ## The difference in similarity between alt temp and hum
        
        for x in range(surface.get_width()):
            for y in range(surface.get_height()):
                 pixel = surface.get_at((x,y))
                 if pixel != (0,0,0):
                    alt =  ((simplex.noise3d(x/resolution*zoomX, y/resolution*zoomY,0) + 1)/2)
                    temp = ((simplex.noise3d(x/resolution*zoomX, y/resolution*zoomY,diff) + 1)/2)
                    hum = (simplex.noise3d(x/resolution*zoomX, y/resolution*zoomY,2*diff) + 1)/2
                    biome_color = self._gen_biome(alt, temp, hum)
                    pixel = biome_color
                    pixel = pixel[0]*(alt**(1/2)),pixel[1]*(alt**(1/2)),pixel[2]*(alt**(1/2)),
                 surface.set_at((x,y), pixel)
        
        end = time.time()
        return surface

    def _gen_biome(self, alt, temp, hum):
        biome = planet.biomes[hum * self.humidity_scalar> self.humidity_mid, temp * self.temperature_scalar> self.temperature_mid, alt * self.altitude_scalar> self.altitude_mid]
        #biome = planet.biomes[(hum > 0.5, temp > 0.5, alt > 0.5)]
        return planet.biome_colors[biome]
        
    def draw(self, ship_coords):
        x,y = self.coords
        sx,sy = ship_coords
        
        new_coords = round(x - sx),round(y - sy)

        screen.blit(self.planet_surface, new_coords)
        

class spaceship:
    """ Contains a velocity, acceleration, coordinates, and rotaation to control movement
        around the universe. Methods for drawing to the screen as well as moving"""
    def __init__(self, coords = [0,0], velocity = [0,0], acceleration = False):
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
        
        screen.blit(new_img, center)
        
        self._disp_data()
        self._disp_vector_graph((200,0),60)
        

    def _disp_data(self, coords = (0,0)):
        """ Displays ships motion vectors via text given top left coords of text"""
        x,y = self.coords
        round_coords = round(x + WIDTH//2),round(y + HEIGHT//2)
        vx,vy = self.velocity
        round_velocity = round(vx), round(vy)

        coords_text = myfont.render(      "Coordinates : " + str(round_coords), False, (255,255,255))
        velocity_text = myfont.render(    "Velocity        : " + str(round_velocity), False, (255,255,255))
        acceleration_text = myfont.render("Acceleration: " + str(self.acceleration), False, (255,255,255))
        
        screen.blit(coords_text, (coords[0],coords[1]))
        screen.blit(velocity_text, (coords[0],coords[1]+20))
        screen.blit(acceleration_text, (coords[0],coords[1]+40))

    def _disp_vector_graph(self, coords, size):
        x,y = coords
        center = x + size/2, y + size/2
        cx, cy = center
        ## Showing movement vectors
        ##pygame.draw.rect(screen, (255,255,255), (coords,(size,size)),0)

        if min(abs(size//2),abs(self.velocity[0]//5)) == size//2:
            x_factor = size//2 * self.velocity[0]/abs(self.velocity[0])
        else:
            x_factor = round(self.velocity[0])//5

        if min(abs(size//2),abs(self.velocity[1]//5)) == size//2:
            y_factor = size//2 * self.velocity[1]/abs(self.velocity[1])
        else:
            y_factor = round(self.velocity[1])//5
        
        pygame.draw.line(screen, (255,0,0), center, (cx + x_factor, cy + y_factor), 2)
        if self.acceleration:
            pygame.draw.line(screen, (0,255,0), center, (cx + math.sin(self.rotation-PI/2)*size//2, cy +  math.cos(self.rotation-PI/2)*size//2), 2)
        

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
 
        for _planet in planet.instances:
                if left_bound - 255 < _planet.coords[0]  < right_bound + 255 and top_bound - 255 < _planet.coords[1] < bottom_bound + 255:
                    _planet.draw(self.coords)

def space_explorer():
    """ Main program loop """
    print("Loading Procedurally Generated Map...")
    screen.fill((0,0,0))
    pygame.display.flip()

    ## Creating star background surface
    stars = render_stars()
    print("Rendering Stars...")
    
    ## Ship movement vectors
    ship = spaceship() 

    done = False
    while not done:
        screen.blit(stars, (0,0))

        ## Modifying Ship Velocity based on keyboard input
        keys,done = key_input()

        if keys[pygame.K_LEFT]:
            ship.rotation += PI/15
        elif keys[pygame.K_RIGHT]:
            ship.rotation -= PI/15

        if keys[pygame.K_DOWN]:
            ship.acceleration = -1
        elif keys[pygame.K_UP]:
            ship.acceleration = 1
        elif keys[pygame.K_SPACE]:
            ship.velocity = [0,0]
        elif keys[pygame.K_RETURN]:
            print("return")
            for planets in planet.instances:
                print("Planet: " + str(planets.coords))
                print("Ship: " + str(ship.coords))
                if planets.coords[0] < ship.coords[0] + WIDTH//2< planets.coords[0] + planets.size*2:
                    if planets.coords[1] < ship.coords[1] + HEIGHT//2< planets.coords[1] + planets.size*2:
                        print("Landed on " + str(planets.id))
                    
        else:
            ship.acceleration = 0

        ship.move()
        ship.draw()
        render_frame(ship.coords)
        if planet.instances:
            pass
            #print(planet.instances[len(planet.instances)-1].coords)
        
        ## Generating planets on outskirts of screen    

        pygame.display.flip()
        clock.tick(30)

def planet_test():
    """ Main program loop """
    screen.fill((0,0,0))
    pygame.display.flip()

    ## Creating star background surface
    stars = render_stars()

    done = False
    x=0
    first = True
    while not done:

        ## Modifying Ship Velocity based on keyboard input
        keys, done = key_input()
        
        if keys[pygame.K_RIGHT] or first:
            screen.blit(stars, (0,0))
            
            start = time.time()
            new_planet = planet_gen((WIDTH//2 + x * WIDTH, HEIGHT//2),"Curtis", True)
            end = time.time()
            print("Gen Time: " + str(end-start))
            
            #new_planet = planet.instances[x]
            if new_planet:
                new_planet.draw((new_planet.size//2 + x*WIDTH,new_planet.size//2))
            pygame.display.flip()
            time.sleep(0.2)
            x+=1
            ##print(new_planet.humidity)
            ##print(new_planet.temp)
        if keys[pygame.K_LEFT]:
            screen.blit(stars, (0,0))
            planet_gen((WIDTH//2 + x, HEIGHT//2),"Curtis")
            planet.instances[x].draw((new_planet.size//2,new_planet.size//2))
            pygame.display.flip()
            time.sleep(0.2)
            x-=1
        first = False
        ## Generating planets on outskirts of screen    
        clock.tick(30)
     
if __name__ == '__main__':
    space_explorer()
    ##planet_test()
    pygame.display.quit()
