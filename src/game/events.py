
from enum import Enum
from src.utils.util import Utils


class EventQueue:

    def __init__(self):
        self.events = []

        self.next_events = {}  # int: delay -> list(Event)

    def add(self, event, delay=0):
        if delay not in self.next_events:
            self.next_events[delay] = []

        self.next_events[delay].append(event)

    def flip(self):
        self.events.clear()

        if 0 in self.next_events:
            self.events = self.next_events[0]
            del self.next_events[0]

        all_delays = list(delay for delay in self.next_events)
        all_delays.sort()

        for delay in all_delays:
            new_delay = max(0, delay - 1)
            if new_delay not in self.next_events:
                self.next_events[new_delay] = []

            self.next_events[new_delay].extend(self.next_events[delay])
            del self.next_events[delay]

    def all_events_with_type(self, single_type):
        for e in self.events:
            if e.get_type() == single_type:
                yield e

    def all_events(self, types=None, predicate=lambda x: True):
        if types is not None:
            types = Utils.listify(types)
            for t in types:
                for e in self.all_events_with_type(t):
                    if predicate(e):
                        yield e
        else:
            for e in self.events:
                if predicate(e):
                    yield e

    def has_event(self, types=None, predicate=None):
        if types is not None:
            types = Utils.listify(types)
            for t in types:
                for e in self.all_events_with_type(t):
                    if predicate is None or predicate(e):
                        return True
        else:
            for e in self.events:
                if predicate is None or predicate(e):
                    return True

        return False


class EventType(Enum):
    # these are "something happened" events
    ACTOR_KILLED = "ACTOR_KILLED"
    PLAYER_DIED = "PLAYER_DIED"
    GAME_WIN = "GAME_WIN"
    DOOR_OPENED = "DOOR_OPENED"
    ACTION_STARTED = "ACTION_STARTED"
    ACTION_FINISHED = "ACTION_FINISHED"
    DIALOG_EXIT = "DIALOG_EXIT"
    ENTERED_BOX = "ENTERED_BOX"
    EXITED_BOX = "EXITED_BOX"
    TRIGGERED_BOX = "TRIGGERED_BOX"
    ITEM_DROPPED = "ITEM_DROPPED"
    TOGGLED_SIDEPANEL = "TOGGLED_SIDEPANEL"
    ROTATED_ITEM = "ROTATED_ITEM"

    # these are "please do something" events
    NEW_ZONE = "NEW_ZONE"
    GAME_EXIT = "GAME_EXIT"
    NEW_GAME = "NEW_GAME"


class Event:
    def __init__(self, event_type, data, description=""):
        self._event_type = event_type
        self._data = data
        self.description = description

    def get_type(self):
        return self._event_type

    def get_data(self):
        return self._data

    def get_msg(self):
        return self.description

    def __repr__(self):
        return "Event({}, {}, {})".format(self._event_type, self._data, self.description)


class EventListenerScope(Enum):
    ZONE = 1
    PERMANENT = 2


class EventListener:

    def __init__(self, action, event_type, predicate, scope=EventListenerScope.ZONE, single_use=False):
        """
        Event, World -> () action: runnable action to perform when event occurs
        EventType event_type: type of event to listen for
        Event -> bool predicate: predicate for events to accept
        EventListenerScope scope: scope of listener
        bool single_use: whether to auto-remove listener after one trigger
        """
        self.event_type = event_type
        self.predicate = predicate if predicate is not None else lambda x: True
        self.action = action
        self.scope = scope
        self.single_use = single_use

    def do_action(self, event, world):
        self.action(event, world)


class DoorOpenEvent(Event):
    def __init__(self, door_uid, grid_x, grid_y):
        Event.__init__(self, EventType.DOOR_OPENED, (door_uid, grid_x, grid_y), "door opened at ({}, {})".format(grid_x, grid_y))

    def get_position(self):
        return (self.get_data()[1], self.get_data()[2])

    def get_uid(self):
        return self.get_data()[0]


# TODO - not really used
class TriggerBoxEvent(Event):
    def __init__(self, box_id, event_type, desc):
        Event.__init__(self, event_type, box_id, description=desc)

    def get_box_id(self):
        return self.get_data()

    @staticmethod
    def new_enter_event(box_id):
        return TriggerBoxEvent(box_id, EventType.ENTERED_BOX, "entered box with id: {}".format(box_id))

    @staticmethod
    def new_exit_event(box_id):
        return TriggerBoxEvent(box_id, EventType.EXITED_BOX, "exited box with id: {}".format(box_id))

    @staticmethod
    def new_trigger_event(box_id):
        return TriggerBoxEvent(box_id, EventType.TRIGGERED_BOX, "triggered box with id: {}".format(box_id))


