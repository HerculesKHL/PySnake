import random
from enum import Enum
import pygame.key as pk
from pygame.locals import *
from pygame import Color, Rect, Surface

from src.snake import Snake
from src.collectible import Collectible

SceneStates = Enum("SceneStates","INTRO LEVEL PAUSED OVER")

class Scene():
    def __init__(self):
        self.state = SceneStates.INTRO

        #play area setup
            #data
        self.play_info = [0, 0, 450, 450]
        self.cell_amt = 18
        self.back_colour = Color(127, 127, 127)
        self.cell_colour = Color(200, 200, 200)

            #creation
        self.cell_size = (int(self.play_info[2]/self.cell_amt),
                          int(self.play_info[3]/self.cell_amt))
        self.play_rect = Rect(self.play_info)
        self.play_surf = Surface(self.play_rect.size)
        self.play_surf.fill(self.back_colour)

            #checkerboard draw
        import pygame.draw
        for x in range(self.cell_amt):
            for y in range(self.cell_amt):
                if (x%2==0)^(y%2==0):
                    pygame.draw.rect(self.play_surf, self.cell_colour,
                                     Rect((x*self.cell_size[0], y*self.cell_size[1]),
                                          self.cell_size))

        #Snake setup
        self.snake = Snake(self.cell_size, self.cell_amt, False)
        
        #Collectible setup
        self.collectible = Collectible(self.cell_size, self.cell_amt)

        #UI area setup
            #data
        self.ui_info = [450, 0, 400, 450]
        self.text_size = 40
        self.ui_colour = Color(0, 0, 200)
        self.text_colour = Color(0, 0, 0)#Color(214, 214, 63)
        
            #creation
        self.ui_rect = Rect(self.ui_info)
        self.ui_surf = Surface(self.ui_rect.size)
        self.ui_surf.fill(self.ui_colour)

        #UI elements setup
        self.timer = 0 #ms
        self.score = 0
        self.ttpos = (200, 100) #timer text position
        self.tpos = (200, 150)
        self.stpos = (200, 250)
        self.spos = (200, 300)
        
        import pygame.font as pft
        self.font = pft.Font(pft.get_default_font(), self.text_size)
        self.timer_tsurf = self.font.render("TIME:", True, self.text_colour, self.ui_colour)
        self.timer_trect = self.timer_tsurf.get_rect()
        self.timer_trect.center = self.ttpos
        self.score_tsurf = self.font.render("SCORE:", True, self.text_colour, self.ui_colour)
        self.score_trect = self.score_tsurf.get_rect()
        self.score_trect.center = self.stpos

        self.timer_surf = self.font.render(str(self.timer//1000), True, self.text_colour, self.ui_colour)
        self.timer_rect = self.timer_surf.get_rect()
        self.timer_rect.center = self.tpos
        self.score_surf = self.font.render(str(self.score), True, self.text_colour, self.ui_colour)
        self.score_rect = self.score_surf.get_rect()
        self.score_rect.center = self.spos

    def start(self):
        return True
    
    def update(self, delta):
        if not self.snake.check_alive():
            return

##        if grow and self.snakegrowth == False:
##            self.snakegrowth = True

        #MAY REQUIRE SOME REFINEMENT
        #self.collect()

        self.timer += delta
        self.timer_surf = self.font.render(str(self.timer//1000), True, self.text_colour, self.ui_colour)
        self.timer_rect = self.timer_surf.get_rect()
        self.timer_rect.center = self.tpos

        #snake update
        self.snake.update(delta)

        #Collectible update
        self.collectible.update(delta)

    def render(self, target):
        target.blit(self.play_surf, self.play_rect)
        #check whether this is the best approach
        self.ui_surf.fill(self.ui_colour)
        self.ui_surf.blit(self.timer_tsurf, self.timer_trect)
        self.ui_surf.blit(self.timer_surf, self.timer_rect)
        self.ui_surf.blit(self.score_tsurf, self.score_trect)
        self.ui_surf.blit(self.score_surf, self.score_rect)
        target.blit(self.ui_surf, self.ui_rect)

        #snake draw
        self.snake.render(target)
        
        #collectible draw
        self.collectible.render(target)

    def collect(self):
        if self.collectible.get_current_cell() == tuple(self.snake[0]):
            self.snake_growth = True
            while self.collectible.get_current_cell() == tuple(self.snake[0]) or\
                  self.collectible.get_current_cell() in self.snake:
                self.collectible.reposition()

            self.score += 1
            self.score_surf = self.font.render(str(self.score), True, self.text_colour, self.ui_colour)
            self.score_rect = self.score_surf.get_rect()
            self.score_rect.center = self.spos

            if self.score%5 != 0:
                self.snake_has_changed = False
            if self.score > 0 and self.score%5 == 0:
                self.snake_speed_change = True
