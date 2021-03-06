import pygame
import pygame as pg
import pymunk

from src.state.state_machine import State
from src.state.game.game_objects import Player
from src.state.game.game_objects import Map
from src.state.game.game_objects import Camera
from src.state.game.game_objects import ItemSpawner
from src.sound.sound import music
from src.common.common_objects import BackGround
from src.common.common_objects import HpBar
from src.common.common_objects import Button
from src.common.common_objects import PotionBar
from src.common.common_objects import Text
from src.common.config import SCREEN_WIDTH
from src.common.config import SCREEN_HEIGHT
from src.common.config import PLAYER_COLLISION_TYPE
from src.common.config import FRUIT_COLLISION_TYPE
from src.common.config import SLIME_COLLISION_TYPE
from src.common.config import THROW_BOX_COLLISION_TYPE
from src.common.config import UP_SEGMENT_COLLISION_TYPE
from src.common.config import MAP_WIDTH
from src.common.config import TILE_WIDTH
from src.common.config import MAP_HEIGHT
from src.common.config import TILE_HEIGHT
from src.common.config import SCALE


class Game(State):
    def __init__(self):
        super().__init__()
        self.name = "GAME"
        self.group_all = None
        self.ui = None
        self.space = None
        self.map = None
        self.player = None
        self.background = None
        self.camera = None
        self.score = None
        self.to_title_btn = None
        self.target = None
        self.grab = None
        self.pause_ui = None
        self.game_over_ui = None
        self.item_spawner = None
        self.continue_btn = None
        self.slime_collision = None
        self.hp_bar = None
        self.potion_bar = None
        self.pause = False
        self.is_game_over = False
        self.game_over_text = None
        self.player_fruit_collision_handler = None
        self.player_slime_collision_handler = None
        self.thrown_box_slime_collision_handler = None
        self.thrown_box_up_segment_handler = None
        self.reset()

    def reset(self):
        self.group_all = pg.sprite.Group()
        self.ui = pg.sprite.Group()
        self.pause_ui = pg.sprite.Group()
        self.target = pg.sprite.Group()
        self.grab = pg.sprite.Group()
        self.game_over_ui = pg.sprite.Group()
        self.space = pymunk.Space()
        self.space.gravity = (0, 10)
        self.item_spawner = ItemSpawner(self)
        self.map = Map(self)
        self.player = Player(self)
        self.camera = Camera(self)
        self.potion_bar = PotionBar()
        self.background = BackGround()
        self.hp_bar = HpBar(3)
        self.score = Text((10, 10), "score: 0", "topleft")
        self.game_over_text = Text((SCREEN_WIDTH / 2, SCREEN_HEIGHT * 3 / 8), "Game Over", "midtop")
        self.to_title_btn = Button((SCREEN_WIDTH / 2, SCREEN_HEIGHT * 4 / 8), "Title", "midtop", self.to_title)
        self.continue_btn = Button((SCREEN_WIDTH / 2, SCREEN_HEIGHT * 5 / 8), "Continue", "midtop", self.continue_click)
        for group in self.map.layers:
            self.group_all.add(*group.sprites())
        for group in self.map.target_groups:
            self.target.add(*group)
        for group in self.map.grab_groups:
            self.grab.add(*group)
        self.group_all.add(self.player)
        self.ui.add(self.score)
        self.ui.add(self.hp_bar)
        self.ui.add(self.potion_bar)
        self.pause_ui.add(self.to_title_btn)
        self.pause_ui.add(self.continue_btn)
        self.game_over_ui.add(self.game_over_text)
        self.game_over_ui.add(self.to_title_btn)
        self.pause = False
        self.is_game_over = False

        self.player_fruit_collision_handler = self.space.add_collision_handler(PLAYER_COLLISION_TYPE, FRUIT_COLLISION_TYPE)
        self.player_fruit_collision_handler.begin = self.player_fruit_collision_handler_begin

        self.slime_collision = self.space.add_collision_handler(SLIME_COLLISION_TYPE, SLIME_COLLISION_TYPE)
        self.slime_collision.begin = self.slime_begin_handler

        self.player_slime_collision_handler = self.space.add_collision_handler(PLAYER_COLLISION_TYPE, SLIME_COLLISION_TYPE)
        self.player_slime_collision_handler.begin = self.player_slime_collision_handler_begin

        self.thrown_box_slime_collision_handler = self.space.add_collision_handler(THROW_BOX_COLLISION_TYPE, SLIME_COLLISION_TYPE)
        self.thrown_box_slime_collision_handler.begin = self.thrown_box_slime_collision_handler_begin

        self.thrown_box_up_segment_handler = self.space.add_collision_handler(THROW_BOX_COLLISION_TYPE, UP_SEGMENT_COLLISION_TYPE)
        self.thrown_box_up_segment_handler.begin = self.thrown_box_up_segment_handler_begin

    @staticmethod
    def thrown_box_up_segment_handler_begin(space, arbiter, data):
        box = space.shapes[0].body.sprite
        if box.is_throwing:
            box.is_throwing = False
        return True

    @staticmethod
    def thrown_box_slime_collision_handler_begin(space, arbiter, data):
        box = space.shapes[0].body.sprite
        slime = space.shapes[1].body.sprite
        if box.is_throwing:
            box.get_hit(1)
            slime.get_hit(2)
            box.is_throwing = False
        return True

    @staticmethod
    def player_slime_collision_handler_begin(space, arbiter, data):
        player = space.shapes[0].body.sprite
        slime = space.shapes[1].body.sprite
        collide_vector = player.body.position - slime.body.position
        collide_vector = collide_vector / collide_vector.length
        player.get_hit(collide_vector)
        return False

    @staticmethod
    def slime_begin_handler(space, arbiter, data):
        return False

    @staticmethod
    def player_fruit_collision_handler_begin(space, arbiter, data):
        fruit = space.shapes[1].body.sprite
        fruit.eat()
        return False

    def game_over(self, is_win=False):
        if is_win:
            self.game_over_text.set_text("Congratulation !")
            music.load("victory.mp3")
        else:
            music.load("game-over.mp3")
        music.start()
        self.is_game_over = True

    def startup(self, now, to_persist):
        super().startup(now, to_persist)
        music.load("field.mp3")
        music.start()
        self.reset()

    def cleanup(self):
        self.group_all = None
        self.ui = None
        self.space = None
        self.map = None
        self.player = None
        self.background = None
        self.camera = None
        self.score = None
        self.to_title_btn = None
        self.continue_btn = None
        self.pause = False
        self.is_game_over = False
        return super().cleanup()

    def continue_click(self):
        self.pause = False

    def to_title(self):
        self.next_state_name = "TITLE"
        self.done = True

    def accept_events(self, events):
        if not self.pause and not self.is_game_over:
            for event in events:
                if event.type == pg.KEYDOWN:
                    if event.key == pygame.K_a:
                        self.player.jump()
                    elif event.key == pygame.K_s:
                        self.player.attack()
                    elif event.key == pygame.K_ESCAPE:
                        self.pause = True
                    elif event.key == pygame.K_d:
                        self.player.grab()
                elif event.type == pg.KEYUP:
                    if event.key == pygame.K_f:
                        self.player.throw()
        elif self.pause:
            for event in events:
                if event.type == pg.MOUSEBUTTONDOWN:
                    self.to_title_btn.click(event.pos)
                    self.continue_btn.click(event.pos)
        elif self.game_over:
            for event in events:
                if event.type == pg.MOUSEBUTTONDOWN:
                    self.to_title_btn.click(event.pos)

    def update(self, now, mouse_pos, keyboard):
        if not self.pause and not self.is_game_over:
            self.group_all.update(now)
            self.item_spawner.items.update(now)
            self.background.update(now)
            self.potion_bar.set_remain(self.player.power_up_duration)
            self.space.step(0.2)
            self.camera.update()
            if keyboard[pg.K_LEFT]:
                self.player.move_left()
            elif keyboard[pg.K_RIGHT]:
                self.player.move_right()
            else:
                self.player.stop_moving()

            if keyboard[pg.K_f]:
                self.player.charge_throw()

    def draw(self, surface: pg.Surface, interpolate):
        big_surface = pg.Surface((MAP_WIDTH * TILE_WIDTH * SCALE, MAP_HEIGHT * TILE_HEIGHT * SCALE), pygame.SRCALPHA)
        self.group_all.draw(big_surface)
        self.item_spawner.items.draw(big_surface)
        surface.blit(self.background.image, self.background.rect)
        surface.blit(big_surface, (-self.camera.offset_x, -self.camera.offset_y))
        self.ui.draw(surface)
        if self.pause:
            self.pause_ui.draw(surface)
        if self.is_game_over:
            self.game_over_ui.draw(surface)
