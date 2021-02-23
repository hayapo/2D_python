import pygame
from pygame.locals import *
import sys
from math import * 
import numpy as np

class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def add(self, b):
        a = self
        return Vec2(a.x+b.x, a.y+b.y)

    def sub(self, b):
        a = self
        return Vec2(a.x-b.x, a.y-b.y)
    
    def copy(self):
        return Vec(self.x, self.y)

    def mult(self, s):
        return Vec2(s*self.x, s*self.y)

    def mag(self):
        return sqrt(self.x**2 + self.y**2)
        
ins = Vec2(2,3)
add_ins = Vec2(1,1)
print(ins)