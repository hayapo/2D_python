from typing import Any
from numpy.lib.function_base import place
import pygame
from pygame.locals import *
import sys
from math import * 
import numpy as np
from functools import reduce

#mainで使う変数
WALL_STROKE: int = 5
WALL_COLOR: tuple = (255, 255, 255)
PLAYER_STROKE: int = 5
PLAYER_COLOR: tuple = (224, 224, 0)
RAY_STROKE_COLOR: tuple = (248, 255, 151)
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

        #r1, r2を直線とみなして交点を求める
        #r1の傾き
        t1: float = r1.way.y / r1.way.x
        #r2の傾き
        t2: float = r2.way.y / r2.way.x
        
        #各座標
        x1: float = r1.pos.x
        x2: float = r2.pos.x
        y1: float = r1.pos.y
        y2: float = r2.pos.y

        #交点の座標
        sx: float  = (t1*x1 - t2*x2 - y1 + y2) / (t1 - t2)
        sy: float = t1 * (sx - x1 ) + y1

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

def constrain(value, min_value: int, max_value: int) -> int:
    '''
    min_value < value < max_valueの範囲に値を制限する
    この範囲より小さければvalue = min_value
    大きければvalue = max_value
    '''
    return min(max_value, max(min_value, value))

def main():
    (w,h) = (900,900)   # 画面サイズ
    player = Player()
    player.pos = Vec2(100, 200)
    player.angle = -pi / 2
    wall = [
        Ray2.with2p(Vec2(50, 50), Vec2(100, 300)),
        Ray2.with2p(Vec2(100, 300), Vec2(250, 200)),
        Ray2.with2p(Vec2(250, 200), Vec2(50, 50)),
    ]

    pygame.init()       #初期化
    pygame.display.set_mode((w, h), 0, 32)  # 画面設定
    font = pygame.font.Font(None, 30)  #fontの設定
    screen = pygame.display.get_surface()

    while (1):
        pygame.draw.circle(screen, PLAYER_COLOR, (player.pos.x, player.pos.y), PLAYER_STROKE)
        # キーイベント処理(playerの移動)
        pressed_key = pygame.key.get_pressed()
        if pressed_key[K_LEFT]:
            player.pos.x-=1
        if pressed_key[K_RIGHT]:
            player.pos.x+=1
        if pressed_key[K_UP]:   
            player.pos.y-=1
        if pressed_key[K_DOWN]:
            player.pos.y+=1
        #視点移動
        if pressed_key[K_q]:
            player.angle -= pi / 120
        if pressed_key[K_e]:
            player.angle += pi / 120 

        pygame.display.update()     # 画面更新
        pygame.time.wait(30)        # 更新時間間隔
        screen.fill((0, 20, 0, 0))  # 画面の背景色

        # 壁を描画
        for i in wall:
            pygame.draw.line(screen, WALL_COLOR, (i.begin().x, i.begin().y), (i.end().x, i.end().y), WALL_STROKE)
        
        #3DViewを描画
        viewRect: Vec2 = Ray2(Vec2(380, 40), Vec2(320, 240))

        fov: int = pi / 2
        center_angle: int = player.angle
        degree_angle: int = -(center_angle * 180 / pi)
        leftAngle: int = center_angle - fov/2
        rightAngle: int = center_angle + fov/2
        beam_total: int = 32
        beam_index: int = -1
        angle: int = leftAngle

        while angle<rightAngle-0.01:
            angle += fov/beam_total
            text = font.render("Player Angle: {}".format(degree_angle%360), True, (255,255,255))
            screen.blit(text, [200, 400])
            beam_index += 1
            beam: Ray2 = Ray2(player.pos.copy(), Vec2(cos(angle), sin(angle)).mult(120))
            #pygame.draw.line(screen, RAY_STROKE_COLOR, (beam.begin().x, beam.begin().y), (beam.end().x, beam.end().y), RAY_STROKE)
            
            #Rayが2枚以上の壁に当たっていたら、一番近いものを採用
            allHitBeamsList: list = list(map(lambda x: beam.intersection(x), wall))
            allHitBeamsNotNone: list = list(filter(lambda y : y is not None, allHitBeamsList))
            allHitBeamsWays: list = list(map(lambda x: x.sub(beam.begin()), allHitBeamsNotNone))
            if len(allHitBeamsWays) == 0:
                pygame.draw.line(screen, RAY_STROKE_COLOR, (beam.begin().x, beam.begin().y), (beam.end().x, beam.end().y), RAY_STROKE)
                continue
            hitBeam: Vec2 = reduce(lambda x, y: x if x.mag() < y.mag() else y, allHitBeamsWays)

            #3DViewに縦線を1本表示
            for i in wall:
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

                if ((hitPos.x % 7 < pillarSize) or (hitPos.x % 7 > 7 - pillarSize)) and ((hitPos.y % 7 < pillarSize) or (hitPos.y > 7 - pillarSize)):
                    WALL_3D_COLOR: tuple = (255, 255, 255)
                else:
                    WALL_3D_COLOR: tuple = (215, 179, 111)

                pygame.draw.rect(screen, WALL_3D_COLOR, Rect(lineBegin.x, lineBegin.y, 7, lineHeight))

                pygame.draw.line(screen, WALL_3D_COLOR, (player.pos.x, player.pos.y), (player.pos.add(hitBeam).x, player.pos.add(hitBeam).y), 1)

        pygame.draw.rect(screen, (0, 156, 209), Rect(viewRect.pos.x, viewRect.pos.y, viewRect.way.x, viewRect.way.y), 7)

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


if __name__ == "__main__":
    main()