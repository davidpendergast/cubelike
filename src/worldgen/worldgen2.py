import re
import random
import time

FLOOR = "."
WALL = "x" # "█"
DOOR = "0"

EMPTY = " "

MONSTER = "m"
PLAYER = "p"
ENTRANCE = "v"
EXIT = "e"
CHEST = "c"
NPC = "n"
STRAY_ITEM = "i"
SPECIAL = "s"


def color_char(c):
    if c == DOOR:
        return "\033[1;34m" + c + "\033[0;0m"  # blue
    elif c == MONSTER:
        return "\033[1;31m" + c + "\033[0;0m"  # red
    elif c == CHEST:
        return "\033[1;35m" + c + "\033[0;0m"  # magenta
    elif c == EXIT or c == PLAYER or c == ENTRANCE:
        return "\033[1;32m" + c + "\033[0;0m"  # green
    elif c == EMPTY or c == WALL or c == FLOOR:
        return c
    else:
        return "\033[1;33m" + c + "\033[0;0m"  # yellow


class Tileish:

    def get(self, x, y):
        return EMPTY

    def w(self):
        return 0

    def h(self):
        return 0

    def __str__(self):
        res = []
        for y in range(0, self.h()):
            for x in range(0, self.w()):
                val = self.get(x, y)
                res.append(str(color_char(val)) + " ")
            res.append("\n")
        return "".join(res)


class Tile(Tileish):

    def __init__(self, size, door_offs=3, door_len=2):
        self.grid = []
        for i in range(0, size):
            self.grid.append([EMPTY for _ in range(0, size)])

        self._door_offs = door_offs
        self._door_length = door_len

    def in_tile(self, x, y):
        return 0 <= x < self.w() and 0 <= y < self.h()

    def get(self, x, y):
        if self.in_tile(x, y):
            return self.grid[x][y]
        else:
            return EMPTY

    def set(self, x, y, val):
        self.grid[x][y] = val

    def replace(self, x, y, repl_val, val):
        if self.get(x, y) == repl_val:
            self.set(x, y, val)

    def fill(self, x1, y1, x2, y2, val):
        for x in range(x1, x2):
            for y in range(y1, y2):
                self.set(x, y, val)

    def w(self):
        return len(self.grid)

    def h(self):
        return len(self.grid[0])

    def coords(self):
        for x in range(0, self.w()):
            for y in range(0, self.h()):
                yield (x, y)

    def door_coords(self, door_num):
        if door_num == 0:
            return [(self._door_offs + i, 0) for i in range(0, self._door_length)]
        elif door_num == 1:
            return [(self.w() - self._door_length - self._door_offs + i, 0) for i in range(0, self._door_length)]
        elif door_num == 2:
            return [(self.w() - 1, self._door_offs + i) for i in range(0, self._door_length)]
        elif door_num == 3:
            return [(self.w() - 1, self.h() - self._door_length - self._door_offs + i) for i in range(0, self._door_length)]
        elif door_num == 4:
            return [(self.w() - self._door_length - self._door_offs + i, self.h() - 1) for i in range(0, self._door_length)]
        elif door_num == 5:
            return [(self._door_offs + i, self.h() - 1) for i in range(0, self._door_length)]
        elif door_num == 6:
            return [(0, self.h() - self._door_length - self._door_offs + i) for i in range(0, self._door_length)]
        elif door_num == 7:
            return [(0, self._door_offs + i) for i in range(0, self._door_length)]

    @staticmethod
    def doors_on_side(side):
        """side: (1, 0), (-1, 0), (0, 1), or (0, -1)"""
        if side == (0, -1):
            return [0, 1]
        elif side == (1, 0):
            return [2, 3]
        elif side == (0, 1):
            return [4, 5]
        elif side == (-1, 0):
            return [6, 7]

    @staticmethod
    def connecting_door(door_num):
        if door_num % 2 == 0:
            return (door_num + 5) % 8
        else:
            return (door_num + 3) % 8

    def hub_coords(self, door_num):
        hub_size = self._door_length
        if door_num == 0 or door_num == 7:
            min_xy = (self._door_offs, self._door_offs)
        elif door_num == 1 or door_num == 2:
            min_xy = (self.w()-self._door_offs-hub_size, self._door_offs)
        elif door_num == 3 or door_num == 4:
            min_xy = (self.w()-self._door_offs-hub_size, self.h()-self._door_offs-hub_size)
        elif door_num == 5 or door_num == 6:
            min_xy = (self._door_offs, self.h()-self._door_offs-hub_size)

        res = []
        for x in range(0, hub_size):
            for y in range(0, hub_size):
                res.append((min_xy[0] + x, min_xy[1] + y))
        return res

    def hub_connection_coords(self, num):
        h1 = self.hub_coords(num*2)
        h2 = self.hub_coords(num*2 + 1)

        enclosing_rect = RectUtils.rect_containing(h1 + h2)
        return [xy for xy in RectUtils.coords_in_rect(enclosing_rect) if (xy not in h1 and xy not in h2)]


