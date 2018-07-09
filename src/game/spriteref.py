import pygame

import string
import collections

from src.items.item import ItemFactory

from src.renderengine.img import ImageModel 

FLOOR_LAYER = 0
SHADOW_LAYER = 5
WALL_LAYER = 10
ENTITY_LAYER = 15
UI_0_LAYER = 20
UI_TOOLTIP_LAYER = 25

"""Layers that follow the player"""
WORLD_LAYERS = (FLOOR_LAYER, SHADOW_LAYER,
                WALL_LAYER, ENTITY_LAYER)

all_imgs = []


def make(x, y, w, h):
    img = ImageModel(x, y, w, h)
    all_imgs.append(img)
    return img


player_idle_0 = make(0, 0, 16, 32)
player_idle_1 = make(16, 0, 16, 32)
player_idle_all = [player_idle_0, player_idle_1]

player_move_0 = make(32, 0, 16, 32)
player_move_1 = make(48, 0, 16, 32)
player_move_2 = make(64, 0, 16, 32)
player_move_3 = make(80, 0, 16, 32)
player_move_all = [player_move_0, player_move_1, player_move_2, player_move_3]

player_death_seq = [make(112 + 32*i, 208, 32, 32) for i in range(0, 5)]

player_attacks = [make(i*16, 208, 16, 64) for i in range(0, 5)]
player_squat = make(80, 240, 16, 32)
player_little_jump_down = [make(128 + i*16, 272, 16, 48) for i in range(0, 6)]

att_circles = [make(112 + 48*i, 240, 48, 32) for i in range(0, 9)]

chest_closed = make(0, 32, 16, 16)
chest_open_0 = make(16, 32, 16, 16)
chest_open_1 = make(32, 32, 16, 16)
chest_open_all = [chest_open_0, chest_open_1]

door_v = [make(112 + i*16, 64, 16, 16) for i in range(0, 6)]
door_h = [make(112 + i*16, 80, 16, 32) for i in range(0, 6)]

enemy_glorple_all = [make(0, 144, 32, 32), make(0, 176, 32, 32)]
enemy_trilla_all = [make(32, 144, 32, 32), make(32, 176, 32, 32)]
enemy_dicel_all = [make(64, 144, 32, 32), make(64, 176, 32, 32)]
enemy_flappum_all = [make(96, 144, 32, 32), make(96, 176, 32, 32)]
enemy_muncher_all = [make(128, 144, 32, 32), make(128, 176, 32, 32)]
enemy_muncher_alt_all = [make(160, 144, 32, 32), make(160, 176, 32, 32)]
enemies_all = [enemy_glorple_all, enemy_trilla_all, enemy_dicel_all,
        enemy_flappum_all, enemy_muncher_all, enemy_muncher_alt_all]

floaty_guys = [make(192, 144 + i * 16, 16, 16) for i in range(0, 2)]

potion_small = make(64, 32, 8, 8)
potion_big = make(48, 32, 16, 16)

item_piece_small = make(72, 32, 4, 4)
item_piece_bigs = [make(i*16, 96, 16, 16) for i in range(0, 6)]
item_entities = {}  # cubes -> sprite

small_shadow = make(80, 32, 16, 8)
medium_shadow = make(80, 40, 16, 8)
large_shadow = make(96, 32, 32, 8)
chest_shadow = make(96, 40, 32, 8)

item_panel_top = make(640, 0, 112, 64)
item_panel_middle = make(640, 64, 112, 8)
item_panel_bottom_0 = make(640, 72, 112, 8)
item_panel_bottom_1 = make(640, 80, 112, 8)  # if no bonus attributes

inv_panel_top = make(480, 0, 160, 128)
inv_panel_mid = make(480, 128, 160, 16)
inv_panel_bot = make(480, 144, 160, 16)

end_level_consoles = [make(i*16, 272, 16, 32) for i in range(0, 8)]

explosions = [make(i*16, 128, 16, 16) for i in range(0, 8)]

