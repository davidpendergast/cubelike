from src.game import spriteref as spriteref
import src.items.item as item
import src.world.entities as entities
from src.renderengine.img import ImageBundle
from src.ui.ui import TextImage, ItemImage, TextBuilder
from src.game.stats import StatType
import src.game.enemies as enemies
import src.utils.colors as colors


class TooltipFactory:

    @staticmethod
    def build_item_tooltip(target_item, xy=(0, 0), layer=spriteref.UI_TOOLTIP_LAYER):
        text_builder = TextBuilder()
        text_builder.add(str(target_item.get_title()), color=target_item.get_title_color())

        plus_att = target_item.stat_value(StatType.LOCAL_ATT)
        if plus_att != 0:
            op = " (+" if plus_att > 0 else "-"
            text_builder.add_line(op + str(plus_att) + ")", color=item.STAT_COLORS[StatType.LOCAL_ATT])
        else:
            text_builder.add_line("")

        all_tags = [t for t in target_item.get_type().get_tags()]
        if item.ItemTags.WEAPON in all_tags and item.ItemTags.EQUIPMENT in all_tags:
            # no reason to display "weapon" AND "equipment"~
            all_tags.remove(item.ItemTags.EQUIPMENT)
        if len(all_tags) > 0:
            tag_str = ", ".join([str(t) for t in all_tags])
            text_builder.add_line(tag_str, color=colors.LIGHT_GRAY)

        all_stats = [x for x in target_item.all_stats()]
        added_newline = False
        for stat in all_stats:
            if not stat.is_hidden():
                if not added_newline:
                    text_builder.add_line("")
                    added_newline = True
                text_builder.add_line(str(stat), color=stat.color())

        return TextOnlyTooltip(text_builder.text(), custom_colors=text_builder.custom_colors(),
                               target=target_item, xy=xy, layer=layer)

    @staticmethod
    def build_enemy_tooltip(target_enemy, xy=(0, 0), layer=spriteref.UI_TOOLTIP_LAYER):
        text_builder = TextBuilder()
        e_state = target_enemy.get_actor_state()

        text_builder.add(e_state.name())
        text_builder.add_line(" (Hostile)", color=colors.RED)
        text_builder.add_line("Enemy", color=colors.LIGHT_GRAY)

        text_builder.add_line("")
        att_val = e_state.stat_value(StatType.ATT) + e_state.stat_value(StatType.UNARMED_ATT)
        text_builder.add_line("Attack: {}".format(att_val), color=colors.RED)
        text_builder.add_line("Defense: {}".format(e_state.stat_value(StatType.DEF)), color=colors.BLUE)
        # text_builder.add_line("Max Health: {}".format(e_state.stat_value(StatType.VIT)), color=colors.GREEN)
        text_builder.add_line("Speed: {}".format(e_state.stat_value(StatType.SPEED)), color=colors.YELLOW)
        text_builder.add_line("Health: {}/{}".format(e_state.hp(), e_state.max_hp()), color=colors.GREEN)
        # text_builder.add_line("Energy: {}/{}".format(e_state.energy(), e_state.max_energy()), colors.YELLOW)

        return TextOnlyTooltip(text_builder.text(), custom_colors=text_builder.custom_colors(),
                               target=target_enemy, xy=xy, layer=layer)

    @staticmethod
    def build_chest_tooltip(target_chest, xy=(0, 0), layer=spriteref.UI_TOOLTIP_LAYER):
        pass

    @staticmethod
    def build_npc_tooltip(target_npc, xy=(0, 0), layer=spriteref.UI_TOOLTIP_LAYER):
        pass

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