class PartitionGrid:
    def __init__(self, grid_w, grid_h):
        self.partitions = [None] * grid_w
        for i in range(0, len(self.partitions)):
            self.partitions[i] = [None] * grid_h

    def w(self):
        return len(self.partitions)

    def h(self):
        return len(self.partitions[0])

    def get(self, x, y):
        if 0 <= x < self.w() and 0 <= y < self.h():
            return self.partitions[x][y]
        else:
            return None

    def set(self, x, y, p):
        self.partitions[x][y] = p

    def is_valid_at(self, x, y, p, direction=None):
        if not (0 <= x < self.w() and 0 <= y < self.h()):
            return False
        elif direction is not None:
            n = self.get(x + direction[0], y + direction[1])
            my_doors = Tile.doors_on_side(direction)
            n_doors = Tile.doors_on_side((-direction[0], -direction[1]))
            for i in range(0, len(my_doors)):
                if p.has_door(my_doors[i]) != n.has_door(n_doors[i]):
                    return False
            return True
        else:
            return (self.is_valid_at(x, y, p, direction=(0, -1)) and
                    self.is_valid_at(x, y, p, direction=(1, 0)) and
                    self.is_valid_at(x, y, p, direction=(0, 1)) and
                    self.is_valid_at(x, y, p, direction=(-1, 0)))

    def has_door(self, x, y, door_num):
        """returns: True, False or None if partition is None"""
        p = self.get(x, y)
        if p is None:
            return None
        else:
            return p.has_door(door_num)

    def needs_door(self, x, y, door_num, prevent_boundary_doors=True):
        """returns: True or False if neighboring tile forces a door connection/disconnection, else None."""
        return self.needed_doors(x, y, prevent_boundary_doors=prevent_boundary_doors)[door_num]

    def needed_doors(self, x, y, prevent_boundary_doors=False):
        res = []
        for dir in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
            if not (0 <= x + dir[0] < self.w() and 0 <= y + dir[1] < self.h()):
                res.append(False if prevent_boundary_doors else None)
                res.append(False if prevent_boundary_doors else None)
            else:
                n = self.get(x + dir[0], y + dir[1])
                if n is None:
                    res.append(None)
                    res.append(None)
                else:
                    d1 = Tile.doors_on_side((-dir[0], -dir[1]))[0]
                    d2 = Tile.doors_on_side((-dir[0], -dir[1]))[1]
                    res.append(n.has_door(d2))  # gotta flip it because it's... mirrored?
                    res.append(n.has_door(d1))
        return res

    def __str__(self):
        return str(self.partitions)


class TileGrid(Tileish):

    def __init__(self, grid_w, grid_h, tile_size=(16, 16)):
        self.tile_size = tile_size
        self.tiles = [None] * grid_w
        for i in range(0, len(self.tiles)):
            self.tiles[i] = [None] * grid_h

    def w(self):
        return self.tile_size[0] * self.grid_w()

    def h(self):
        return self.tile_size[1] * self.grid_h()

    def grid_w(self):
        return len(self.tiles)

    def grid_h(self):
        return len(self.tiles[0])

    def get_tile(self, grid_x, grid_y):
        if 0 <= grid_x < self.grid_w() and 0 <= grid_y < self.grid_h():
            return self.tiles[grid_x][grid_y]
        else:
            return None

    def tile_at(self, x, y):
        if x < 0 or y < 0:
            return None
        else:
            return self.get_tile(int(x / self.tile_size[0]), int(y / self.tile_size[1]))

    def get(self, x, y):
        t = self.tile_at(x, y)
        if t is None:
            return EMPTY
        else:
            rel_x, rel_y = self.rel_coords(x, y)
            return t.get(rel_x, rel_y)

    def rel_coords(self, x, y):
        rel_x = x % self.tile_size[0]
        rel_y = y % self.tile_size[1]
        return (rel_x, rel_y)

    def set_tile(self, grid_x, grid_y, tile):
        self.tiles[grid_x][grid_y] = tile

    def set(self, x, y, val):
        t = self.tile_at(x, y)
        if t is None:
            if val is not EMPTY:
                raise ValueError("tile is None at ({}, {})".format(x, y))
            else:
                return
        else:
            rel_x, rel_y = self.rel_coords(x, y)
            t.set(rel_x, rel_y, val)


