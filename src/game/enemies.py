import random

import src.game.spriteref as spriteref
from src.world.entities import Enemy
from src.game.stats import StatTypes
import src.game.stats as stats
import src.game.inventory as inventory
import src.items.item as item
import src.items.itemgen as itemgen


class EnemyTemplate:

    def __init__(self, name, shadow_sprite):
        self._name = name
        self._shadow_sprite = shadow_sprite

    def get_sprites(self):
        return spriteref.player_idle_arms_up_all

    def get_shadow_sprite(self):
        return self._shadow_sprite

    def get_name(self):
        return self._name

    def get_level_range(self):
        return range(0, 64)

    def get_base_stats(self):
        return stats.BasicStatLookup({
            StatTypes.VIT: 3,
            StatTypes.SPEED: 2,
            StatTypes.ATT: 0,
            StatTypes.UNARMED_ATT: 1,
            StatTypes.DEF: 1,
            StatTypes.INTELLIGENCE: 1
        })


class FlappumTemplate(EnemyTemplate):

    def __init__(self):
        EnemyTemplate.__init__(self, "Cave Crawler", spriteref.medium_shadow)

    def get_sprites(self):
        return spriteref.enemy_flappum_all

    def get_level_range(self):
        return range(0, 4)

    def get_base_stats(self):
        return stats.BasicStatLookup({
            StatTypes.VIT: 5,
            StatTypes.SPEED: 2,
            StatTypes.ATT: 0,
            StatTypes.UNARMED_ATT: 1,
            StatTypes.DEF: 2,
            StatTypes.INTELLIGENCE: 2
        })


class TrillaTemplate(EnemyTemplate):

    def __init__(self):
        EnemyTemplate.__init__(self, "Masked Adult", spriteref.large_shadow)

    def get_sprites(self):
        return spriteref.enemy_trilla_all

    def get_base_stats(self):
        return stats.BasicStatLookup({
            StatTypes.VIT: 12,
            StatTypes.SPEED: 4,
            StatTypes.ATT: 2,
            StatTypes.UNARMED_ATT: 0,
            StatTypes.DEF: 4,
            StatTypes.INTELLIGENCE: 3
        })

    def get_level_range(self):
        return range(6, 16)


class SmallFrogTemplate(EnemyTemplate):

    def __init__(self):
        EnemyTemplate.__init__(self, "Frog", spriteref.medium_shadow)

    def get_sprites(self):
        return spriteref.enemy_frog_all

    def get_base_stats(self):
        return stats.BasicStatLookup({
            StatTypes.VIT: 5,
            StatTypes.SPEED: 2,
            StatTypes.ATT: 0,
            StatTypes.UNARMED_ATT: 2,
            StatTypes.DEF: 0,
            StatTypes.INTELLIGENCE: 1
        })

    def get_level_range(self):
        return range(0, 6)


class TrilliteTemplate(EnemyTemplate):

    def __init__(self):
        EnemyTemplate.__init__(self, "Masked Child", spriteref.medium_shadow)

    def get_sprites(self):
        return spriteref.enemy_small_trilla_all

    def get_base_stats(self):
        return stats.BasicStatLookup({
            StatTypes.VIT: 4,
            StatTypes.SPEED: 4,
            StatTypes.ATT: 0,
            StatTypes.UNARMED_ATT: 2,
            StatTypes.DEF: 1,
            StatTypes.INTELLIGENCE: 1

        })

    def get_level_range(self):
        return range(3, 7)


class SmallMuncherTemplate(EnemyTemplate):

    def __init__(self, alt=False):
        self._is_alt = alt
        name = "Dark Muncher" if alt else "Small Muncher"
        EnemyTemplate.__init__(self, name, spriteref.medium_shadow)

    def get_sprites(self):
        return spriteref.enemy_muncher_small_alt_all if self._is_alt else spriteref.enemy_muncher_small_all

    def get_level_range(self):
        return range(10, 16)

    def get_base_stats(self):
        return stats.BasicStatLookup({
            StatTypes.VIT: 8,
            StatTypes.SPEED: 2,
            StatTypes.ATT: 0,
            StatTypes.UNARMED_ATT: 2,
            StatTypes.DEF: 2,
            StatTypes.INTELLIGENCE: 2
        })


