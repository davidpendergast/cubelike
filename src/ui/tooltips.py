from src.game import spriteref as spriteref
import src.items.item as item
import src.world.entities as entities
from src.renderengine.img import ImageBundle
from src.ui.ui import TextImage, ItemImage, TextBuilder
from src.game.stats import StatTypes
import src.game.enemies as enemies
import src.game.gameengine as gameengine
import src.utils.colors as colors
import src.game.globalstate as gs
import src.game.statuseffects as statuseffects
from src.utils.util import Utils


class TooltipFactory:

    @staticmethod
    def build_item_tooltip(target_item, xy=(0, 0), layer=spriteref.UI_TOOLTIP_LAYER):
        text_builder = TextBuilder()

        plus_att = target_item.stat_value(StatTypes.ATT, local=True)
        if plus_att != 0:
            op = "(+" if plus_att > 0 else "-"
            text_builder.add(op + str(plus_att) + ") ", color=StatTypes.ATT.get_color())

        text_builder.add_line(str(target_item.get_title()), color=target_item.get_title_color())

        all_tags = [t for t in target_item.get_type().get_tags() if not t.startswith("_")]
        if item.ItemTags.WEAPON in all_tags and item.ItemTags.EQUIPMENT in all_tags:
            all_tags.remove(item.ItemTags.EQUIPMENT)

        if len(all_tags) > 0:
            tag_str = ", ".join([str(t) for t in all_tags])
            text_builder.add_line(tag_str, color=colors.LIGHT_GRAY)

        if item.ItemTags.WEAPON in all_tags:
            # this relies on weapons only having one attack, which is ~currently~ true
            for act in target_item.all_actions():
                if act.get_type() == gameengine.ActionType.ATTACK:
                    dists = act.get_target_dists()
                    dists_str = ", ".join([str(d) for d in dists])
                    text_builder.add_line("Range: {}".format(dists_str), color=colors.LIGHT_GRAY)
                    break

        added_newline = False
        all_stats = [x for x in target_item.all_applied_stats()]
        for stat in all_stats:
            if not stat.is_hidden():
                if not added_newline:
                    text_builder.add_line("")
                    added_newline = True
                text_builder.add_line(str(stat), color=stat.color())

        w, p = gs.get_instance().get_world_and_player()

        if target_item.can_consume():
            consume_effect = target_item.get_consume_effect()
            text_builder.add_line("")
            if consume_effect is not None:
                text_builder.add("Gives ")
                text_builder.add(consume_effect.get_name(), color=consume_effect.get_color())
                text_builder.add_line(" when consumed ({} turns).".format(consume_effect.get_duration()))

        if p is not None:
            right_click_action = gameengine.get_right_click_action_for_item(target_item)
            if right_click_action is not None and right_click_action.is_possible(w):
                text_builder.add_line("")

                if isinstance(right_click_action, gameengine.ConsumeItemAction):
                    text_builder.add_line("(Right-Click to Consume)", color=colors.LIGHT_GRAY)
                elif isinstance(right_click_action, gameengine.AddItemToGridAction):
                    if right_click_action.get_grid() == p.get_actor_state().inventory().get_equip_grid():
                        text_builder.add_line("(Right-Click to Equip)", color=colors.LIGHT_GRAY)
                    else:
                        text_builder.add_line("(Right-Click to Store)", color=colors.LIGHT_GRAY)
                else:
                    text_builder.add_line("(Right-Click to Use)", color=colors.LIGHT_GRAY)

        return TextOnlyTooltip(text_builder.text(), custom_colors=text_builder.custom_colors(),
                               target=target_item, xy=xy, layer=layer)

    @staticmethod
    def build_enemy_tooltip(target_enemy, xy=(0, 0), layer=spriteref.UI_TOOLTIP_LAYER):
        text_builder = TextBuilder()
        e_state = target_enemy.get_actor_state()

        text_builder.add_line(e_state.name())

        attributes = [("Hostile", colors.LIGHT_GRAY)]
        for st in e_state.all_nonzero_stat_types():
            attrib_name = st.get_enemy_desc(e_state)
            if attrib_name is not None:
                attributes.append((attrib_name, st.get_color()))

        for i in range(0, len(attributes)):
            name = attributes[i][0]
            color = attributes[i][1]
            text_builder.add(name, color=color)
            if i < len(attributes) - 1:
                text_builder.add(", ", color=color)

        text_builder.add_line("")
        att_val = e_state.stat_value(StatTypes.ATT) + e_state.stat_value(StatTypes.UNARMED_ATT)
        text_builder.add_line("Attack: {}".format(att_val), color=StatTypes.ATT.get_color())
        text_builder.add_line("Defense: {}".format(e_state.stat_value(StatTypes.DEF)), color=StatTypes.DEF.get_color())
        text_builder.add_line("Speed: {}".format(e_state.stat_value(StatTypes.SPEED)), color=StatTypes.SPEED.get_color())
        text_builder.add_line("Health: {}/{}".format(e_state.hp(), e_state.max_hp()), color=StatTypes.VIT.get_color())

        # debug stuff
        # text_builder.add_line("Energy: {}/{}".format(e_state.energy(), e_state.max_energy()), color=colors.LIGHT_GRAY)
        # if e_state.ready_to_act():
        #    text_builder.add_line("Ready to Act", color=colors.LIGHT_GRAY)

        return TextOnlyTooltip(text_builder.text(), custom_colors=text_builder.custom_colors(),
                               target=target_enemy, xy=xy, layer=layer)

    @staticmethod
    def build_chest_tooltip(target_chest, xy=(0, 0), layer=spriteref.UI_TOOLTIP_LAYER):
        text_builder = TextBuilder()
        text_builder.add("Chest")
        if target_chest.is_open():
            text_builder.add_line(" (Empty)", color=colors.LIGHT_GRAY)

        return TextOnlyTooltip(text_builder.text(), custom_colors=text_builder.custom_colors(),
                               target=target_chest, xy=xy, layer=layer)

    @staticmethod
    def build_npc_tooltip(target_npc, xy=(0, 0), layer=spriteref.UI_TOOLTIP_LAYER):
        text_builder = TextBuilder()

        text_builder.add_line(target_npc.get_npc_template().name)
        text_builder.add_line("Friendly", color=colors.LIGHT_GRAY)

        return TextOnlyTooltip(text_builder.text(), custom_colors=text_builder.custom_colors(),
                               target=target_npc, xy=xy, layer=layer)

    @staticmethod
    def build_action_provider_tooltip(action_prov, xy=(0, 0), layer=spriteref.UI_TOOLTIP_LAYER):
        text_builder = TextBuilder()
        text_builder.add_line(action_prov.get_name())

        if action_prov.get_type() == gameengine.ActionType.ATTACK:
            ps = gs.get_instance().player_state()
            att_value = ps.stat_value_with_item(StatTypes.ATT, action_prov.get_item())
            text_builder.add_line("Attack: {}".format(att_value), color=StatTypes.ATT.get_color())

            dists = action_prov.get_target_dists()
            dists_str = ", ".join([str(d) for d in dists])
            text_builder.add_line("Range: {}".format(dists_str), color=colors.LIGHT_GRAY)

        if action_prov.get_item() is not None:
            added_newline = False
            for item_stat in action_prov.get_item().all_applied_stats():
                if not item_stat.is_hidden() and item_stat.is_local():
                    if not added_newline:
                        text_builder.add_line("")
                        added_newline = True
                    text_builder.add_line(str(item_stat), color=item_stat.color())

        for i in range(0, 6):
            if gs.get_instance().get_mapped_action(i) == action_prov:
                keys = gs.get_instance().settings().action_key(i)
                if len(keys) == 0:
                    key_str = "None"
                else:
                    key_str = Utils.stringify_key(keys[0])
                text_builder.add_line("")
                text_builder.add_line("([{}] to Activate)".format(key_str), color=colors.LIGHT_GRAY)

        return TextOnlyTooltip(text_builder.text(), custom_colors=text_builder.custom_colors(),
                               target=action_prov, xy=xy, layer=layer)

    @staticmethod
    def build_status_effect_tooltip(effect, turns_remaining, xy=(0, 0), layer=spriteref.UI_TOOLTIP_LAYER):
        text_builder = TextBuilder()
        text_builder.add_line(effect.get_name())

        # TODO - we're assuming this effect is on the player, which may (in the future) not always be the case.
        for applied_stat in effect.all_applied_stats():
            if not applied_stat.is_hidden():
                text_builder.add_line(str(applied_stat), color=applied_stat.color())

        text_builder.add_line("")
        text_builder.add_line("({} turns remaining)".format(turns_remaining), color=colors.LIGHT_GRAY)

        return TextOnlyTooltip(text_builder.text(), custom_colors=text_builder.custom_colors(),
                               target=(effect, turns_remaining), xy=xy, layer=layer)

    @staticmethod
    def build_tooltip(obj, xy=(0, 0), layer=spriteref.UI_TOOLTIP_LAYER):
        if isinstance(obj, entities.ItemEntity):
            obj = obj.get_item()

        if isinstance(obj, item.Item):
            return TooltipFactory.build_item_tooltip(obj, xy=xy, layer=layer)
        elif isinstance(obj, entities.Enemy):
            return TooltipFactory.build_enemy_tooltip(obj, xy=xy, layer=layer)
        elif isinstance(obj, entities.NpcEntity):
            return TooltipFactory.build_npc_tooltip(obj, xy=xy, layer=layer)
        elif isinstance(obj, entities.ChestEntity):
            return TooltipFactory.build_chest_tooltip(obj, xy=xy, layer=layer)
        elif isinstance(obj, gameengine.ActionProvider):
            return TooltipFactory.build_action_provider_tooltip(obj, xy=xy, layer=layer)
        elif isinstance(obj, tuple) and len(obj) == 2 and isinstance(obj[0], statuseffects.StatusEffect):
            return TooltipFactory.build_status_effect_tooltip(obj[0], obj[1], xy=xy, layer=layer)
        elif isinstance(obj, TextBuilder):
            return TextOnlyTooltip(obj.text(), custom_colors=obj.custom_colors(), target=obj, xy=xy, layer=layer)
        else:
            return None


