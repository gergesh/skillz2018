from pirates import *
#from genf import * # TODO figure out how to import functions from another file, should be possible.
import math


# CONSTANTS
# See https://piratez.skillz-edu.org/static/c785238d5a9dbb1feea8f1b057b06393958cfe2ff34c8ee820d7bb2df4a2bc33/environment/docs/Python/PirateGame.html#capsule_pickup_range
MOVE_SIZE = 200
PUSH_DISTANCE = 600
MAP_SIZE = 6400
GAME_TURNS = 750
TIME_LOSE_SUICIDE_THRESHOLD = int(0.8 * GAME_TURNS)
TIME_LOSE_SUICIDE_POINT_THRESHOLD = int(0.4 * GAME_TURNS)
MAX_POINTS = 8
POINTS_LOSE_SUICIDE_THRESHOLD = int(0.8 * MAX_POINTS)  # 6
DEBUG = True

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


def expected_location(pirate, pl, mv, turns=1):
    '''
    :param pirate: The pirate to track.
    :param pl: A dictionary of pirate IDs and their previous locations.
    :param mv: A dictionary of pirate IDs and their movement vectors.
    :param turns: Turns forward to anticipate.
    :return: Location object,
    '''
    # TODO make me smarter
    for map_location in get_all_map_locations():
        if 198 <= pirate.get_location().distance(map_location) - pl[pirate.unique_id].distance(map_location) <= 202:
            return pirate.towards(map_location, MOVE_SIZE*turns)
    return pl[pirate.id].towards(pirate.get_location(), MOVE_SIZE*(turns+1))


def get_all_map_locations(game):
    l = game.get_living_asteroids() + game.get_all_capsules() + game.get_my_living_pirates() + game.get_enemy_living_pirates() + game.get_all_motherships()
    return [i.get_location() for i in l]

def dbg(msg, game):
    if DEBUG:
        game.debug(msg)  # builtin


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

def loc_mul(loc, n):
    loc = loc.get_location()
    for _ in xrange(n):
        loc.add(n)
    return loc


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

        moves = round(self.p.get_location().distance(destination.get_location()) / MOVE_SIZE) + 1
        _, best_destination = get_path_cost(self.p.get_location(), locations_and_weights, destination, moves)
        self.p.sail(best_destination)

    def threats(self, movement_vectors, turns_forward=3, rad=200):
        '''Returns a list of threats, sorted by most to least critical/feasible.'''
        enemy_pirates = self.g.get_enemy_living_pirates()
        threats = [p for p in enemy_pirates if p.can_push(self.p)]
        for tf in xrange(1, turns_forward+1):
            for ep in enemy_pirates:
                if ep not in threats and self.p.distance(ep.get_location() + loc_mul(movement_vectors[ep.id], tf)) < rad:
                    threats.append(ep)

        return threats

    def operate(self):
        '''
        Main function of the Pirate.
        This is the function to be executed on every round of the game. In it, a pirate should figure out his role
        in the team and operate accordingly.
        '''

        # some things we will need
        game = self.g
        my_capsules = game.get_my_capsules()
        enemy_capsules = game.get_enemy_capsules()
        my_pirates = game.get_my_living_pirates()
        enemy_pirates = game.get_enemy_living_pirates()
        my_motherships = game.get_my_motherships()
        enemy_motherships = game.get_enemy_motherships()
        asteroids = game.get_living_asteroids()

        # first of all - if we're gonna lose, let's try to make them crash. Perhaps they're dumb.
        if game.get_myself().score + POINTS_LOSE_SUICIDE_THRESHOLD <= game.get_enemy().score or (
                game.turn > TIME_LOSE_SUICIDE_THRESHOLD and game.get_myself.score() + TIME_LOSE_SUICIDE_POINT_THRESHOLD <= game.get_enemy().score):
            self.p.sail(closest_wall(self))
            return

        if not my_capsules[0].holder is self.p:
            self.p.sail(my_capsules[0].get_location())
        else:
            self.p.sail(my_motherships[0])

        # TODO much more

def do_turn(game):
    #update_enemy_locations(game, previous_locations, current_locations, movement_vectors)  # TODO make me work
    for my_pirate in game.get_my_living_pirates():
        SmartPirate(my_pirate, game).operate()