class GridBuilder:

    @staticmethod
    def random_path_between(p1, p2, w, h):
        path = [p1]
        bad = []
        while path[-1] != p2:
            cur = path[-1]
            neighbors = list(TileFiller.neighbhors(cur[0], cur[1]))
            random.shuffle(neighbors)

            added_n = False
            while not added_n and len(neighbors) > 0:
                n = neighbors.pop()
                if 0 <= n[0] < w and 0 <= n[1] < h and n not in bad and n not in path:
                    path.append(n)
                    added_n = True

            if not added_n:
                bad.append(path.pop(-1))  # at a dead end

            if len(path) == 0:
                raise ValueError("failed to find path: p1={}, p2={}, w={}, h={}".format(p1, p2, w, h))

        return path

    @staticmethod
    def random_partition_grid(w, h, start=None, end=None):
        """returns: (path, partition_grid)"""
        start = start if start is not None else (random.randint(0, w - 1), random.randint(0, h - 1))
        end = end if end is not None else (random.randint(0, w - 1), random.randint(0, h - 1))

        p_grid = PartitionGrid(w, h)
        path = GridBuilder.random_path_between(start, end, w, h)

        entry_door = None
        for path_idx in range(0, len(path)):
            cur_path = path[path_idx]

            force_enabled = []
            force_disabled = []
            force_connected = []

            door_req = p_grid.needed_doors(cur_path[0], cur_path[1])
            for i in range(0, 8):
                if door_req[i] is True:
                    force_enabled.append(i)
                elif door_req[i] is False:
                    force_disabled.append(i)

            if path_idx < len(path) - 1:
                next_path = path[path_idx + 1]
                direction = (next_path[0] - cur_path[0], next_path[1] - cur_path[1])
                exit_door = random.choice(Tile.doors_on_side(direction))
                force_enabled.append(exit_door)
                if entry_door is not None:
                    force_connected = [entry_door, exit_door]

                entry_door = Tile.connecting_door(exit_door)  # setting for next loop

            p = Partition.random_partition(force_valid=True,
                                           force_doors=force_enabled,
                                           force_not_doors=force_disabled,
                                           force_connected=force_connected)

            p_grid.set(cur_path[0], cur_path[1], p)

        empty_coords = [xy for xy in RectUtils.coords_in_rect([0, 0, w, h]) if p_grid.get(xy[0], xy[1]) is None]
        random.shuffle(empty_coords)

        for (x, y) in empty_coords:
            door_req = p_grid.needed_doors(x, y)
            force_enabled = []
            force_disabled = []
            for i in range(0, 8):
                if door_req[i] is True:
                    force_enabled.append(i)
                elif door_req[i] is False:
                    force_disabled.append(i)
            p = Partition.random_partition(force_valid=True,
                                           force_doors=force_enabled,
                                           force_not_doors=force_disabled)
            p_grid.set(x, y, p)

        return path, p_grid


