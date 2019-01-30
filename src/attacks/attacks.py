import random

import src.world.entities as entities
import src.game.globalstate as gs
from src.utils.util import Utils
from src.game.stats import StatType


class AttackState:

    def __init__(self):
        self.attack_tick = 0

        self.attack_dur = 1
        self.delay_dur = 1

        self.current_attack = None
        self._next_att = None

        self._delayed_attacks_this_tick = []  # list of tuples (position, target_entity, attack)

    def set_attack(self, attack):
        if self.is_attacking():
            self._next_att = attack
        else:
            self.current_attack = attack

    def get_next_or_current_attack(self):
        if self._next_att is not None:
            return self._next_att
        else:
            return self.current_attack

    def can_attack(self):
        return not self.is_active() and self.current_attack is not None

    def start_attack(self, stat_lookup):
        if not self.can_attack():
            return False
        else:
            self.attack_tick = 1

            self.attack_dur = self.get_attack_dur(stat_lookup)

            self.delay_dur = self.get_delay_dur(stat_lookup)

    def get_attack_dur(self, stat_lookup):
        att_speed = 1.0 / self.current_attack.base_duration
        att_speed *= (1 + 0.01 * stat_lookup.stat_value(StatType.ATTACK_SPEED))
        return max(1, round(1.0 / att_speed))

    def get_delay_dur(self, stat_lookup):
        del_speed = 1.0 / self.current_attack.base_delay
        del_speed *= (1 + 0.01 * stat_lookup.stat_value(StatType.ATTACK_SPEED))
        return max(1, round(1.0 / del_speed))

    def get_attack_range(self, stat_lookup):
        return self.current_attack.get_base_range() * (1 + 0.01 * stat_lookup.stat_value(StatType.ATTACK_RADIUS))

    def update(self, entity, world):
        stat_lookup = entity.get_actorstate()

        num_hit = 0
        dmg_dealt = 0

        if len(self._delayed_attacks_this_tick) > 0:
            for del_att in self._delayed_attacks_this_tick:
                pos, t_entity, attack = del_att
                t_state = t_entity.get_actorstate()

                successful, dmg = self._resolve_attack(attack, stat_lookup, pos, t_state, t_entity)
                if successful:
                    num_hit += 1
                    dmg_dealt += dmg
                    attack.on_hit(t_entity, dmg_dealt, entity, world)

            self._delayed_attacks_this_tick.clear()

        if self.is_active():
            if self.attack_tick == self.attack_dur:
                targets = self.current_attack.activate(entity, world, stat_lookup)

                for target in targets:
                    t_ent = target
                    t_state = t_ent.get_actorstate()

                    successful, dmg = self._resolve_attack(self.current_attack, stat_lookup,
                                                           entity.center(), t_state, t_ent)

                    if successful:
                        num_hit += 1
                        dmg_dealt += dmg

                        self.current_attack.on_hit(t_ent, dmg_dealt, entity, world)

            elif self.attack_tick >= self.attack_dur + self.delay_dur:
                self._finish_attack()

            if self.is_active():
                self.attack_tick += 1

        if num_hit > 0:
            healing = stat_lookup.stat_value(StatType.LIFE_ON_HIT) * num_hit
            healing += stat_lookup.stat_value(StatType.LIFE_LEECH) * 0.01 * dmg_dealt
            if healing >= 0:
                stat_lookup.do_heal(healing)
            else:
                # negative healing stats damage you
                stat_lookup.deal_damage(-healing)

    def _resolve_attack(self, attack, stat_lookup, source_pos, t_state, t_ent):
        """
            returns (bool: hit, dmg_dealt)
        """
        att_defense = stat_lookup.stat_value(StatType.DEF) + stat_lookup.stat_value(StatType.ACCURACY)
        defend_defense = t_state.stat_value(StatType.DEF) + t_state.stat_value(StatType.DODGE)

        chance_to_hit = Utils.bound(2 * att_defense / (att_defense + defend_defense), 0.10, 1.0)

        if random.random() <= chance_to_hit:
            dmg = self.get_dmg(stat_lookup, attack=attack)
            spread = 0.25
            dmg_actual = dmg * (1 + spread * 2 * (0.5 - random.random()))
            sub = Utils.sub(t_ent.center(), source_pos)
            kb = Utils.set_length(sub, self.current_attack.knockback)
            dmg_color = self.current_attack.dmg_color
            t_state.deal_damage(dmg_actual, knockback=kb, color=dmg_color)
            return (True, dmg_actual)
        else:
            t_state.was_missed()
            return (False, 0)

    def delayed_attack_landed(self, pos, target_entity, attack):
        self._delayed_attacks_this_tick.append((pos, target_entity, attack))

    def get_dps(self, stat_lookup):
        if self.current_attack is None:
            return 0.0

        total_dur = self.get_delay_dur(stat_lookup) + self.get_attack_dur(stat_lookup)
        total_dmg = self.get_dmg(stat_lookup)

        return total_dmg / (total_dur / 60.0)

    def get_dmg(self, stat_lookup, attack=None):
        att = self.current_attack if attack is None else attack
        dmg = stat_lookup.stat_value(StatType.ATT)
        dmg *= (1 + 0.01 * stat_lookup.stat_value(StatType.ATTACK_DAMAGE))
        return dmg * att.base_damage

    def is_active(self):
        return self.attack_tick > 0

    def is_attacking(self):
        return 0 < self.attack_tick <= self.attack_dur

    def is_delaying(self):
        return self.attack_tick - self.attack_dur > 0

    def total_progress(self):
        return Utils.bound(self.attack_tick / (self.attack_dur + self.delay_dur), 0.0, 0.999)

    def attack_progress(self):
        return Utils.bound(self.attack_tick / self.attack_dur, 0.0, 0.999)

    def delay_progress(self):
        return Utils.bound((self.attack_tick - self.attack_dur) / self.delay_dur, 0.0, 0.999)

    def _finish_attack(self):
        self.attack_tick = 0
        if self._next_att is not None:
            self.current_attack = self._next_att
            self._next_att = None


