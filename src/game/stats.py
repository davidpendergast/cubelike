import math

import src.utils.colors as colors
import src.game.balance as balance


_ALL_STAT_TYPES = {}  # stat_id -> StatType


class StatType:

    def __init__(self, stat_id, color=colors.LIGHT_GRAY, desc=None, local_desc=None):
        self._stat_id = stat_id
        self._color = color
        self._desc = desc
        self._local_desc = local_desc

        _ALL_STAT_TYPES[stat_id] = _ALL_STAT_TYPES

    def get_color(self):
        return self._color

    def get_id(self):
        return self._stat_id

    def __repr__(self):
        return str(self.get_id())

    def is_hidden(self, local=False):
        if local:
            return self._local_desc is None
        else:
            return self._desc is None

    def get_description(self, value, local=False):
        if not local:
            if self._desc is None:
                return "{}: {}".format(self.get_id(), value)
            else:
                return self._desc.format(value)
        else:
            if self._local_desc is None:
                return "{}: {} (local)".format(self.get_id(), value)
            else:
                return self._local_desc.format(value)

    def __eq__(self, other):
        if isinstance(other, StatType):
            return self.get_id() == other.get_id()
        else:
            return False

    def __hash__(self):
        return hash(self.get_id())


class StatTypes:
    ATT = StatType("ATT", color=colors.RED, desc="+{} to All Attacks")
    DEF = StatType("DEF", color=colors.BLUE, desc="+{} Defense")
    VIT = StatType("VIT", color=colors.GREEN, desc="+{} Vitality")
    SPEED = StatType("SPEED", color=colors.YELLOW, desc="+{} Speed")

    UNARMED_ATT = StatType("UNARMED_ATT", color=colors.RED, desc="+{} to Unarmed Attacks")
    MIN_LIGHT_LEVEL = StatType("MIN_LIGHT_LEVEL")
    LIGHT_LEVEL = StatType("LIGHT_LEVEL", desc="+{} Light Level")
    HP_REGEN = StatType("HP_REGEN", desc="+{} HP per Turn", color=colors.GREEN)
    POISON = StatType("POISON", desc="-{} HP per Turn", color=colors.PURPLE)

    ENERGY_DRAIN = StatType("ENERGY_DRAIN", desc="+{} Energy Drain on Hit",
                            local_desc="Drains +{} Energy on Hit")

    PLUS_DEFENSE_ON_HIT = StatType("PLUS_DEFENSE_ON_HIT",
                                   color=colors.BLUE,
                                   desc="+{}".format(balance.STATUS_EFFECT_PLUS_DEFENSE_VAL) + " DEF on Hit (lasts {} turns)",
                                   local_desc="+{}".format(balance.STATUS_EFFECT_PLUS_DEFENSE_VAL) + " DEF on Hit (lasts {} turns)")

    @staticmethod
    def all_types():
        for stat_id in _ALL_STAT_TYPES:
            yield _ALL_STAT_TYPES[stat_id]


class StatProvider:

    def stat_value(self, stat_type, local=False):
        return 0

    def all_nonzero_stat_types(self, local=False):
        """returns: a list of all StatTypes with non-zero values on this StatProvider."""
        for s_type in StatTypes.all_types():
            if self.stat_value(s_type, local=local) != 0:
                yield s_type


def default_player_stats():
    return BasicStatLookup({
        StatTypes.ATT: 0,
        StatTypes.VIT: 8,
        StatTypes.DEF: 1,
        StatTypes.UNARMED_ATT: 2,
        StatTypes.LIGHT_LEVEL: 4,
        StatTypes.MIN_LIGHT_LEVEL: 2,
        StatTypes.SPEED: 4
    })


class BasicStatLookup(StatProvider):

    def __init__(self, lookup_dict):
        self.lookup = lookup_dict

    def stat_value(self, stat_type, local=False):
        if stat_type in self.lookup:
            return self.lookup[stat_type]
        else:
            return 0

    def set_stat_value(self, stat_type, val):
        self.lookup[stat_type] = val