class RectUtils:

    @staticmethod
    def coords_in_rect(rect):
        for x in range(rect[0], rect[0] + rect[2]):
            for y in range(rect[1], rect[1] + rect[3]):
                yield (x, y)

    @staticmethod
    def coords_around_rect(rect):
        for x in range(rect[0]-1, rect[0] + rect[2] + 1):
            yield (x, rect[1]-1)
            yield (x, rect[1] + rect[3])
        for y in range(rect[1], rect[1] + rect[3]):
            yield (rect[0] - 1, y)
            yield (rect[0] + rect[2], y)

    @staticmethod
    def rect_containing(xy_coords):
        min_xy = [xy_coords[0][0], xy_coords[0][1]]
        max_xy = [xy_coords[0][0], xy_coords[0][1]]
        for (x, y) in xy_coords:
            min_xy[0] = min(min_xy[0], x)
            min_xy[1] = min(min_xy[1], y)
            max_xy[0] = max(max_xy[0], x)
            max_xy[1] = max(max_xy[1], y)
        return [min_xy[0], min_xy[1], max_xy[0] - min_xy[0] + 1, max_xy[1] - min_xy[1] + 1]

    @staticmethod
    def rects_intersect(r1, r2, buffer_zone=0):
        if r1[0] + r1[2] <= r2[0] - buffer_zone or r2[0] + r2[2] <= r1[0] - buffer_zone:
            return False
        elif r1[1] + r1[3] <= r2[1] - buffer_zone or r2[1] + r2[3] <= r1[1] - buffer_zone:
            return False
        return True


class TileFiller:

    @staticmethod
    def neighbhors(x, y, include_diags=False):
        yield (x + 1, y)
        yield (x, y + 1)
        yield (x - 1, y)
        yield (x, y - 1)

        if include_diags:
            yield (x + 1, y - 1)
            yield (x + 1, y + 1)
            yield (x - 1, y + 1)
            yield (x - 1, y - 1)

    @staticmethod
    def flood_fill(tile, start_x, start_y, on_values):
        if tile.get(start_x, start_y) not in on_values:
            return
        else:
            seen = {(start_x, start_y): None}  # i don't know how to make sets rn

            q = [(start_x, start_y)]

            while len(q) > 0:
                x, y = q.pop()
                if tile.get(x, y) in on_values:
                    yield (x, y)
                    for (n_x, n_y) in TileFiller.neighbhors(x, y):
                        if tile.in_tile(n_x, n_y) and (n_x, n_y) not in seen:
                            seen[(n_x, n_y)] = None
                            q.append((n_x, n_y))

    @staticmethod
    def calculate_partition(tile):
        all_doors = [0, 1, 2, 3, 4, 5, 6, 7]
        door_coords = {}
        for d in all_doors:
            door_coords[d] = tile.door_coords(d)[0]

        res = []
        while len(all_doors) > 0:
            d_num = all_doors.pop(0)
            d_x, d_y = tile.door_coords(d_num)[0]
            touches = [xy for xy in TileFiller.flood_fill(tile, d_x, d_y, (DOOR, FLOOR))]
            if len(touches) > 0:
                group = [d_num]
                for d in list(all_doors):
                    if door_coords[d] in touches:
                        group.append(d)
                        all_doors.remove(d)
                res.append(group)
        return Partition(res)

    @staticmethod
    def basic_door_fill(tile, partition):
        tile.fill(0, 0, tile.w(), tile.h(), EMPTY)

        for i in range(0, 8):
            for (x, y) in tile.door_coords(i):
                if i in partition.as_map:
                    tile.set(x, y, DOOR)
                else:
                    tile.set(x, y, EMPTY)

    @staticmethod
    def basic_floor_fill(tile, partition):
        TileFiller.basic_door_fill(tile, partition)
        unfilled_hubs = [0, 2, 4, 6]
        for i in range(0, 8):
            if partition.has_door(i):
                door_coords = tile.door_coords(i)
                hub_coords = tile.hub_coords(i)
                full_rect = RectUtils.rect_containing(door_coords + hub_coords)
                for (x, y) in RectUtils.coords_in_rect(full_rect):
                    tile.replace(x, y, EMPTY, FLOOR)

                if int(i/2) in unfilled_hubs:
                    unfilled_hubs.remove((i + i % 2) % 8)

        toggle_zones = [tile.hub_connection_coords(i) for i in range(0, 4)]
        for hub in unfilled_hubs:
            toggle_zones.append([xy for xy in tile.hub_coords(hub)])

        enabled = []
        for i in range(0, 2**len(toggle_zones)):  # very nice efficiency!
            enabled.append([min(2**j & i, 1) for j in range(0, len(toggle_zones))])
        random.shuffle(enabled)
        enabled.sort(key=lambda v: sum(v))

        for zone_toggle in enabled:
            for i in range(0, len(toggle_zones)):
                for (x, y) in toggle_zones[i]:
                    if zone_toggle[i]:
                        tile.set(x, y, FLOOR)
                    else:
                        tile.set(x, y, EMPTY)
            if TileFiller.calculate_partition(tile) == partition:
                return

    @staticmethod
    def basic_room_fill(tile, partition, min_rooms=1, max_rooms=4, iter_limit=300,
                        min_size=3, max_size=6, disjoint_rooms=True, connected_rooms=True):
        """returns: list of room rectangles"""
        TileFiller.basic_floor_fill(tile, partition)

        n = random.randint(min_rooms, max_rooms)
        iteration = 0

        rooms_placed = []

        while n > 0 and iteration < iter_limit:
            iteration += 1
            w = random.randint(min_size, max_size)
            h = random.randint(min_size, max_size)
            x = random.randint(1, tile.w() - w - 2)
            y = random.randint(1, tile.h() - h - 2)

            room_rect = [x, y, w, h]

            if disjoint_rooms:
                bad_intersect = False
                for r in rooms_placed:
                    if RectUtils.rects_intersect(room_rect, r):
                        bad_intersect = True
                        break
                if bad_intersect:
                    continue

            if connected_rooms:
                not_connected = True
                for (x, y) in RectUtils.coords_around_rect(room_rect):
                    if tile.get(x, y) != EMPTY:
                        not_connected = False
                        break
                if not_connected:
                    continue

            was_empty = []
            for xy in RectUtils.coords_in_rect(room_rect):
                if tile.get(xy[0], xy[1]) == EMPTY:
                    was_empty.append(xy)
                    tile.set(xy[0], xy[1], FLOOR)

            if TileFiller.calculate_partition(tile) == partition:
                # added a room successfully!
                rooms_placed.append(room_rect)
                n -= 1
            else:
                for xy in was_empty:
                    tile.set(xy[0], xy[1], EMPTY)

        return rooms_placed