class Attack:
    def __init__(self, name):
        self.name = name
        self.base_duration = 15
        self.base_delay = 12
        self.base_radius = 64
        self.base_damage = 1.0
        self.knockback = 1
        self.dmg_color = (1, 0, 0)
        self.is_droppable = False  # TODO - delete this
        self.is_jumpy = True

    def place_attack_circle(self, pos, stat_lookup, world, color=None):
        radius = self.base_radius * (1 + 0.01 * stat_lookup.stat_value(StatType.ATTACK_RADIUS))
        if color is None:
            color = self.dmg_color
        circle = entities.AttackCircleArt(*pos, radius, 60, color=color, color_end=(0, 0, 0))
        world.add(circle)

    def get_base_range(self):
        return self.base_radius

    def activate(self, entity, world, stat_lookup):
        """
            returns: list of Entities hit by attack.
        """
        att_range = self.base_radius
        att_range *= (1 + 0.01 * stat_lookup.stat_value(StatType.ATTACK_RADIUS))

        e_center = entity.center()
        hit_entities = world.entities_in_circle(e_center, att_range + 150, cond=lambda t: entity.can_damage(t))

        res = []

        for target in hit_entities:
            if target.is_enemy() and Utils.dist(e_center, target.center()) <= att_range + target.hurtbox():
                res.append(target)
            elif Utils.dist(e_center, target.center()) <= att_range:
                res.append(target)

        return res

    def on_hit(self, t_entity, dmg, s_entity, world):
        pass


class GroundPoundAttack(Attack):
    def __init__(self):
        Attack.__init__(self, "Satan's Circle")
        self.base_duration = 35
        self.base_delay = 12
        self.base_radius = 54
        self.base_damage = 0.65
        self.dmg_color = (1, 0, 0)
        self.knockback = 0.25
        self.is_droppable = False

    def activate(self, entity, world, stat_lookup):
        res = Attack.activate(self, entity, world, stat_lookup)
        self.place_attack_circle(entity.center(), stat_lookup, world, color=(0.25, 0.25, 0.25))

        return res


class FrogAttack(Attack):
    """This attack is only used by the Frog Boss"""
    def __init__(self):
        Attack.__init__(self, "Crushing Leap")
        self.base_duration = 1
        self.base_delay = 1
        self.base_radius = 75
        self.base_damage = 2.00
        self.dmg_color = (1, 0, 0)
        self.knockback = 0.65
        self.is_droppable = False
        self.is_jumpy = False

    def activate(self, entity, world, stat_lookup):
        res = Attack.activate(self, entity, world, stat_lookup)
        self.place_attack_circle(entity.center(), stat_lookup, world, color=(0, 0, 0))

        return res


class TouchAttack(Attack):
    def __init__(self):
        Attack.__init__(self, "Evil Touch")
        self.base_duration = 15
        self.base_delay = 12
        self.base_radius = 42
        self.base_damage = 1.0
        self.knockback = 2
        self.is_droppable = False
        self.is_jumpy = False


class SpawnMinionAttack(Attack):
    def __init__(self):
        Attack.__init__(self, "Minion Launcher")
        self.base_duration = 35
        self.base_delay = 12
        self.base_radius = 64
        self.base_damage = 0.6
        self.knockback = 0.25
        self.projectile_range = 300
        self.dmg_color = (1, 0, 1)
        self.is_droppable = True

    def activate(self, entity, world, stat_lookup):
        res = Attack.activate(self, entity, world, stat_lookup)
        self.place_attack_circle(entity.center(), stat_lookup, world)

        pos = entity.center()
        cond = lambda e: entity.can_damage(e) and not world.get_hidden_at(*e.center()) and e not in res
        targets_in_range = world.entities_in_circle(pos, self.projectile_range, cond=cond)

        if len(targets_in_range) > 0:
            src_state = entity.get_actorstate()
            target_e = targets_in_range[0]

            proj = entities.MinionProjectile(pos[0], pos[1], entity, target_e, 150, (1, 0, 1), src_state, self)
            world.add(proj)

        return res