class DialogExitEvent(Event):
    def __init__(self, uid, opt_idx):
        Event.__init__(self, EventType.DIALOG_EXIT, (uid, opt_idx), description="exited dialog with uid: " + str(uid))

    def get_uid(self):
        return self.get_data()[0]

    def get_option_idx(self):
        return self.get_data()[1]


class NewZoneEvent(Event):

    def __init__(self, next_zone, current_zone, show_zone_title_menu=True):
        data = (next_zone, current_zone, show_zone_title_menu)
        desc = "moved from zone {} to {} via {}".format(current_zone, next_zone, show_zone_title_menu)
        Event.__init__(self, EventType.NEW_ZONE, data, description=desc)

    def get_next_zone(self):
        return self.get_data()[0]

    def get_current_zone(self):
        return self.get_data()[1]

    def get_show_zone_title(self):
        return self.get_data()[2]


class GameExitEvent(Event):

    def __init__(self):
        Event.__init__(self, EventType.GAME_EXIT, None, description="exit game")


class NewGameEvent(Event):

    def __init__(self, instant_start=True):
        my_data = tuple([instant_start])
        Event.__init__(self, EventType.NEW_GAME, my_data, description="new game")

    def get_instant_start(self):
        return self.get_data()[0]


class ActionFinishedEvent(Event):

    def __init__(self, action):
        data = (action.get_actor().get_uid(), action.get_type(), action.get_position(), action.get_item())
        Event.__init__(self, EventType.ACTION_FINISHED, data, description="action completed")

    def get_uid(self):
        return self.get_data()[0]

    def get_action_type(self):
        return self.get_data()[1]

    def get_position(self):
        return self.get_data()[2]

    def get_item(self):
        return self.get_data()[3]


class ActionStartedEvent(Event):

    def __init__(self, action):
        data = (action.get_actor().get_uid(), action.get_type(), action.get_position(), action.get_item())
        Event.__init__(self, EventType.ACTION_STARTED, data, description="action started")

    def get_uid(self):
        return self.get_data()[0]

    def get_action_type(self):
        return self.get_data()[1]

    def get_position(self):
        return self.get_data()[2]

    def get_item(self):
        return self.get_data()[3]


class PlayerDiedEvent(Event):

    def __init__(self):
        Event.__init__(self, EventType.PLAYER_DIED, None, description="player died")


class GameWinEvent(Event):

    def __init__(self):
        Event.__init__(self, EventType.GAME_WIN, None, description="game win")


class ToggledSidepanelEvent(Event):

    def __init__(self, panel_type, opened):
        Event.__init__(self, EventType.TOGGLED_SIDEPANEL, (panel_type, opened), description="toggled sidepanel")

    def get_panel_type(self):
        return self.get_data()[0]

    def get_opened(self):
        """returns: bool, True if the panel was opened, False otherwise."""
        return self.get_data()[1]


class RotatedItemEvent(Event):

    def __init__(self, item):
        Event.__init__(self, EventType.ROTATED_ITEM, (item,), description="rotated item")

    def get_item(self):
        return self.get_data()[0]


class ActorKilledEvent(Event):

    def __init__(self, actor_uid, killer_uid):
        if killer_uid == actor_uid:
            # just makes things simpler this way
            killer_uid = None

        data = (actor_uid, killer_uid)
        Event.__init__(self, EventType.ACTOR_KILLED, data, description="actor killed")

    def get_actor_uid(self):
        return self.get_data()[0]

    def get_killer_uid(self):
        return self.get_data()[1]


# TODO - not used
class ItemDroppedEvent(Event):

    def __init__(self, item, dropped_by=None):
        data = (item, dropped_by)
        Event.__init__(self, EventType.ITEM_DROPPED, data, description="item dropped")

    def get_item(self):
        return self.get_data()[0]

    def get_dropped_by(self):
        return self.get_data()[1]


def play_game(p1_target, p2_target, p3_target):
    import random

    rolls = [random.random() < 0.5 for _ in range(0, len(p1_target))]
    while True:
        if p1_target == rolls:
            return 0
        elif p2_target == rolls:
            return 1
        elif p3_target == rolls:
            return 2
        else:
            new_roll = random.random() < 0.5
            rolls.append(new_roll)
            rolls.pop(0)


if __name__ == "__main__":
    H = True
    T = False
    p1_target = [H, T, T]
    p2_target = [T, T, H]
    p3_target = [H, T, H]

    wins = [0, 0, 0]

    n = 100000

    for i in range(0, n):
        wins[play_game(p1_target, p2_target, p3_target)] += 1

    print("{} wins: {}%\n{} wins: {}%\n{} wins: {}".format(p1_target, wins[0] / n,
                                                           p2_target, wins[1] / n,
                                                           p3_target, wins[2] / n))