class TileGridBuilder:

    @staticmethod
    def is_dangly(x, y, tile_grid):
        if tile_grid.get(x, y) != EMPTY:
            count = 0
            for n in TileFiller.neighbhors(x, y):
                if tile_grid.get(n[0], n[1]) != EMPTY:
                    count += 1
            if count <= 1:
                return True
        return False

    @staticmethod
    def clean_up_dangly_bits(tile_grid, source_xy=None):
        if source_xy is not None:
            if TileGridBuilder.is_dangly(source_xy[0], source_xy[1], tile_grid):
                tile_grid.set(source_xy[0], source_xy[1], EMPTY)
                for n in TileFiller.neighbhors(source_xy[0], source_xy[1]):
                    TileGridBuilder.clean_up_dangly_bits(tile_grid, source_xy=n)
            else:
                return
        else:
            for x in range(0, tile_grid.w()):
                for y in range(0, tile_grid.h()):
                    if TileGridBuilder.is_dangly(x, y, tile_grid):
                        TileGridBuilder.clean_up_dangly_bits(tile_grid, source_xy=(x, y))

    @staticmethod
    def is_valid_door_coord(x, y, tile_grid):
        horz_door = (tile_grid.get(x-1, y) == FLOOR and tile_grid.get(x+1, y) == FLOOR and
                     tile_grid.get(x, y-1) == EMPTY and tile_grid.get(x, y+1) == EMPTY)
        vert_door = (tile_grid.get(x, y-1) == FLOOR and tile_grid.get(x, y+1) == FLOOR and
                     tile_grid.get(x-1, y) == EMPTY and tile_grid.get(x+1, y) == EMPTY)

        return horz_door != vert_door

    @staticmethod
    def clean_up_doors(tile_grid):
        for x in range(0, tile_grid.w()):
            for y in range(0, tile_grid.h()):
                if tile_grid.get(x, y) == DOOR and not TileGridBuilder.is_valid_door_coord(x, y, tile_grid):
                    tile_grid.set(x, y, FLOOR)

    @staticmethod
    def add_walls(tile_grid):
        needs_walls = []
        for x in range(0, tile_grid.w()):
            for y in range(0, tile_grid.h()):
                if (tile_grid.get(x, y) == EMPTY):
                    for n in TileFiller.neighbhors(x, y, include_diags=True):
                        if tile_grid.get(n[0], n[1]) != EMPTY:
                            needs_walls.append((x, y))
                            continue
        for (x, y) in needs_walls:
            tile_grid.set(x, y, WALL)


