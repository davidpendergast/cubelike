import math

import src.utils.colors as colors
import src.game.balance as balance


_ALL_STAT_TYPES = {}  # stat_id -> StatType


class StatType:

    def __init__(self, stat_id, color=colors.LIGHT_GRAY, desc=None, local_desc=None, enemy_desc=None):
        self._stat_id = stat_id
        self._color = color
        self._desc = desc
        self._local_desc = local_desc
        self._enemy_desc = enemy_desc

        _ALL_STAT_TYPES[stat_id] = self

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

    def get_enemy_desc(self, stat_provider):
        value = stat_provider.stat_value(self)
        if self._enemy_desc is None or value <= 0:
            return None
        else:
            return self._enemy_desc.format(value)

    def __eq__(self, other):
        if isinstance(other, StatType):
            return self.get_id() == other.get_id()
        else:
            return False

    def __hash__(self):
        return hash(self.get_id())


class RangedStatType(StatType):
    def __init__(self):
        StatType.__init__(self, "UNARMED_RANGE", desc="+{} to Unarmed Range")

    def get_enemy_desc(self, stat_provider):
        value = stat_provider.stat_value(self)
        if value <= 0:
            return None
        elif stat_provider.stat_value(StatTypes.UNARMED_IS_PROJECTILE) > 0:
            return "Ranged"
        else:
            return "Leaping"


class StatTypes:
    ATT = StatType("ATT", color=colors.RED, desc="+{} to All Attacks")
    DEF = StatType("DEF", color=colors.BLUE, desc="+{} Defense")
    VIT = StatType("VIT", color=colors.GREEN, desc="+{} Vitality")
    SPEED = StatType("SPEED", color=colors.YELLOW, desc="+{} Speed")

    UNARMED_ATT = StatType("UNARMED_ATT", color=colors.RED, desc="+{} to Unarmed Attacks")
    UNARMED_RANGE = RangedStatType()
    UNARMED_IS_PROJECTILE = StatType("UNARMED_IS_PROJECTILE", desc="Unarmed Attacks are Projectiles")
    THROWN_ATT = StatType("THROWN_ATT", color=colors.RED, desc="+{} to Throw Damage", local_desc="+{} Damage when Thrown")
    MIN_LIGHT_LEVEL = StatType("MIN_LIGHT_LEVEL")
    LIGHT_LEVEL = StatType("LIGHT_LEVEL", desc="+{} Light Level", color=colors.LIGHT_BLUE)
    HP_REGEN = StatType("HP_REGEN", color=colors.GREEN, desc="+{} HP per Turn", enemy_desc="Regenerating")

    POISON = StatType("POISON", desc="-{} HP per Turn", color=colors.PURPLE)  # poison that's currently inflicted
    POISON_ON_HIT = StatType("POISON_ON_HIT", color=colors.PURPLE, desc="Inflicts Poison on Hit (lasts {} turns)",
                             local_desc="Inflicts Poison on Hit (lasts {} turns)", enemy_desc="Poisonous")

    NULLIFICATION = StatType("NULLIFICATION", desc="Unaffected by Status Effects and Curses",
                             color=colors.WHITE, enemy_desc="Nullifying")

    CONFUSION = StatType("CONFUSION", desc="Moving is more difficult", color=colors.RED)
    CONFUSION_ON_HIT = StatType("CONFUSION_ON_HIT", color=colors.RED, desc="Inflicts Confusion on Hit (lasts {} turns)",
                                local_desc="Inflicts Confusion on Hit (lasts {} turns)", enemy_desc="Confusing")

    SLOW_ON_HIT = StatType("SLOW_ON_HIT", color=colors.DARK_YELLOW, desc="Inflicts Slowness on Hit (lasts {} turns)",
                           local_desc="Inflicts Slowness on Hit (lasts {} turns)", enemy_desc="Slowing")

    GRASPED = StatType("GRASPED", desc="Unable to move", color=colors.ORANGE)
    GRASP_ON_MELEE_HIT = StatType("GRASP_ON_MELEE_HIT", color=colors.ORANGE, desc="Grasps on Melee Hit (lasts {} turns)",
                                  local_desc="Grasps on Melee Hit (lasts {} turns)", enemy_desc="Grasping")

    HEAL_AT_LEVEL_END = StatType("HEAL_AT_LEVEL_END", desc="+{} HP at End of Level", color=colors.GREEN)

    # these are currently only used to control enemy behavior.
    INTELLIGENCE = StatType("INTELLIGENCE")
    WEALTH = StatType("WEALTH")

    PLUS_SPEED_ON_HIT = StatType("PLUS_SPEED_ON_HIT",
                                 color=colors.YELLOW,
                                 desc="+{}".format(balance.STATUS_EFFECT_PLUS_SPEED_VAL) + " SPD on Hit (lasts {} turns)",
                                 local_desc="+{}".format(balance.STATUS_EFFECT_PLUS_SPEED_VAL) + " SPD on Hit (lasts {} turns)")

    PLUS_DEFENSE_ON_HIT = StatType("PLUS_DEFENSE_ON_HIT",
                                   color=colors.BLUE,
                                   desc="+{}".format(balance.STATUS_EFFECT_PLUS_DEFENSE_VAL) + " DEF on Hit (lasts {} turns)",
                                   local_desc="+{}".format(balance.STATUS_EFFECT_PLUS_DEFENSE_VAL) + " DEF on Hit (lasts {} turns)")

    HP_ON_KILL = StatType("HP_ON_KILL",
                          color=colors.GREEN,
                          desc="+{} HP on Kill",
                          local_desc="Kills with this item grant +{} HP")

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

    def stat_value_with_item(self, stat_type, item):
        res = self.stat_value(stat_type)
        if item is None and stat_type == StatTypes.ATT:
            res += self.stat_value(StatTypes.UNARMED_ATT)
        elif item is not None:
            res += item.stat_value(stat_type, local=True)
        return res


def default_player_stats():
    return BasicStatLookup({
        StatTypes.ATT: 0,
        StatTypes.VIT: 8,
        StatTypes.DEF: 1,
        StatTypes.UNARMED_ATT: 2,
        StatTypes.UNARMED_RANGE: 1,
        StatTypes.LIGHT_LEVEL: 4,
        StatTypes.MIN_LIGHT_LEVEL: 2,
        StatTypes.SPEED: 4,
        StatTypes.HEAL_AT_LEVEL_END: 5,
        StatTypes.INTELLIGENCE: 5,  # affects nothing, but there's no reason to be mean
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