class Tooltip:

    def __init__(self, xy=(0, 0), target=None, layer=spriteref.UI_TOOLTIP_LAYER):
        self.layer = layer
        self.xy = xy
        self.target = target

    def all_bundles(self):
        return []

    def get_target(self):
        """
            returns: object that this tooltip is 'for'
        """
        return self.target

    def get_rect(self):
        return [self.xy[0], self.xy[1], 0, 0]


class TextOnlyTooltip(Tooltip):

    TEXT_SCALE = 1

    def __init__(self, text, target=None, xy=(0, 0), custom_colors={}, layer=spriteref.UI_TOOLTIP_LAYER):
        Tooltip.__init__(self, xy=xy, target=target, layer=layer)
        self.bg_sprite = spriteref.UI.tooltip_bg

        self.text = text
        self.custom_colors = custom_colors

        self._rect = [xy[0], xy[1], 0, 0]

        self._text_image = None
        self._bg_image = None

        self._build_images()

    def get_rect(self):
        return self._rect

    def _build_images(self):
        x = self.xy[0]
        y = self.xy[1]

        self._text_image = TextImage(x, y, self.text, self.layer,
                                     custom_colors=self.custom_colors,
                                     scale=TextOnlyTooltip.TEXT_SCALE)

        self._rect = [self.xy[0], self.xy[1],
                      self._text_image.size()[0],
                      self._text_image.size()[1]]

        if self._rect[2] > 0 and self._rect[3] > 0:
            ratio = (int(0.5 + self._rect[2] / self.bg_sprite.width()),
                     int(0.5 + self._rect[3] / self.bg_sprite.height()))

            self._bg_image = ImageBundle(self.bg_sprite, self.xy[0], self.xy[1], layer=self.layer,
                                         scale=1, ratio=ratio)

    def all_bundles(self):
        if self._bg_image is not None:
            yield self._bg_image
        if self._text_image is not None:
            for bun in self._text_image.all_bundles():
                yield bun


