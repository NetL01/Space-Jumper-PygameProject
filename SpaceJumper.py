#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pygame
from pygame.locals import *
import sys
from os import path
import random
from groups import *
import inputbox
from config import *



# Начало программы
class Game():

    def __init__(self):
        pygame.init()
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption('Space Jumper')
        
    def event(self, event):
        if event.type == QUIT:
            sys.exit()
        elif event.type == KEYUP:
            if event.key == K_ESCAPE:
                if isinstance(self.location, GameLocation):
                    self.location = StartLocation(self)
                elif isinstance(self.location, StartLocation):
                    sys.exit()
                

# main функция
def main():
    game = Game()
    start_location = StartLocation(game)
    game.location = start_location
    clock = pygame.time.Clock()
    while 1:
        clock.tick(fps)
        game.location.draw()
        pygame.display.flip()
        for event in pygame.event.get():
            game.location.event(event)
            game.event(event)            

pygame.mixer.init()
pygame.mixer.music.load('game.mp3')
pygame.mixer.music.play()
pygame.mixer.music.set_volume(0.4)


class Location(object):
    def __init__(self, parent):
        self.window = pygame.display.get_surface()
        self.parent = parent
        self.background = pygame.image.load('img/background.png').convert()
        self.lose = pygame.image.load('img/original.jpg').convert()
    def event(self,event):
        pass
    def draw(self):
        pass


# самый первый экран программы
class StartLocation(Location):
    
    def __init__(self, parent):
        Location.__init__(self, parent)
        pygame.key.set_repeat(0)
        self.startbtn = Button(240, 200, "Начать")
        self.exitbtn = Button(240, 270, "Выйти")
        self.controls = pygame.sprite.Group()
        self.surfaces = []
        self.controls_captions = pygame.sprite.Group()
        self.controls_captions.add(self.startbtn.textSprite)
        self.controls_captions.add(self.exitbtn.textSprite)
        self.controls.add(self.startbtn)
        self.controls.add(self.exitbtn)
        self.window.blit(self.background, (0, 0))
        
    def draw(self):
        self.controls.clear(self.window, self.background)
        self.controls.draw(self.window)
        self.controls_captions.draw(self.window)
    
    def event(self,event):
        if event.type == MOUSEMOTION:
            for btn in self.controls:
                if btn.rect.collidepoint(pygame.mouse.get_pos()):
                #pass
                    btn.changeState(1)
                else:
                #pass
                    btn.changeState(0)
        elif event.type == MOUSEBUTTONUP:
            if self.startbtn.rect.collidepoint(pygame.mouse.get_pos()):
                name = inputbox.ask(self.window, "Имя:")
                if name:
                    self.parent.location = GameLocation(self.parent, name)
            elif self.exitbtn.rect.collidepoint(pygame.mouse.get_pos()):
                sys.exit()
    
    def showInput(self):
        self.input_surf = Rectangle(300, 100, (0,191,255,200))
        self.surfaces.append(self.input_surf)   