class StatusEffect:
    POISON = 0

    def __init__(self, name, s_type):
        self._name = name
        self._type = s_type

    def get_name(self):
        return self._name

    def get_type(self):
        return self._type

    def update(self, entity, world):
        pass


class PoisonStatus(StatusEffect):

    def __init__(self, dmg_per_pulse, n_pulses, pulse_delay, color=(0, 1, 0), src_state=None):
        StatusEffect.__init__(self, "Plague Breath", StatusEffect.POISON)
        self.dmg_per_pulse = dmg_per_pulse
        self.n_pulses = n_pulses
        self.pulse_delay = pulse_delay
        self.color = color

        self.src_state = src_state

        self.ticks_active = 0

    def update(self, entity, world):
        self.ticks_active += 1

        if self.ticks_active > (self.n_pulses + 1) * self.pulse_delay - 1:
            e_state = entity.get_actorstate()
            e_state.remove_status(self)

        elif gs.get_instance().tick_counter % self.pulse_delay == 0:
            e_state = entity.get_actorstate()
            e_state.deal_damage(self.dmg_per_pulse, ignore_invuln=True, color=self.color)

            if self.src_state is not None:
                leech_pct = self.src_state.stat_value(StatType.LIFE_LEECH) / 100.0
                self.src_state.do_heal(leech_pct * self.dmg_per_pulse)


class PoisonAttack(Attack):

    def __init__(self):
        Attack.__init__(self, "Plague")
        self.base_duration = 35
        self.base_delay = 12
        self.base_radius = 72
        self.base_range = 72
        self.base_damage = 0.75
        self.knockback = 0.15
        self.dmg_color = (0, 1, 0)
        self.is_droppable = True

        self.num_pulses = 7
        self.base_pulse_delay = 60

    def activate(self, entity, world, stat_lookup):
        res = Attack.activate(self, entity, world, stat_lookup)
        self.place_attack_circle(entity.center(), stat_lookup, world)

        return res

    def on_hit(self, t_entity, dmg, s_entity, world):
        s_state = s_entity.get_actorstate()
        att_spd = 1 + 0.01 * s_state.stat_value(StatType.ATTACK_SPEED)
        pulse_delay = max(1, round(self.base_pulse_delay / att_spd))
        dmg = max(1, dmg)
        n_pulses = self.num_pulses if dmg >= self.num_pulses else int(dmg)
        per_pulse = round(dmg / n_pulses)

        poison_effect = PoisonStatus(per_pulse, n_pulses, pulse_delay,
                                     color=self.dmg_color, src_state=s_entity.get_actorstate())

        t_entity.get_actorstate().add_status(poison_effect)


class TeleportAttack(Attack):

    def __init__(self):
        Attack.__init__(self, "Teleport")
        self.base_duration = 35
        self.base_delay = 12
        self.base_radius = 56
        self.base_damage = 0.7
        self.knockback = 0.25
        self.dmg_color = (0.5, 0.5, 1)
        self.is_droppable = True

    def get_base_range(self):
        return self.base_radius * 3

    def activate(self, entity, world, stat_lookup):
        res = Attack.activate(self, entity, world, stat_lookup)

        if len(res) == 0 and entity.get_vel() != (0, 0):
            length = self.get_base_range() * (1 + 0.01 * stat_lookup.stat_value(StatType.ATTACK_RADIUS))
            move_xy = Utils.set_length(entity.get_vel(), length)
            move_xy = (round(move_xy[0]), round(move_xy[1]))

            # definitely don't want player or entities porting through closed doors
            if world.get_hidden_at(*move_xy) is not True:
                entity.move(*move_xy, world, and_search=True)
                res = Attack.activate(self, entity, world, stat_lookup)

        self.place_attack_circle(entity.center(), stat_lookup, world)
        return res

    def on_hit(self, t_entity, dmg, s_entity, world):
        pass


GROUND_POUND = GroundPoundAttack()
MINION_LAUNCH_ATTACK = SpawnMinionAttack()
TOUCH_ATTACK = TouchAttack()
POISON_ATTACK = PoisonAttack()
TELEPORT_ATTACK = TeleportAttack()


FROG_ATTACK = FrogAttack()  # special frog boss attack

ALL_SPECIAL_ATTACKS = [MINION_LAUNCH_ATTACK, POISON_ATTACK, TELEPORT_ATTACK]