class TitleImageAndStatsTooltip(Tooltip):

    def __init__(self, title, level, stat_list, title_color=(1, 1, 1), xy=(0, 0), layer=spriteref.UI_TOOLTIP_LAYER):
        Tooltip.__init__(self, xy=xy, layer=layer)
        self.title = title
        self.title_color = title_color
        self.level = level
        self.core_stats = [s for s in stat_list if s.stat_type in item.CORE_STATS]
        self.non_core_stats = [s for s in stat_list if s.stat_type not in item.CORE_STATS]

        self.top_panel = None
        self.mid_panels = []
        self.bot_panel = None
        self.title_text = None
        self.core_texts = []
        self.non_core_texts = []

        self.size = (0, 0)

        self._build_images()

    def get_rect(self):
        r = Tooltip.get_rect(self)
        return [r[0], r[1], self.size[0], self.size[1]]

    def _build_images(self):
        sc = 2
        text_sc = 1
        self.top_panel = ImageBundle(spriteref.UI.item_panel_top, self.xy[0], self.xy[1], layer=self.layer, scale=sc)
        h = self.top_panel.height()
        for i in range(0, len(self.non_core_stats)):
            img = ImageBundle(spriteref.UI.item_panel_middle, self.xy[0], self.xy[1] + h, layer=self.layer, scale=sc)
            h += img.height()
            self.mid_panels.append(img)

        if len(self.mid_panels) > 0:
            bot_sprite = spriteref.UI.item_panel_bottom_0
        else:
            bot_sprite = spriteref.UI.item_panel_bottom_1
            h -= bot_sprite.height() * sc  # covers up part of the top
        self.bot_panel = ImageBundle(bot_sprite, self.xy[0], self.xy[1] + h, layer=self.layer, scale=sc)

        self.size = (self.top_panel.width(), h + self.bot_panel.height())

        self.title_text = TextImage(self.xy[0] + 8 * sc, self.xy[1] + 6 * sc, self.title, self.layer, scale=text_sc,
                                    color=self.title_color)

        line_spacing = int(1.5 * sc)

        h = 16 * sc + line_spacing

        if self.level is not None:
            lvl_str = "LVL:{}".format(self.level)
            lvl_txt = TextImage(self.xy[0] + 56 * sc, self.xy[1] + h, lvl_str, self.layer, scale=text_sc)
            self.core_texts.append(lvl_txt)
            h += lvl_txt.line_height()

        for stat in self.core_stats:
            h += line_spacing
            stat_txt = TextImage(self.xy[0] + 56 * sc, self.xy[1] + h, str(stat), self.layer, color=stat.color(),
                                 scale=text_sc)
            self.core_texts.append(stat_txt)
            h += stat_txt.line_height()

        h = 64 * sc
        for stat in self.non_core_stats:
            h += line_spacing
            stat_txt = TextImage(self.xy[0] + 8 * sc, self.xy[1] + h, str(stat), self.layer, color=stat.color(),
                                 scale=text_sc)
            self.non_core_texts.append(stat_txt)
            h += stat_txt.line_height()

    def all_bundles(self):
        yield self.top_panel
        for bun in self.mid_panels:
            yield bun
        yield self.bot_panel
        for bun in self.title_text.all_bundles():
            yield bun

        for text in self.core_texts:
            for bun in text.all_bundles():
                yield bun

        for text in self.non_core_texts:
            for bun in text.all_bundles():
                yield bun


class ItemInfoTooltip(TitleImageAndStatsTooltip):

    def __init__(self, item, xy=(0, 0), layer=spriteref.UI_TOOLTIP_LAYER):
        self.item = item
        TitleImageAndStatsTooltip.__init__(self, item.name, 1, item.all_stats(),
                                           title_color=item.get_title_color(), xy=xy, layer=layer)

    def get_target(self):
        return self.item


class EnemyInfoTooltip(TitleImageAndStatsTooltip):

    def __init__(self, enemy_state, xy=(0, 0), layer=spriteref.UI_TOOLTIP_LAYER):
        self.e_state = enemy_state
        stat_map = enemy_state.get_base_stats()
        stats = []
        for stat_type in stat_map:
            if not isinstance(stat_type, StatType):
                continue
            base_val = enemies.TRUE_BASE_STATS[stat_type] if stat_type in enemies.TRUE_BASE_STATS else 0
            stat_val = stat_map[stat_type] - base_val

            if stat_val != 0:
                stats.append(item.ItemStat(stat_type, stat_val))

        TitleImageAndStatsTooltip.__init__(self, enemy_state.name(), enemy_state.level(), stats, xy=xy, layer=layer)

    def get_target(self):
        return self.e_state

    def get_special_image_bundles(self, rect, sc):
        bun = ImageBundle.new_bundle(self.layer, scale=sc)
        sprite = self.e_state.template.get_sprites()[0]
        color = self.e_state.base_color()
        x = rect[0] + rect[2] // 2 - sc * sprite.width() // 2
        y = rect[1] + rect[3] // 2 - sc * sprite.height() // 2
        return [bun.update(new_x=x, new_y=y, new_color=color, new_model=sprite)]


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

        width = 0

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