progress_bars = [make((i // 4)*16, (i % 4)*4 + 336, 16, 4) for i in range(0, 16)]

health_bar_top = make(544, 160, 256, 16)
health_bar_full = make(544, 176, 256, 16)
health_bars_with_length = []
for i in range(0, 256):
    health_bars_with_length.append(make(544, 176, i, 16))
health_bars_with_length.append(health_bar_full)


def get_health_bar(pcnt_full):
    return health_bars_with_length[round(pcnt_full * 256)]


_chars = [letter for letter in string.ascii_lowercase]
_chars.extend(["+", "-", "\"", ".", ",", "!", "?", "_", "~", "%", "=", ":", "'"])
_qmark = make(160, 115, 5, 5)
alphabet = collections.defaultdict(lambda: _qmark)
for i in range(0, len(_chars)):
    alphabet[_chars[i]] = make(5*i, 115, 5, 5) if _chars[i] != "?" else _qmark
for i in range(0, 10):
    c = "0123456789"[i]
    alphabet[c] = make(5*i, 120, 5, 5)

_cached_text = ["att:", "def:", "vit:", "miss", "dodge", "inventory", "lvl:", "room:",
               "kill:", "hp:", "dps:"]
_cached_lengths = set([len(t) for t in _cached_text])
cached_text_imgs = {}


def split_text(text, add_to=None):
    if add_to is None:
        add_to = []

    if len(text) == 0:
        return add_to
    elif len(text) == 1:
        add_to.append(text)
        return add_to
    else:
        for length in _cached_lengths:
            if len(text) >= length:
                if text[:length] in cached_text_imgs:
                    add_to.append(text[:length])
                    split_text(text[length:], add_to)
                    return add_to
        add_to.append(text[0])
        split_text(text[1:], add_to)
        return add_to


"""Lookup table for wall sprites:   
       0    1    2
    * -- * -- * -- *
    |  1 |  2 |  4 |
    * -- * -- * -- *
  7 |128 |  x |  8 | 3
    * -- * -- * -- *
    | 64 | 32 | 16 |
    * -- * -- * -- *  
       6    5    4
"""
walls = [None] * 256

"""Lookup table for floor sprites:
    * -- * -- *
    |  2 |  4 |
    * -- * -- *
    |  1 |  x |
    * -- * -- * 
"""
floors = [make(i*16, 48, 16, 16) for i in range(0, 8)]
floor_totally_dark = make(128, 48, 16, 16)
floor_hidden = make(144, 48, 16, 16)


def _get_wall_corner_loc(spot, bools):
    orig_walls = [0, 64, 64, 32] # x, y, w, h
    if spot == "TL":
        y = 0
        x = 1*bools[7] + 2*bools[0] + 4*bools[1]
    elif spot == "TR":
        y = 1
        x = 1*bools[3] + 2*bools[2] + 4*bools[1]
    elif spot == "BL":
        y = 2
        x = 1*bools[7] + 2*bools[6] + 4*bools[5]
    else:
        y = 3
        x = 1*bools[3] + 2*bools[4] + 4*bools[5]
        
    return (orig_walls[0] + x*8, orig_walls[1] + y*8, 8, 8)
        
    
def build_spritesheet(raw_image):
    """
        returns: Surface
    """
    global walls
    sheet_size = (raw_image.get_width(), raw_image.get_height() + 1000)
    sheet = pygame.Surface(sheet_size, pygame.SRCALPHA, 32) 
    sheet.fill((255, 255, 255, 0))
    sheet.blit(raw_image, (0, 0))

    print("building approx 256 wall sprites...")

    dupe_preventer = {}
    draw_x = 0
    draw_y = raw_image.get_height()
    
    for i in range(0, 256):
        bools = [int(x) for x in reversed(list('{0:0b}'.format(i)))]
        bools= bools + [0]*(8 - len(bools))
        
        tl = _get_wall_corner_loc("TL", bools)
        tr = _get_wall_corner_loc("TR", bools)
        bl = _get_wall_corner_loc("BL", bools)
        br = _get_wall_corner_loc("BR", bools)
        key = (tl, tr, bl, br)
        if key in dupe_preventer:
            walls[i] = dupe_preventer[key]
        else:
            sheet.blit(raw_image, (draw_x, draw_y), tl)
            sheet.blit(raw_image, (draw_x + 8, draw_y), tr)
            sheet.blit(raw_image, (draw_x, draw_y + 8), bl)
            sheet.blit(raw_image, (draw_x + 8, draw_y + 8), br)
            model = make(draw_x, draw_y, 16, 16)
            walls[i] = model
            dupe_preventer[key] = model
            
            draw_x += 16
            if draw_x > sheet_size[0] - 16:
                draw_x = 0
                draw_y += 16

    draw_x = 0
    draw_y += 16

    for text in _cached_text:
        width = len(text) * (5 + 1) - 1
        if draw_x + width >= sheet_size[0]:
            draw_y += 6
            draw_x = 0

        cached_text_imgs[text] = make(draw_x, draw_y, width, 5)

        for letter in text:
            if letter != " ":
                letter_img = alphabet[letter]
                sheet.blit(raw_image, (draw_x, draw_y), letter_img.rect())
                draw_x += 6

    draw_y += 6

    all_cube_configs = ItemFactory.get_all_possible_cube_configs(n=(5, 6, 7))
    print("building {} item sprites...".format(len(all_cube_configs)))

    draw_x = 0
    piece_rect = item_piece_small.rect()
    for item in all_cube_configs:
        w = 1
        h = 1
        for c in item:
            dest = (draw_x + c[0]*4, draw_y + c[1]*4)
            sheet.blit(raw_image, dest, piece_rect)
            w = max(c[0] + 1, w)
            h = max(c[1] + 1, h)

        item_entities[item] = make(draw_x, draw_y, w*4, h*4)
        draw_x += 20
        if draw_x > sheet_size[0] - 20:
            draw_x = 0
            draw_y += 20

    for img in all_imgs:
        img.set_sheet_size(sheet_size)
    
    # pygame.image.save(sheet, "src/spritesheet.png")
    
    return sheet


if __name__ == "__main__":
    raw = pygame.image.load("assets/image.png")
    output = build_spritesheet(raw)
    pygame.image.save(output, "src/spritesheet.png")
    
