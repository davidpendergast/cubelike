import pygame

from renderengine.img import ImageModel 

all_imgs = []

def make(x, y, w, h):
    img = ImageModel(x, y, w, h)
    all_imgs.append(img)
    return img
    
player_idle_0 = make(0, 0, 16, 32)
player_idle_1 = make(16, 0, 16, 32)

player_move_0 = make(32, 0, 16, 32)
player_move_1 = make(48, 0, 16, 32)
player_move_2 = make(64, 0, 16, 32)
player_move_3 = make(80, 0, 16, 32)
player_move_all = [player_move_0, player_move_1, player_move_2, player_move_3]

chest = make(0, 32, 16, 16)
chest_open_1 = make(16, 32, 16, 16)
chest_open_2 = make(32, 32, 16, 16)

"""Lookup table for wall sprites:   
       0    1    2
    * -- * -- * -- *
    |  1 |  2 |  4 |
    * -- * -- * -- *
  7 |128 |  x |  8 | 3
    * -- * -- * -- *
    | 64 | 32 | 16 | 4
    * -- * -- * -- *  
       6    5 
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
    sheet_size = (raw_image.get_width(), raw_image.get_height() + 128)
    sheet = pygame.Surface(sheet_size, pygame.SRCALPHA, 32) 
    sheet.blit(raw_image, (0, 0))
    
    dupe_preventer = {}
    draw_x = 0
    draw_y = raw_image.get_height()
    
    for i in range(0, 256):
        bools = [int(x) for x in list('{0:0b}'.format(i))]
        bools.extend([0]*(8 - len(bools)))
        
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
    
    for img in all_imgs:
        img.set_sheet_size(sheet_size)
    
    return sheet
    
if __name__ == "__main__":
    raw = pygame.image.load("image.png")
    output = build_spritesheet(raw)
    pygame.image.save(output, "spritesheet.png")
    
    print("walls[128] = {}".format(walls[128]))
    
