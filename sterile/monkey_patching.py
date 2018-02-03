from pirates import *
import math
from types import MethodType  # may not work

# CONSTANTS

# See https://piratez.skillz-edu.org/static/c785238d5a9dbb1feea8f1b057b06393958cfe2ff34c8ee820d7bb2df4a2bc33/environment/docs/Python/PirateGame.html#capsule_pickup_range
MOVE_SIZE = 200
PUSH_DISTANCE = 600
MAP_SIZE = 6400
GAME_TURNS = 800
TIME_LOSE_SUICIDE_THRESHOLD = int(0.8 * GAME_TURNS)
TIME_LOSE_SUICIDE_POINT_THRESHOLD = int(0.4 * GAME_TURNS)
MAX_POINTS = 8
POINTS_LOSE_SUICIDE_THRESHOLD = int(0.8 * MAX_POINTS)  # 6
DEBUG = True


# -------------------------------------- GENERAL FUNCTIONS -------------------------------------


def update_enemy_locations(game, pl, cl, mv):
    '''
    :param game: the game, will be used to retrieve positions
    :param pl: previous locations.
    :param cl: current locations.
    :param mv: movement vectors.
    :return: nothing. The dicts are modified, no need to return them.
    '''

    for i in game.get_enemy_living_pirates():
        pl[i.unique_id] = cl[i.unique_id]
        cl[i.unique_id] = i.get_location()
        mv[i.unique_id] = cl[i.unique_id].subtract(pl[i.unique_id])


def expected_location(pirate, pl, cl, mv):
    # TODO make me smarter
    """Receives a pirate, returns its expected location in the next turn."""
    for map_location in get_all_map_locations():
        if 198 <= cl[pirate.unique_id].distance(map_location) - pl[pirate.unique_id].distance(map_location) <= 202:
            return map_location
    return pirate.location.towards(mv[pirate.unique_id], MOVE_SIZE)


def get_all_map_locations(game=PirateGame):


def dbg(msg):
    if DEBUG:
        debug(msg)  # builtin


def locations_of(*arg):
    '''
    Helper function, written by Yoav Shai. Returns locations of items.
    Usage: a, b = locations_of(a, b)
    '''
    return [int(x) for x in arg]


def sort_by_distance_from(objects, place):
    place = place.get_location()
    return sorted(objects, key=lambda o: place.distance(o.get_location()))


def closest_wall(loc):
    """Receives either a GameObject or a location, returns Location of nearest wall"""
    x = loc.get_location().row
    y = loc.get_location().col
    distances = [x, MAP_SIZE - x, y, MAP_SIZE - y]
    index = distances.index(min(distances))
    if index == 0:
        return Location(0, y)
    elif index == 1:
        return Location(MAP_SIZE, y)
    elif index == 2:
        return Location(x, 0)
    else:
        return Location(x, MAP_SIZE)


# ------------------------------------- SMARTPIRATE FUNCTIONS -----------------------------------------


