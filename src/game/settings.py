import pygame
from src.utils.util import Utils
import src.utils.passwordgen as passwordgen
import src.game.sound_effects as sound_effects

ALL_SETTINGS = {}
ALL_KEY_SETTINGS = []


class Setting:
    def __init__(self, name, key, default):
        self.name = name
        self.key = key
        self.default = default
        ALL_SETTINGS[key] = self

    def clean(self, new_value):
        return new_value

    def on_set(self, old_value, new_value):
        pass


class KeySetting(Setting):
    def __init__(self, name, key, default, editable=True):
        Setting.__init__(self, name, key, default)
        self.editable = editable
        ALL_KEY_SETTINGS.append(self)


# these are all configurable
KEY_UP = Setting("move up", "UP", [pygame.K_w])
KEY_LEFT = Setting("move down", "LEFT", [pygame.K_a])
KEY_RIGHT = Setting("move right", "RIGHT", [pygame.K_d])
KEY_DOWN = Setting("move down", "DOWN", [pygame.K_s])
KEY_INVENTORY = Setting("inventory", "INVENTORY", [pygame.K_r])
KEY_ROTATE_CW = Setting("rotate item", "ROTATE_CW", [pygame.K_e])

num_keys = [pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
            pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]

KEY_MAPPED_ACTIONS = [Setting("action " + str(i), "ACTION_" + str(i), [num_keys[i]]) for i in range(1, 7)]

# these are locked
KEY_MENU_UP = Setting("menu up", "MENU_UP", [pygame.K_UP])
KEY_MENU_DOWN = Setting("menu down", "MENU_DOWN", [pygame.K_DOWN])
KEY_ENTER = Setting("enter", "ENTER", [pygame.K_RETURN])
KEY_EXIT = Setting("escape", "EXIT", [pygame.K_ESCAPE])

EFFECTS_VOLUME = Setting("effects volume", "EFFECTS_VOLUME", 100)
EFFECTS_VOLUME.clean = lambda val: Utils.bound(int(val), 0, 100)
EFFECTS_VOLUME.on_set = lambda old_val, new_val: sound_effects.set_volume(new_val / 100)

MUSIC_VOLUME = Setting("music volume", "MUSIC_VOLUME", 100)
MUSIC_VOLUME.clean = lambda val: Utils.bound(int(val), 0, 100)
MUSIC_VOLUME.on_set = lambda old_val, new_val: pygame.mixer.music.set_volume(new_val / 100)

LAST_PASSWORD = Setting("last password", "LAST_PASSWORD", None)
LAST_PASSWORD.clean = lambda val: val if passwordgen.is_valid(val) else None


class Settings:

    def __init__(self):
        self.values = {}
        for setting_key in ALL_SETTINGS:
            self.values[setting_key] = ALL_SETTINGS[setting_key].default

    def get(self, setting):
        return self.values[setting.key]

    def set(self, setting, val):
        try:
            old_val = self.values[setting.key]
            new_val = setting.clean(val)
            self.values[setting.key] = new_val
            print("INFO: updated setting {} from {} to {}.".format(setting.key, old_val, new_val))
            setting.on_set(old_val, new_val)
        except ValueError:
            print("ERROR: failed to set {} to {}".format(setting.key, val))

    def load_from_file(self, filename):
        try:
            loaded_values = Utils.load_json_from_path(filename)
            for key in loaded_values:
                val = loaded_values[key]
                if key in ALL_SETTINGS:
                    self.set(ALL_SETTINGS[key], val)
                else:
                    print("INFO: skipping unknown setting: {}".format(key))
            print("INFO: successfully loaded settings from {}".format(filename))

        except Exception:
            print("ERROR: failed to load settings from {}".format(filename))

    def save_to_file(self, filename):
        try:
            Utils.save_json_to_path(self.values, filename)
            print("INFO: successfully saved settings to {}".format(filename))
        except Exception:
            print("ERROR: failed to save settings to {}".format(filename))

    def up_key(self):
        return self.get(KEY_UP)

    def left_key(self):
        return self.get(KEY_LEFT)

    def right_key(self):
        return self.get(KEY_RIGHT)

    def down_key(self):
        return self.get(KEY_DOWN)

    def menu_up_key(self):
        return self.get(KEY_MENU_UP)

    def menu_down_key(self):
        return self.get(KEY_MENU_DOWN)

    def inventory_key(self):
        return self.get(KEY_INVENTORY)

    def exit_key(self):
        return self.get(KEY_EXIT)

    def enter_key(self):
        return self.get(KEY_ENTER)

    def rotate_cw_key(self):
        return self.get(KEY_ROTATE_CW)

    def all_direction_keys(self):
        for k in self.up_key():
            yield k
        for k in self.down_key():
            yield k
        for k in self.left_key():
            yield k
        for k in self.right_key():
            yield k

    def num_mapped_actions(self):
        return len(KEY_MAPPED_ACTIONS)

    def action_key(self, num):
        return self.get(KEY_MAPPED_ACTIONS[num])

    def all_in_game_keys(self):
        for k in self.all_direction_keys():
            yield k
        for i in range(0, self.num_mapped_actions()):
            for k in self.action_key(i):
                yield k
        for k in self.enter_key():
            yield k