class Feature(Tileish):

    def __init__(self, feat_id, replace, place, can_rotate=True):
        self.feat_id = feat_id
        self.replace = replace
        self.place = place
        self.can_rotate = can_rotate

        self._validate()

    def _validate(self):
        if len(self.replace) == 0 or len(self.replace[0]) == 0:
            raise ValueError("empty feature {}".format(self.feat_id))
        for row in self.replace:
            if len(row) != len(self.replace[0]):
                raise ValueError("non-rectangular feature {}".format(self.feat_id))

        if len(self.replace) != len(self.place):
            raise ValueError("invalid feature {}: mismatched place/replace heights {} != {}".format(
                self.feat_id, len(self.replace), len(self.place)
            ))
        for i in range(0, len(self.replace)):
            place_width = len(self.replace[i])
            replace_width = len(self.place[i])
            if place_width != replace_width:
                raise ValueError("invalid feature {}: mismatched place/replace widths on row {}: {} != {}".format(
                    self.feat_id, i, place_width, replace_width
                ))

    def w(self):
        return len(self.replace[0])

    def h(self):
        return len(self.replace)

    def get(self, x, y):
        if 0 <= x < self.w() and 0 <= y < self.h():
            return self.replace[y][x]
        else:
            return EMPTY

    def get_place_val(self, x, y):
        return self.place[y][x]

    def rotated(self, rots=1):
        if rots <= 0:
            return self
        elif not self.can_rotate:
            return ValueError("can't rotate feature: {}".format(self.feat_id))

        place = ["" for _ in range(0, self.w())]
        replace = ["" for _ in range(0, self.w())]

        for i in range(0, self.w()):
            for j in range(self.h()-1, -1, -1):
                place[i] = place[i] + self.place[j][i]
                replace[i] = replace[i] + self.replace[j][i]

        return Feature(self.feat_id, place, replace, can_rotate=True).rotated(rots=rots-1)

    def can_place_at(self, tilish, x, y):
        for feat_x in range(0, self.w()):
            for feat_y in range(0, self.h()):
                feat_val = self.get(feat_x, feat_y)
                if feat_val == "?":
                    continue
                elif feat_val != tilish.get(x + feat_x, y + feat_y):
                    return False
        return True

    def __str__(self):
        return "Feature:[{}, replace={}, place={}]".format(self.feat_id, self.replace, self.place)


class FeatureUtils:

    @staticmethod
    def all_possible_placements_overlapping_rect(feature, tilish, rect):
        """returns: list of valid feature placements (x, y)"""
        res = []
        for x in range(rect[0] - feature.w() + 1, rect[0] + rect[2]):
            for y in range(rect[1] - feature.h(), rect[1] + rect[3]):
                if feature.can_place_at(tilish, x, y):
                    res.append((x, y))
        return res

    @staticmethod
    def try_to_place_feature_into_rect(feature, tilish, rect):
        rots = [0]
        if feature.can_rotate:
            rots.extend([1, 2, 3])

        random.shuffle(rots)
        for rot in rots:
            rotated_feature = feature.rotated(rot)
            possible_placements = FeatureUtils.all_possible_placements_overlapping_rect(feature, tilish, rect)
            if len(possible_placements) > 0:
                placement = random.choice(possible_placements)
                FeatureUtils.write_into(rotated_feature, tilish, placement[0], placement[1])
                return True

        return False

    @staticmethod
    def write_into(feature, tile_grid, x, y):
        # print("placing feature {} at ({}, {})".format(feature.feat_id, x, y))
        for feat_x in range(0, feature.w()):
            for feat_y in range(0, feature.h()):
                feat_val = feature.get_place_val(feat_x, feat_y)
                if feat_val != "?":
                    tile_grid.set(x + feat_x, y + feat_y, feat_val)

    CHAR_MAP = {"X": FLOOR,
                ".": EMPTY,
                "p": PLAYER,
                "v": ENTRANCE,
                "e": EXIT,
                "m": MONSTER,
                "c": CHEST,
                "i": STRAY_ITEM,
                "n": NPC,
                "s": SPECIAL}

    @staticmethod
    def convert_char(c):
        if c in FeatureUtils.CHAR_MAP:
            return FeatureUtils.CHAR_MAP[c]
        else:
            return c

    @staticmethod
    def convert(feature_def):
        res = []
        for word in feature_def:
            new_word = "".join(FeatureUtils.convert_char(c) for c in word)
            res.append(new_word)
        return res