# сам геймплей
class GameLocation(Location):
    def __init__(self, parent, name):
        Location.__init__(self, parent)
        pygame.key.set_repeat(10)
        pygame.mouse.set_visible(0)
        self.jumper = Jumper(name)
        self.jumper.name = name
        # список, содержащий в себе информацию о всех спрайтах
        self.allsprites = pygame.sprite.Group()
        self.allsprites.add(self.jumper)
        for i in range(0, platform_count):
            self.allsprites.add(self.randomPlatform(False))

        # занесение пратформ в спрайты
        for platform in self.allsprites:
            if isinstance(platform, Platform) and platform.spring != None:
                self.allsprites.add(platform.spring)

        self.score_sprite = TextSprite(50, 15, self.jumper.name, 45, (0,0,0))
        self.allsprites.add(self.score_sprite)
        # self.header = Rectangle(screen_width, 50, (0,191,255,128))
        # закрашиваем фон
        self.window.blit(self.background, (0, 0))
        # начало создания монстров
        self.monster = None
        self.allsprites.add(Platform((480 / 2), (640 - 50)))
    
    
    def randomPlatform(self,top = True):
        x = random.randint(0, screen_width - platform_width)
        # список координат, которые не соответствуют для создания платформ по x
        bad_y = []
        for spr in self.allsprites:
            bad_y.append((spr.y-platform_y_padding, spr.y + platform_y_padding + spr.rect.height))
        
        good = 0
        while not good:
            if top:
               y = random.randint(-100, 50)
            else:
                y = random.randint(0, screen_height)
            good = 1
            for bad_y_item in bad_y:
                if bad_y_item[0] <= y <= bad_y_item[1]:
                    good = 0
                    break
            
        dig = random.randint(0, 100)
        if dig < 35:
            return MovingPlatform(x,y)
        elif dig >= 35 and dig < 50:
            return CrashingPlatform(x,y)
        else:
            return Platform(x,y)
    
    
    
    def draw(self):
        if self.jumper.alive == 1:
            # create monster
            if self.monster == None:
                case = random.randint(-1000, 50)
                if case > 0:
                    x = self.jumper.x
                    y = self.jumper.y
                    
                    self.monster = Monster(random.randint(0, screen_width), random.randint(-50, 50), x, y, (45 * random.randint(2, 4)))
                    self.allsprites.add(self.monster)
                    self.monster.move()
            else:
                self.monster.move()
                # полёт монстра по прямой к прошлому месту джампера
                if self.jumper.rect.colliderect(self.monster.rect):
                    self.jumper.alive = 0
                if self.monster.y >= screen_height:
                    self.allsprites.remove(self.monster)
                    self.monster = None
                    
            self.allsprites.clear(self.window, self.background)
            
            # прыжки джампера
            mousePos = pygame.mouse.get_pos()
            self.jumper.inc_y_speed(-gravitation)
            if mouse_enabled:
                self.jumper.set_x(mousePos[0])
            else:
                if transparent_walls:
                    if self.jumper.x < 0:
                        self.jumper.set_x(screen_width)
                    elif self.jumper.x > screen_width:
                        self.jumper.set_x(0)
            self.jumper.move_y(-self.jumper.ySpeed)
            for spr in self.allsprites:
                # пересечение с пружинами
                if isinstance(spr, Spring) and self.jumper.get_legs_rect().colliderect(spr.get_top_surface()) and self.jumper.ySpeed <= 0:
                    spr.compress()
                    self.jumper.ySpeed = spring_speed
                # пересечение с платформами
                if isinstance(spr, Platform) and self.jumper.get_legs_rect().colliderect(spr.get_surface_rect()) and self.jumper.ySpeed <= 0:
                    if isinstance(spr, CrashingPlatform):
                        spr.crash()
                        break
                    self.jumper.ySpeed = jump_speed
            
                if isinstance(spr, Platform):
                    # создание новых платформ
                    if spr.y >= screen_height:
                        self.allsprites.remove(spr)
                        platform = self.randomPlatform()
                        self.allsprites.add(platform)
                        if isinstance(platform, Platform) and platform.spring != None:
                            self.allsprites.add(platform.spring)

                
                # move blue and crashed platforms
                if isinstance(spr, MovingPlatform) or (isinstance(spr, CrashingPlatform) and spr.crashed == 1):
                    spr.move()
            
            # передвижение экрана 
            if self.jumper.y < horizont:
                self.jumper.inc_score(self.jumper.ySpeed)
                for spr in self.allsprites:
                    if not isinstance(spr, TextSprite):
                        spr.move_y(self.jumper.ySpeed)
            
            
            # отрисовка всех спрайтов
            self.allsprites.draw(self.window)
            self.score_sprite.setText("               %s,    %s" % (self.jumper.name, int(self.jumper.score/10)))
            # self.window.blit(self.header, (0,0))
        else:
            # если умер - экран смерти
            self.rever()
            
    def rever(self):
        font = pygame.font.Font(None, 40)
        gray = pygame.Color('gray19')
        blue = pygame.Color('dodgerblue')
        clock = pygame.time.Clock()
        timer = 10
        dt = 0
        done = False
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True

            timer -= dt
            if timer <= 0:
                timer = 10
                done =  True
            # self.window.fill(gray)
            self.window.blit(self.lose, (-170,0))
            txt = font.render(str(round(timer, 2)), True, blue)
            self.window.blit(txt, (250, 300))
            pygame.display.flip()
            dt = clock.tick(30) / 1000
        self.parent.location = GameLocation(self.parent, self.jumper.name)

    def event(self,event):
        if event.type == KEYDOWN:
            if event.key == K_LEFT:
                self.jumper.set_x(self.jumper.x - 10)
            elif event.key == K_RIGHT:
                self.jumper.set_x(self.jumper.x + 10)
            

class ExitLocation(Location):
    def __init__(self, parent, name, score):
        Location.__init__(self, parent)
        self.background = pygame.image.load('img/background.png')
        print("Ну и ладно!")


if __name__ == "__main__":
    main()
