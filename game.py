from typing import Any
from numpy.lib.function_base import place
import pygame
from pygame.locals import *
import sys
from math import * 
import numpy as np
from functools import reduce

#mainで使う変数
WALL_STROKE: int = 3
WALL_COLOR: tuple = (255, 240, 240)
PLAYER_STROKE: int = 10
PLAYER_COLOR: tuple = (224, 224, 0)
RAY_STROKE_COLOR: tuple = (207, 194, 120)
RAY_STROKE: int = 1

class Vec2:
    '''Vec2(int:x, int:y)
        x:ベクトルのx成分
        y:ベクトルのy成分
    '''

    x: int
    y: int

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
    
    def add(self, b):
        '''
        ベクトルの足し算
        b:足したいベクトル
        '''
        a: Vec2 = self
        return Vec2(a.x+b.x, a.y+b.y)

    def sub(self, b):
        '''
        ベクトルの引き算 
        b:引きたいベクトル
        '''
        a: Vec2 = self
        return Vec2(a.x-b.x, a.y-b.y)
    
    def copy(self):
        '''
        ベクトルのコピー
        '''
        return Vec2(self.x, self.y)

    
    def mult(self, s):
        '''
        ベクトルの掛け算
        s:掛ける数
        '''
        return Vec2(s*self.x, s*self.y)

    def mag(self):
        '''
        ベクトルの大きさを求める
        '''
        return sqrt(self.x**2 + self.y**2)

class Ray2(Vec2):
    '''Ray2(Vec2:pos, Vec2:way)
        pos:このレイの始点の位置ベクトル
        way:このレイの始点から伸びる方向ベクトル
    '''
    pos: Vec2
    way: Vec2

    def __init__(self, pos: Vec2, way: Vec2):
        self.pos = pos
        self.way = way
    

    def begin(self) -> Vec2:
        '''
        レイの始点を求める
        '''
        return self.pos

    def end(self) -> Vec2:
        '''
        レイの終点を求める
        '''
        return self.pos.add(self.way)

    def intersection(self, r2) -> Vec2:
        '''
        このレイとr2との交点を求める
        '''
        r2: Ray2
        r1: Ray2 = self

        #y軸方向の線分はちょっとずらす
        if abs(r1.way.x) < 0.01:
            r1.way.x = 0.01
        if abs(r2.way.x) < 0.01:
            r2.way.x = 0.01

        #r1, r2を直線とみなして交点を求める
        #r1の傾き
        if r1.way.x != 0:
            t1: float = r1.way.y / r1.way.x
        else:
            t1: float = float('inf')
        #r2の傾き
        
        if r2.way.x != 0:
            t2: float = r2.way.y / r2.way.x
        else:
            t2: float = float('inf')
        
        #各座標
        x1: float = r1.pos.x
        x2: float = r2.pos.x
        y1: float = r1.pos.y
        y2: float = r2.pos.y

        #交点の座標
        if t1 - t2 != 0:
            sx: float  = (t1*x1 - t2*x2 - y1 + y2) / (t1 - t2)
        else:
            sx: float = float('inf')
        sy: float = t1 * (sx - x1 ) + y1
        
        #壁との交点がなければNoneを返す
        if min(r1.begin().x, r1.end().x) < sx < max(r1.begin().x, r1.end().x) and min(r2.begin().x, r2.end().x) < sx < max(r2.begin().x, r2.end().x):
            return Vec2(sx, sy)
        else: 
            None

    @staticmethod
    def with2p(begin: Vec2, end: Vec2) -> Any:
        '''
        位置ベクトルと方向ベクトルではなく、始点と終点からレイを作る。
        return: Ray2(begin, end.sub(begin))
        '''
        return Ray2(begin, end.sub(begin))
    

class Player:
    '''
    プレイヤーのクラス
    methods: self.pos{Vec2}, self.angle{int}
    '''
    
    def __init__(self):
        self.pos: Vec2 = Vec2(0,0) #初期値
        self.angle: int = 0 #初期値