class MuncherTemplate(EnemyTemplate):

    def __init__(self, alt=False):
        self._is_alt = alt
        name = "Dark Muncher" if alt else "Muncher"
        EnemyTemplate.__init__(self, name, spriteref.large_shadow)

    def get_sprites(self):
        return spriteref.enemy_muncher_alt_all if self._is_alt else spriteref.enemy_muncher_all

    def get_level_range(self):
        return range(10, 16)

    def get_base_stats(self):
        return stats.BasicStatLookup({
            StatTypes.VIT: 16,
            StatTypes.SPEED: 4,
            StatTypes.ATT: 0,
            StatTypes.UNARMED_ATT: 8,
            StatTypes.DEF: 6,
            StatTypes.INTELLIGENCE: 3
        })


class CycloiTemplate(EnemyTemplate):

    def __init__(self):
        EnemyTemplate.__init__(self, "Cyclops", spriteref.large_shadow)

    def get_sprites(self):
        return spriteref.enemy_cyclops_all

    def get_level_range(self):
        return range(6, 16)

    def get_base_stats(self):
        return stats.BasicStatLookup({
            StatTypes.VIT: 10,
            StatTypes.SPEED: 6,
            StatTypes.ATT: 0,
            StatTypes.UNARMED_ATT: 6,
            StatTypes.DEF: 2,
            StatTypes.INTELLIGENCE: 3
        })


# TODO these suck, consider deleting
class DicelTemplate(EnemyTemplate):

    def __init__(self):
        EnemyTemplate.__init__(self, "Dicel", spriteref.medium_shadow)

    def get_sprites(self):
        return spriteref.enemy_dicel_all

    def get_level_range(self):
        return range(4, 7)

    def get_base_stats(self):
        return stats.BasicStatLookup({
            StatTypes.VIT: 12,
            StatTypes.SPEED: 3,
            StatTypes.ATT: 0,
            StatTypes.UNARMED_ATT: 3,
            StatTypes.DEF: 4,
            StatTypes.INTELLIGENCE: 2
        })


class ScorpionTemplate(EnemyTemplate):

    def __init__(self):
        EnemyTemplate.__init__(self, "Wanderer", spriteref.medium_shadow)

    def get_sprites(self):
        return spriteref.enemy_scorpion_all

    def get_level_range(self):
        return range(9, 16)

    def get_base_stats(self):
        return stats.BasicStatLookup({
            StatTypes.VIT: 8,
            StatTypes.SPEED: 6,
            StatTypes.ATT: 0,
            StatTypes.UNARMED_ATT: 4,
            StatTypes.DEF: 2,
            StatTypes.INTELLIGENCE: 4,
            StatTypes.LIGHT_LEVEL: 1,  # the gimmick
        })


class FallenTemplate(EnemyTemplate):

    def __init__(self):
        EnemyTemplate.__init__(self, "The Fallen", spriteref.medium_shadow)

    def get_sprites(self):
        return spriteref.enemy_the_fallen_all

    def get_level_range(self):
        return range(8, 16)

    def get_base_stats(self):
        return stats.BasicStatLookup({
            StatTypes.VIT: 16,
            StatTypes.SPEED: 2,
            StatTypes.ATT: 0,
            StatTypes.UNARMED_ATT: 4,
            StatTypes.DEF: 4,
            StatTypes.INTELLIGENCE: 4
        })


# TODO - these also suck really bad
class FungoiTemplate(EnemyTemplate):

    def __init__(self):
        EnemyTemplate.__init__(self, "Fungoi", spriteref.medium_shadow)

    def get_sprites(self):
        return spriteref.enemy_fungoi_all

    def get_level_range(self):
        return range(12, 15)

    def get_base_stats(self):
        return stats.BasicStatLookup({
            StatTypes.VIT: 10,
            StatTypes.SPEED: 4,
            StatTypes.ATT: 0,
            StatTypes.UNARMED_ATT: 4,
            StatTypes.DEF: 2,
            StatTypes.INTELLIGENCE: 2
        })