class SmartPirate(object):
    def __init__(self, pirate, game):
        self.p = pirate
        self.g = game

    def smart_sail(self, locations_and_weights, destination):
        '''
        Receives a list of tuples, each containing a location and its weight.
        Written by Ben Rapoport, is probably broken.
        '''

        def get_path_cost(origin, locations_and_weights, destination, available_moves):

            origin, destination = locations_of(origin, destination)

            if available_moves == 0:
                return float('inf'), None
            else:
                cost_of_move = 0
                for loc in locations_and_weights:
                    cost_of_move += origin.distance(loc[0]) * loc[1]

                if origin.distance(destination) < MOVE_SIZE:
                    return cost_of_move, destination
                else:
                    side_destinations = []
                    number_of_possibilities = 8
                    for i in range(number_of_possibilities):
                        angle = i / number_of_possibilities * 2 * math.pi
                        x = int(math.cos(angle) * 10000)
                        y = int(math.sin(angle) * 10000)
                        side_destinations.append(origin.towards(Location(x, y), MOVE_SIZE))

                    costs = []
                    for i in range(number_of_possibilities):
                        costs.append(
                            get_path_cost(side_destinations[i], locations_and_weights, destination, available_moves - 1))

                    minimum = min([cost[0] for cost in costs])

                    for cost in costs:
                        if cost[0] == minimum:
                            minimum_loc = cost[1]
                            break

                    return cost_of_move + minimum, minimum_loc

        moves = round(self.get_location().distance(destination.get_location()) / MOVE_SIZE) + 1
        _, best_destination = get_path_cost(self.get_location(), locations_and_weights, destination, moves)
        self.p.sail(best_destination)

    def retrieve(self, locations_and_weights, my_capsule):
        need_to_act = list(retrievers)
        if my_capsule.holder is None:
            if len(retrievers) > 0:
                # if none of our pirates have our capsule
                my_closest_pirate = sort_by_distance_from(retrievers, my_capsule.get_location())[0]
                '''threats = threatened_by(my_closest_pirate)
                if len(threats) == 0:
                    my_closest_pirate.sail(my_capsule.location)
                else:
                    my_closest_pirate.push(threats[0], should_push_to(threats[0]))
                '''
                my_closest_pirate.sail(my_capsule.get_location())
                for my_pirate in sort_by_distance_from(need_to_act, my_closest_pirate.get_location())[1:-1]:
                    my_pirate.sail(my_closest_pirate.location)
                    need_to_act.remove(my_pirate)

                if len(retrievers) > 2:
                    last_pirate = sort_by_distance_from(need_to_act, my_closest_pirate.location)[-1]
                    last_pirate.sail(my_capsule.initial_location.towards(my_mothership.location, PICKUP_RANGE - 1))
                    # move the closest I can to my base that will also let me pick up the capsule


        else:
            my_capsule.holder.sail(my_mothership.location)
            need_to_act.remove(my_capsule.holder)
            # TODO else - protect himself
            for my_pirate in sort_by_distance_from(need_to_act, my_capsule.holder.location)[0:len(need_to_act) / 2]:
                my_pirate.sail(my_capsule.holder.location.towards(my_mothership.location, 200))
                need_to_act.remove(my_pirate)

            for camper in sort_by_distance_from(need_to_act, my_capsule.holder)[len(need_to_act) / 2:len(need_to_act)]:
                if camper.location.distance(my_capsule.initial_location) > PICKUP_RANGE:
                    camper.sail(my_capsule.initial_location)


    def threats(self, movement_vectors, turns_forward=3, rad=200):
        '''Returns a list of threats, sorted by most to least critical/feasible.'''
        enemy_pirates = self.g.get_enemy_living_pirates()
        threats = [p for p in enemy_pirates if p.can_push(self.p)]
        for tf in xrange(1, turns_forward+1):
            for ep in enemy_pirates:
                if movement_vectors[ep.id] # TODO complete

    def operate(self, game):
        '''
        Main function of the Pirate.
        This is the function to be executed on every round of the game. In it, a pirate should figure out his role
        in the team and operate accordingly.
        '''
        distance_from_capsule = self.distance(game.get_my_capsule())
        distance_from_home = self.distance(game.get_my_mothership())
        distance_from_closest_enemy = self.distance(game.get_enemy_living_pirates()[0]) if len(
            game.get_enemy_living_pirates()) > 0 else None

        # first of all - if we're gonna lose, let's try to make them crash. Perhaps they're dumb.
        if game.get_myself().score + LOSE_SUICIDE_THRESHOLD <= game.get_enemy().score or (
                game.turn > TIME_LOSE_SUICIDE_THRESHOLD and game.get_myself.score() + TIME_LOSE_SUICIDE_POINT_THRESHOLD <= game.get_enemy().score):
            self.sail(closest_wall(self))

        # TODO much more

def do_turn(game):
    # enemy tracking stuff
    previous_locations = {}
    current_locations = {}
    movement_vectors = {}
    update_enemy_locations(game, previous_locations, current_locations, movement_vectors)

    # You need to import them all manually, at least for now.
    Pirate.smart_sail = MethodType(smart_sail)  # declaration option #1, works better
    Pirate.retrieve = retrieve  # also works, doesn't need the import.
    for my_pirate in game.get_my_living_pirates():
        my_pirate.operate()
