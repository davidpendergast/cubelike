import pygame

import src.spriteref as spriteref
from src.globalstate import GlobalState
from src.inputs import InputState

from src.world.worldstate import World
from src.world.entities import Player, Enemy, ChestEntity
import src.renderengine.img as img
from src.renderengine.engine import RenderEngine

print("launching Cubelike...")
print("running pygame version: " + pygame.version.ver)


SCREEN_SIZE = (800, 600)

def build_me_a_world(width, height):
    import random
    w = World(width, height)
    for x in range(0, width):
        for y in range(0, height):
            if random.random() < 0.33:
                w.set_geo(x, y, World.WALL)
            else:
                w.set_geo(x, y, World.FLOOR)
                if random.random() < 0.05:
                    i = int(random.random() * len(spriteref.enemies_all))
                    e = Enemy(0, 0, spriteref.enemies_all[i])
                    w.add(e, gridcell=(x, y))
                elif random.random() < 0.05:
                    w.add(ChestEntity(0, 0), gridcell=(x, y))
    return w
   
    
def run():
    pygame.init()
    mods = pygame.OPENGL | pygame.DOUBLEBUF | pygame.HWSURFACE
    screen = pygame.display.set_mode(SCREEN_SIZE, mods)
    
    input_state = InputState()
    gs = GlobalState()
    
    render_eng = RenderEngine()
    render_eng.init(*SCREEN_SIZE)
    render_eng.add_layer(gs.FLOOR_LAYER, "floors", 0, False, True)
    render_eng.add_layer(gs.BW_WALL_AND_FLOOR_LAYER, "between wall and floor", 5, False, True)
    render_eng.add_layer(gs.WALL_LAYER, "walls", 10, False, True)
    render_eng.add_layer(gs.ENTITY_LAYER, "entities", 15, True, True)
    render_eng.add_layer(gs.UI_0_LAYER, "ui_0", 20, False, False)
    render_eng.add_layer(gs.UI_1_LAYER, "ui_1", 25, False, False)
    
    raw_sheet = pygame.image.load("assets/image.png")
    img_surface = spriteref.build_spritesheet(raw_sheet)
    texture_data = pygame.image.tostring(img_surface, "RGBA", 1)
    width = img_surface.get_width()
    height = img_surface.get_height()
    render_eng.set_texture(texture_data, width, height)
    
    world = build_me_a_world(15, 15)
    
    for bun in world.get_all_bundles():
        render_eng.update(bun, layer_id=gs.WALL_LAYER)
        
    player = Player(32, 32)
    world.add(player)
    
    clock = pygame.time.Clock()    
    
    running = True
    
    while running:
        gs.update()
        input_state.update(gs)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                running = False
            elif event.type == pygame.KEYDOWN:
                input_state.set_key(event.key, True)
            elif event.type == pygame.KEYUP:
                input_state.set_key(event.key, False)
            elif event.type == pygame.MOUSEMOTION:
                input_state.set_mouse_pos(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                input_state.set_mouse_down(True)
            elif event.type == pygame.MOUSEBUTTONUP:
                input_state.set_mouse_down(False)

            if not pygame.mouse.get_focused():
                input_state.set_mouse_pos(None)
        
        world.update_all(gs, input_state, render_eng)
        
        render_eng.render_layers()
        pygame.display.flip()
        clock.tick(60)
        if gs.tick_counter % 60 == 0:
            if clock.get_fps() < 59:
                print("fps: {}".format(clock.get_fps()))
        
    