class Features:
    START = Feature("start",
                    FeatureUtils.convert(["XXX", "...", "?.?"]),
                    FeatureUtils.convert(["XpX", ".v.", "?.?"]), can_rotate=False)

    EXIT = Feature("exit_door",
                   FeatureUtils.convert([".", "X"]),
                   FeatureUtils.convert([".", "e"]), can_rotate=False)

    SMALL_MONSTER = Feature("monster_2x2",
                            FeatureUtils.convert(["XX", "XX"]),
                            FeatureUtils.convert(["mX", "Xm"]))

    LARGE_MONSTER = Feature("monster_3x3",
                            FeatureUtils.convert(["XXX", "XXX", "XXX"]),
                            FeatureUtils.convert(["mXX", "XXm", "XmX"]))

    CHEST = Feature("chest",
                    FeatureUtils.convert(["XXX", "XXX", "XXX"]),
                    FeatureUtils.convert(["XXX", "XcX", "XXX"]))

    STRAY_ITEM = Feature("stray_item",
                         FeatureUtils.convert(["X"]),
                         FeatureUtils.convert(["i"]))

    WISHING_WELL = Feature("wishing_well",
                           FeatureUtils.convert(["....", "XXXX", "XXXX"]),
                           FeatureUtils.convert(["....", "XnsX", "XXXX"]))

    QUEST_NPC = Feature("quest_npc",
                        FeatureUtils.convert(["XXX", "XXX", "..."]),
                        FeatureUtils.convert(["XXX", "XnX", "..."]))

    @staticmethod
    def get_random_feature():
        return random.choice([Features.SMALL_MONSTER,
                              Features.CHEST,
                              Features.QUEST_NPC,
                              Features.LARGE_MONSTER,
                              Features.WISHING_WELL,
                              Features.QUEST_NPC,
                              Features.STRAY_ITEM])


class Partition:
    def __init__(self, p):
        for g in p:
            g.sort()
        p.sort()

        self.p = p
        self.as_map = {}  # door_number -> group number

        for i in range(0, len(p)):
            group = p[i]
            if len(group) == 0:
                raise ValueError("empty group in partition: {}".format(p))
            for door_num in group:
                if door_num in self.as_map:
                    raise ValueError("door {} appears multiple times: {}".format(door_num, p))
                self.as_map[door_num] = i

    def get_doors(self):
        return [i for i in range(0, 8) if i in self.as_map]

    def has_door(self, door_num):
        return door_num in self.as_map

    def num_groups(self):
        return len(self.p)

    def is_valid(self):
        # doors that share the same corner must connect if both are present.
        corners = [(0, 7), (1, 2), (3, 4), (5, 6)]
        for c in corners:
            if c[0] in self.as_map and c[1] in self.as_map:
                if self.as_map[c[0]] != self.as_map[c[1]]:
                    return False

        ordered_groups = []
        for door_num in range(0, 8):
            if door_num in self.as_map:
                group_num = self.as_map[door_num]
                if len(ordered_groups) == 0:
                    ordered_groups.append(group_num)
                elif ordered_groups[-1] != group_num:
                    if door_num != 7 or group_num != ordered_groups[0]:
                        ordered_groups.append(group_num)
        as_str = "".join([str(v) for v in ordered_groups])

        # two groups cannot make an A-B-A-C pattern
        pattern = re.compile(r'(\d)[^\1]+\1[^\1]')
        if pattern.search(as_str) is not None:
            return False

        # or an A-B-C-B pattern
        pattern = re.compile(r'(\d)([^\1])[^\2]+\2')
        if pattern.search(as_str) is not None:
            return False

        return True

    def __repr__(self):
        res = "Partition:{}".format(self.p)
        if not self.is_valid():
            res += " (invalid)"
        return res

    def __eq__(self, other):
        return self.p == other.p  # should both have been sorted the same

    @staticmethod
    def random_partition(force_valid=True, min_doors=0, max_doors=8, force_doors=[], force_not_doors=[], force_connected=[]):

        p = None
        while p is None or (force_valid and not p.is_valid()):

            doors = [i for i in range(0, 8) if i in force_doors or i in force_connected]
            optional_doors = [i for i in range(0, 8) if (i not in doors and i not in force_not_doors)]

            to_choose = random.randint(min_doors - len(doors), max_doors - len(doors))
            if to_choose < 0:
                to_choose = 0
            elif to_choose > len(optional_doors):
                to_choose = len(optional_doors)

            doors.extend(random.sample(optional_doors, to_choose))

            if len(doors) == 0:
                return Partition([])

            res = []

            if len(force_connected) > 0:
                for d in force_connected:
                    doors.remove(d)

            if len(doors) == 0:
                if len(force_connected) > 0:
                    return Partition([list(force_connected)])
                else:
                    return Partition([])

            n_groups = 1 + int((len(doors) - 1) * random.random())
            random.shuffle(doors)
            for i in range(0, n_groups):
                res.append([doors[i]])

            if n_groups < len(doors):
                for i in range(n_groups, len(doors)):
                    res[int(n_groups * random.random())].append(doors[i])

            if len(force_connected) > 0:
                i = random.randint(0, n_groups)
                if i == n_groups:
                    res.append(list(force_connected))
                else:
                    res[i].extend(force_connected)

            p = Partition(res)

        return p


