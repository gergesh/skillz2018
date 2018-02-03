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

# --------------------------------------------------- LIEUTENANT FUNCTIONS --------------------------------------

def update_locations(game):
    '''
    :param game: the game, will be used to retrieve positions
    :param pl: previous locations.
    :param cl: current locations.
    :param mv: movement vectors.
    :return: nothing. The dicts are modified, no need to return them.
    '''

    global previous_locations, current_locations, movement_vectors

    for i in game.get_enemy_living_pirates() + game.get_my_living_pirates() + game.get_living_asteroids():
        if i.unique_id in current_locations:
            previous_locations[i.unique_id] = current_locations[i.unique_id]
            current_locations[i.unique_id] = i.get_location()
            movement_vectors[i.unique_id] = current_locations[i.unique_id].subtract(previous_locations[i.unique_id])
        else:
            current_locations[i.unique_id] = i.get_location()
            movement_vectors[i.unique_id] = Location(0, 0)


def expected_location(pirate, turns=1):
    '''
    :param pirate: The pirate to track.
    :param turns: Turns forward to anticipate.
    :return: Location object
    '''

    global previous_locations
    # TODO make me smarter
    for map_location in get_all_map_locations(GAME):
        if 198 <= pirate.get_location().distance(map_location) - previous_locations[pirate.unique_id].distance(map_location) <= 202:
            return pirate.get_location().towards(map_location, MOVE_SIZE*turns)
    return previous_locations[pirate.unique_id].towards(pirate.get_location(), MOVE_SIZE*(turns+1))


def get_all_map_locations(game):
    l = game.get_living_asteroids() + game.get_all_capsules() + game.get_my_living_pirates() + game.get_enemy_living_pirates() + game.get_all_motherships()
    return [i.get_location() for i in l]


def update_globals(game):
    '''Should be run on the first round of the game.'''
    p0 = game.get_my_living_pirates()[0]
    global CAPSULE_PICKUP_RANGE; CAPSULE_PICKUP_RANGE = game.capsule_pickup_range
    global CAPSULE_SPAWN_TURNS; CAPSULE_SPAWN_TURNS = game.capsule_spawn_turns
    global MAP_SIZE; MAP_SIZE = game.cols
    global MAX_POINTS; MAX_POINTS = game.max_points
    global TURNS; TURNS = game.max_turns
    global MOTHERSHIP_UNLOAD_RANGE; MOTHERSHIP_UNLOAD_RANGE = game.mothership_unload_range
    global NUM_PUSHES_FOR_CAPSULE_LOSS; NUM_PUSHES_FOR_CAPSULE_LOSS = game.num_pushes_for_capsule_loss
    global PIRATE_MAX_SPEED; PIRATE_MAX_SPEED = game.pirate_max_speed
    global PIRATE_SPAWN_TURNS; PIRATE_SPAWN_TURNS = game.pirate_spawn_turns
    global PUSH_DISTANCE; PUSH_DISTANCE = game.push_distance
    global PUSH_COOLDOWN; PUSH_COOLDOWN = game.push_max_reload_turns
    global PUSH_RANGE; PUSH_RANGE = game.push_range


def dbg(msg, game):
    DEBUG and game.debug(msg)  # builtin


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


# ---------------------------------------------------- SMARTP ------------------------------------------------


class SmartPirate(object):
    def __init__(self, pirate, game, index):
        self.p = pirate
        self.g = game
        self.i = index

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
        index = self.i
        p = self.p

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
            self.p.sail(closest_wall(self.p))
            return

        if sort_by_distance_from(my_capsules, self.p)[0].holder is not None:  # if we have the capsule
            if sort_by_distance_from(my_capsules, self.p)[0].holder == self.p:
                self.p.sail(sort_by_distance_from(my_motherships, self.p)[0])
            else:
                self.p.sail(expected_location(my_capsules[0].holder, turns=2))
        else:
            self.p.sail(sort_by_distance_from(my_capsules, self.p)[0])

        # TODO much more


def do_turn(game):
    global previous_locations, current_locations, movement_vectors, GAME
    GAME = game

    #justgamestartthings
    if game.turn == 1:
        update_globals(game)
        previous_locations = {}
        current_locations = {}
        movement_vectors = {}

    # update directions
    update_locations(game)

    # Might seem stupid, but this way every pirate knows every other pirate's index.
    smart_pirates = []
    for index, my_pirate in enumerate(game.get_my_living_pirates(), start=1):
        smart_pirates.append(SmartPirate(my_pirate, game, index))
    for sp in smart_pirates:
        sp.operate()