class FrogTemplate(EnemyTemplate):

    def __init__(self):
        EnemyTemplate.__init__(self, "Cave Beast", spriteref.enormous_shadow)
        print("my_sprites={}".format(self.get_sprites()))

    def get_sprites(self):
        return spriteref.Bosses.frog_idle_1

    def get_level_range(self):
        return range(14, 16)

    def get_base_stats(self):
        return stats.BasicStatLookup({
            StatTypes.VIT: 30,
            StatTypes.SPEED: 3,
            StatTypes.ATT: 2,
            StatTypes.UNARMED_ATT: 4,
            StatTypes.DEF: 8,
            StatTypes.INTELLIGENCE: 5
        })


TEMPLATE_TRILLA = TrillaTemplate()
TEMPLATE_TRILLITE = TrilliteTemplate()
TEMPLATE_FLAPPUM = FlappumTemplate()
TEMPLATE_MUNCHER = MuncherTemplate(alt=False)
TEMPLATE_MUNCHER_ALT = MuncherTemplate(alt=True)
TEMPLATE_MUNCHER_SMALL = SmallMuncherTemplate(alt=False)
TEMPLATE_MUNCHER_SMALL_ALT = SmallMuncherTemplate(alt=True)
TEMPLATE_CYCLOI = CycloiTemplate()
TEMPLATE_DICEL = DicelTemplate()
TEMPLATE_THE_FALLEN = FallenTemplate()
TEMPLATE_FUNGOI = FungoiTemplate()
TEMPLATE_FROG = FrogTemplate()
TEMPLATE_SCORPION = ScorpionTemplate()
TEMPLATE_SMALL_FROG = SmallFrogTemplate()

RAND_SPAWN_TEMPLATES = [TEMPLATE_MUNCHER_SMALL,
                        TEMPLATE_MUNCHER,
                        TEMPLATE_DICEL,
                        TEMPLATE_THE_FALLEN,
                        TEMPLATE_CYCLOI,
                        TEMPLATE_FLAPPUM,
                        TEMPLATE_TRILLA,
                        TEMPLATE_TRILLITE,
                        TEMPLATE_FROG,
                        TEMPLATE_SMALL_FROG,
                        TEMPLATE_FUNGOI,
                        TEMPLATE_SCORPION]


def get_rand_template_for_level(level, rand_val):
    choices = []
    for template in RAND_SPAWN_TEMPLATES:
        lvl_range = template.get_level_range()
        if level in lvl_range:
            choices.append(template)

    if len(choices) == 0:
        print("WARN: no enemy templates for level: {}".format(level))
        return TEMPLATE_FLAPPUM
    else:
        return choices[int(rand_val * len(choices))]


class EnemyFactory:

    @staticmethod
    def get_state(template, level):
        inv = inventory.FakeInventoryState()

        item_type_choices = item.ItemTypes.all_types(level)
        if len(item_type_choices) > 0:
            item_type = random.choice(item_type_choices)
            loot_item = itemgen.ItemFactory.gen_item(level, item_type)
            inv.add_to_inv(loot_item)

        import src.game.gameengine as gameengine
        a_state = gameengine.ActorState(template.get_name(), level, template.get_base_stats(), inv, 1)
        a_state.set_energy(0 if random.random() < 0.5 else 4)

        return a_state

    @staticmethod
    def gen_enemy(template, level):
        return EnemyFactory.gen_enemies(template, level, n=1)[0]

    @staticmethod
    def gen_enemies(template, level, n=1):
        template = template if template is not None else get_rand_template_for_level(level, random.random())

        res = []
        for _ in range(0, n):
            res.append(Enemy(0, 0, EnemyFactory.get_state(template, level), template.get_sprites()))
        return res