if __name__ == "__main__":
    dims = (3, 3)
    start = (0, 0)
    end = (dims[0]-1, dims[1]-1)
    t_size = 12
    path, p_grid = GridBuilder.random_partition_grid(dims[0], dims[1], start=start, end=end)

    t_grid = TileGrid(dims[0], dims[1], tile_size=(t_size, t_size))

    room_map = {}  # (grid_x, grid_y) -> list of room_rects
    empty_rooms = []

    for x in range(0, dims[0]):
        for y in range(0, dims[1]):
            part = p_grid.get(x, y)
            if part is not None:
                tile = Tile(t_size + 1, door_len=1, door_offs=3)
                rooms_in_tile = TileFiller.basic_room_fill(tile, part, disjoint_rooms=True, connected_rooms=True)
                rooms = [[x*t_size + r[0], y*t_size + r[1], r[2], r[3]] for r in rooms_in_tile]

                if len(rooms) > 0:
                    room_map[(x, y)] = rooms
                    empty_rooms.extend(rooms)

                t_grid.set_tile(x, y, tile)
                print(t_grid)
                time.sleep(0.5)

    print(t_grid)
    time.sleep(0.5)

    TileGridBuilder.clean_up_dangly_bits(t_grid)
    TileGridBuilder.clean_up_doors(t_grid)

    if len(empty_rooms) < 4:
        raise ValueError("super low number of rooms..?")

    start_placed = False
    for p in path:
        rooms_in_p = list(room_map.get(p))
        random.shuffle(rooms_in_p)
        for r in rooms_in_p:
            if r not in empty_rooms:
                continue
            if FeatureUtils.try_to_place_feature_into_rect(Features.START, t_grid, r):
                start_placed = True
                empty_rooms.remove(r)
                break
        if start_placed:
            break

    if not start_placed:
        raise ValueError("failed to place start anywhere on path...")

    end_placed = False
    for p in reversed(path):
        rooms_in_p = list(room_map.get(p))
        random.shuffle(rooms_in_p)
        for r in rooms_in_p:
            if r not in empty_rooms:
                continue
            if FeatureUtils.try_to_place_feature_into_rect(Features.EXIT, t_grid, r):
                end_placed = True
                empty_rooms.remove(r)
                break
        if end_placed:
            break

    if not start_placed:
        raise ValueError("failed to place end anywhere on path...")

    print(t_grid)
    time.sleep(0.5)

    while len(empty_rooms) > 0:
        r = empty_rooms.pop()
        feat = Features.get_random_feature()
        if random.random() > 0.333:
            FeatureUtils.try_to_place_feature_into_rect(feat, t_grid, r)

    print(t_grid)
    time.sleep(0.5)

    TileGridBuilder.add_walls(t_grid)

    print(t_grid)
    time.sleep(0.5)





