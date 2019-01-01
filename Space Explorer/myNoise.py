## A Cheaper noise function
import math, random, pygame
import space_explorer

class myNoise:
    def __init__(self, seed):
        self.Xseed = random.randint(0,999999999)
        self.Yseed = random.randint(0,999999999)

        self.interval = 100

    def noise1d(self,x, seed):
        data = space_explorer.myhash(x//self.interval, seed) ## Possibly hash only once
        a = data[0]
        value = ((x%self.interval)+a)*((x%self.interval)+self.interval)
        maximum = ((self.interval/2)+a)*((self.interval/2)+self.interval)
        if x%self.interval == 0:
            print(x,a)
        if value/ maximum > 1:
            return(1)
        return value/maximum
        
    def noise2d(self,x,y):
        return (self.noise1d(x, self.Xseed) + self.noise1d(y, self.Yseed))/2
        
pygame.init()
noise = myNoise("Curtis")
screen = pygame.display.set_mode((500,500))
for x in range(500):
    for y in range(500):
        ##print(noise.noise2d(x,y))
        alt = (noise.noise2d(x,y) + 1)/2 * 255
        ##print(alt)
        pixel = (alt,alt,alt)
        screen.set_at((x,y),pixel)
print("All Done")
pygame.display.flip()
        
