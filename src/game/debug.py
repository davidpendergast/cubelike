import os

_IS_DEV = os.path.exists("this_is_dev.txt")

# flip to toggle all debug settings
_DEBUG = True

# these flags can be manually flipped before launching to alter the game's behavior
_IGNORE_LOOT_LEVELS = False
_PLAYER_CANT_DIE = False
_MAP_SEES_ALL = False
_UNLIMITED_TRADES = False
_HOLY_ARTIFACTS_100x_MORE_LIKELY = False


def is_dev():
    return _IS_DEV


def is_debug():
    return _DEBUG and is_dev()


def ignore_loot_levels():
    return is_debug() and _IGNORE_LOOT_LEVELS


def player_cant_die():
    return is_debug() and _PLAYER_CANT_DIE


def map_sees_all():
    return is_debug() and _MAP_SEES_ALL


def unlimited_trades():
    return is_debug() and _UNLIMITED_TRADES
