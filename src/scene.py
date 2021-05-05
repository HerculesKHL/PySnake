import random
from enum import Enum
import pygame.key as pk
from pygame.locals import *
from pygame import Color, Rect, Surface

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

        #Snake
        self.snake_surf = Surface(self.play_rect.size, pygame.SRCALPHA)
        self.snake = [[9,9],(9,8)]
        self.snake_cell_size = tuple(self.cell_size)
        self.snake_head = Color(255, 0, 0)
        self.snake_body = Color(0, 255,0)
        self.snake_position = (0,0)
        self.snake_max_time = 500 #ms
        self.snake_cur_time = 500
        self.snake_speed_change = False
        self.snake_has_changed = False
        self.snake_speed_rate = 50
            #CLOCKWISE FROM NORTH
        self.snake_directions = ((0,-1),(1,0),(0,1),(-1,0))
        self.snake_cur_direction = (1,0)
        self.snake_growth = False
        self.snake_alive = True
        self.command_queue = []

        #Collectible setup
        self.collectible = (random.randrange(0,self.cell_amt),
                            random.randrange(0,self.cell_amt))
        self.reposition_collectible()

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
        if not self.snake_alive:
            return
        #KEY PRESSES
        keys = pk.get_pressed()
        north = keys[K_w] or keys[K_UP]
        south = keys[K_s] or keys[K_DOWN]
        east = keys[K_d] or keys[K_RIGHT]
        west = keys[K_a] or keys[K_LEFT]
        grow = keys[K_SPACE]
        pause = keys[K_RETURN]

        if grow and self.snake_growth == False:
            self.snake_growth = True

        #MAY REQUIRE SOME REFINEMENT
        #uses the same ordering as the snake's directions
        self.turn_snake((north, east, south, west))
        self.update_snake(delta)

        self.collect()

        self.timer += delta
        self.timer_surf = self.font.render(str(self.timer//1000), True, self.text_colour, self.ui_colour)
        self.timer_rect = self.timer_surf.get_rect()
        self.timer_rect.center = self.tpos

    def render(self, target):
        target.blit(self.play_surf, self.play_rect)
        self.snake_surf.fill((0, 0, 0, 0))
        for bodypart in self.snake:
            fill = self.snake_body
            if self.snake.index(bodypart) == 0:
                fill = self.snake_head
            if not self.snake_alive:
                fill = Color(0, 0, 0)
            import pygame.draw as pd
            pd.rect(self.snake_surf, fill,
                    Rect((bodypart[0]*self.snake_cell_size[0],
                          bodypart[1]*self.snake_cell_size[1]),
                         self.snake_cell_size))
            pd.circle(self.snake_surf, Color(255, 0, 50),
                      (int((self.collectible[0]+0.5)*self.cell_size[0]),
                       int((self.collectible[1]+0.5)*self.cell_size[1])),
                      self.cell_size[0]>>1)
        target.blit(self.snake_surf, self.play_rect)
        #check whether this is the best approach
        self.ui_surf.fill(self.ui_colour)
        self.ui_surf.blit(self.timer_tsurf, self.timer_trect)
        self.ui_surf.blit(self.timer_surf, self.timer_rect)
        self.ui_surf.blit(self.score_tsurf, self.score_trect)
        self.ui_surf.blit(self.score_surf, self.score_rect)
        target.blit(self.ui_surf, self.ui_rect)

    def update_snake(self, delta):
        self.snake_cur_time -= delta
        if self.snake_cur_time <= 0:
            self.snake_cur_time += self.snake_max_time
            self.move_snake()
            self.snake_alive = self.check_snake()

        #REFACTOR
        if self.snake_speed_change and not self.snake_has_changed:
            self.snake_speed_change = False
            self.snake_has_changed = True
            self.snake_max_time -= self.snake_speed_rate
            #print(self.snake_max_time)

        if self.snake_cur_time < 0:
            self.snake_cur_time = 0

    def move_snake(self):
        temp_growth = None
        if self.snake_growth:
            self.snake_growth = False
            temp_growth = self.snake[-1]
        for i in range(len(self.snake)-1, 0, -1):
            self.snake[i] = tuple(self.snake[i-1])
        if temp_growth is not None:
            self.snake.append(temp_growth)
        if len(self.command_queue) > 0:
            self.snake_cur_direction = self.command_queue.pop(0)
        self.snake[0][0] += self.snake_cur_direction[0]
        self.snake[0][1] += self.snake_cur_direction[1]  

        self.snake[0][0] %= self.cell_amt
        self.snake[0][1] %= self.cell_amt

    def turn_snake(self, directions):
        #will have to turn into list of movement pushes...
        if len(self.command_queue) < 2:
            if self.snake_cur_direction[0] != 0:
                if len(self.command_queue) == 0 or self.command_queue[-1][0] != 0:
                    if directions[0]:
                        self.command_queue.append(self.snake_directions[0])
                    elif directions[2]:
                        self.command_queue.append(self.snake_directions[2])
            elif self.snake_cur_direction[1] != 0:
                if len(self.command_queue) == 0 or self.command_queue[-1][1] != 0:
                    if directions[1]:
                        self.command_queue.append(self.snake_directions[1])
                    elif directions[3]:
                        self.command_queue.append(self.snake_directions[3])

    def check_snake(self):
        if tuple(self.snake[0]) in self.snake[1::]:
            return False
        return True

    def collect(self):
        if self.collectible == tuple(self.snake[0]):
            self.snake_growth = True
            self.reposition_collectible()

            self.score += 1
            self.score_surf = self.font.render(str(self.score), True, self.text_colour, self.ui_colour)
            self.score_rect = self.score_surf.get_rect()
            self.score_rect.center = self.spos

            if self.score%5 != 0:
                self.snake_has_changed = False
            if self.score > 0 and self.score%5 == 0:
                self.snake_speed_change = True

    def reposition_collectible(self):
        while self.collectible in self.snake[1::] or\
              self.collectible == tuple(self.snake[0]):
            self.collectible = (random.randrange(0,self.cell_amt),
                                random.randrange(0,self.cell_amt))