class Level:
    '''
    壁を描画する
    '''
    def __init__(self) -> Any:
        pass

    walls: list = []
    tileMap: str = ''
    tileSize: int = 0
    mapWidth: int = 0
    mapHeight: int = 0

    def tileAt(self, x: int , y: int ) -> str:
        '''
        タイルの現在位置を返す
        '''
        return self.tileMap[self.mapWidth*y + x ]

    def addWorldEdges(self) -> list :
        '''
        マップの端をwallsに追加
        '''
        s: int = self.tileSize
        w: int = self.mapWidth
        h: int = self.mapHeight

        self.walls.append(Ray2(Vec2(0,0), Vec2(s*w, 0)))
        self.walls.append(Ray2(Vec2(0,0), Vec2(0, s*h)))
        self.walls.append(Ray2(Vec2(s*w, s*h), Vec2(-s*w, 0)))
        self.walls.append(Ray2(Vec2(s*w,s*h), Vec2(0, -s*h)))
    
    def addtileMap(self, tileMap: str, width: int, height: int, size:int) -> list:
        '''
        tileMap(str)から壁をタイルの形式で追加
        '''
        Level.tileMap = tileMap
        Level.mapWidth = width
        Level.mapHeight = height
        Level.tileSize = size
        #print(Level.tileMap)
        s = size
        y: int = 0

        while y < Level.mapHeight :
            x: int = 0
            while x < Level.mapWidth:
                tile = self.tileAt(x, y)
                if tile == 'O' or tile == 'X':
                    Level.walls.append(Ray2(Vec2(s*x, s*y), Vec2(s, 0)))
                    Level.walls.append(Ray2(Vec2(s*x, s*y), Vec2(0, s)))
                    if y < 9 and self.tileAt(x, y + 1) == '.':
                        Level.walls.append(Ray2(Vec2(s*x, s*y + s), Vec2(s, 0)))
                    if self.tileAt(x+1, y) == '.':
                        Level.walls.append(Ray2(Vec2(s*x + s, s*y), Vec2(0, s)))
                    if tile == 'X':
                        Level.walls.append(Ray2(Vec2(s*x, s*y), Vec2(s, s)))
                        Level.walls.append(Ray2(Vec2(s*x + s, s*y), Vec2(-s, s)))
                x  += 1
            y += 1

class Game():
    def __init__(self) -> None:
        self.player = Player()
        self.level = Level()

    def reset(self):
        self.player.pos = Vec2(118, 201)
        self.player.anlge =  -pi/2

def constrain(value, min_value: int, max_value: int) -> int:
    '''
    min_value < value < max_valueの範囲に値を制限する
    この範囲より小さければvalue = min_value
    大きければvalue = max_value
    '''
    return min(max_value, max(min_value, value))

global game

def main():
    (w,h) = (900,900)   # 画面サイズ
    
    game = Game()
    game.reset()
    wall_str = \
        '........' +\
        '........' +\
        '..OOO...' +\
        '..O.....' +\
        '........' +\
        '....X...' +\
        '........' +\
        '......O.' +\
        'OO...OO.' +\
        'OO...O..'
    
    game.level.addtileMap(wall_str,8,10,35)
    game.level.addWorldEdges()
    pygame.init()       #初期化
    pygame.display.set_mode((w, h), 0, 32)  # 画面設定
    font = pygame.font.Font(None, 30)  #fontの設定
    screen = pygame.display.get_surface()

    while (1):
        player = game.player
        pygame.draw.circle(screen, PLAYER_COLOR, (player.pos.x, player.pos.y), PLAYER_STROKE)
        # キーイベント処理(playerの移動)
        pressed_key = pygame.key.get_pressed()
        # イベント処理
        for event in pygame.event.get():
            if event.type == MOUSEMOTION:
                player.pos.x, player.pos.y = event.pos
            # 画面の閉じるボタンを押したとき
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            # キーを押したとき
            if event.type == KEYDOWN:
                # ESCキーなら終了
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        """
        if pressed_key[K_LEFT]:
            player.pos.x-=1
        if pressed_key[K_RIGHT]:
            player.pos.x+=1
        if pressed_key[K_UP]:   
            player.pos.y-=1
        if pressed_key[K_DOWN]:
            player.pos.y+=1
        """
        #視点移動
        if pressed_key[K_q]:
            player.angle -= pi / 120
        if pressed_key[K_e]:
            player.angle += pi / 120 

        pygame.display.update()     # 画面更新
        pygame.time.wait(30)        # 更新時間間隔
        screen.fill((0, 20, 0, 0))  # 画面の背景色

        # 壁を描画
        walls = game.level.walls
        
        for i in walls:
            pygame.draw.line(screen, WALL_COLOR, (i.begin().x, i.begin().y), (i.end().x, i.end().y), WALL_STROKE)
        
        #3DViewを描画
        viewRect: Vec2 = Ray2(Vec2(380, 40), Vec2(320, 240))

        fov: int = pi / 2
        center_angle: int = player.angle
        degree_angle: int = -(center_angle * 180 / pi)
        leftAngle: int = center_angle - fov/2
        rightAngle: int = center_angle + fov/2
        beam_total: int = 35
        beam_index: int = -1
        angle: int = leftAngle
        
        while angle<rightAngle-0.01:
            beam_index += 1
            angle += fov/beam_total

            #現在向いている角度を表示
            text = font.render("Player Angle: {}".format(int(degree_angle%360)), True, (255,255,255))
            screen.blit(text, [200, 400])

            beam: Ray2 = Ray2(player.pos.copy(), Vec2(cos(angle), sin(angle)).mult(120))
            
            #Rayが2枚以上の壁に当たっていたら、一番近いものを採用
            allHitBeamsList: list = list(map(lambda x: beam.intersection(x) , walls))
            allHitBeamsNotNone: list = list(filter(lambda y : y is not None, allHitBeamsList))
            allHitBeamsWays: list = list(map(lambda x: x.sub(beam.begin()), allHitBeamsNotNone))
            if len(allHitBeamsWays) == 0:
                pygame.draw.line(screen, RAY_STROKE_COLOR, (beam.begin().x, beam.begin().y), (beam.end().x, beam.end().y), RAY_STROKE)
                continue
            hitBeam: Vec2 = reduce(lambda x, y: x if x.mag() < y.mag() else y, allHitBeamsWays)

            #3DViewに縦線を1本表示
            hitPos: Vec2 = hitBeam.add(beam.begin())
            #FPS視点を表示
            wallDist: float = hitBeam.mag()
            wallPerDist: float = wallDist * cos(angle - center_angle)
            lineHeight: int = constrain(3500 / wallPerDist, 0, viewRect.way.y)
            lineHeight -= lineHeight % 8
            lineBegin: Vec2 = viewRect.begin().add(
                Vec2(
                    viewRect.way.x/beam_total*beam_index, 
                    viewRect.way.y/2 - lineHeight/2
                )
            )
            
            pillarSize: int = 5
            tileSize: int = game.level.tileSize
            if ((hitPos.x % tileSize < pillarSize) or (hitPos.x % tileSize > tileSize - pillarSize)) and ((hitPos.y % tileSize < pillarSize) or (hitPos.y % tileSize > tileSize - pillarSize)):
                WALL_3D_COLOR: tuple = (215, 179, 111)
            else:
                WALL_3D_COLOR: tuple = (255, 255, 255)
            #3DViewの壁を描画
            pygame.draw.rect(screen, WALL_3D_COLOR, Rect(lineBegin.x, lineBegin.y, 7, lineHeight))
            #壁の色に応じたRayを俯瞰図に描画
            pygame.draw.line(screen, WALL_3D_COLOR, (player.pos.x, player.pos.y), (player.pos.add(hitBeam).x, player.pos.add(hitBeam).y), 1)
        pygame.draw.circle(screen, PLAYER_COLOR, (player.pos.x, player.pos.y), PLAYER_STROKE)
        pygame.draw.rect(screen, (0, 156, 209), Rect(viewRect.pos.x, viewRect.pos.y, viewRect.way.x, viewRect.way.y), 7)


if __name__ == "__main__":
    main()