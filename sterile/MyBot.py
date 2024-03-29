from pirates import *
import math


# CONSTANTS
# See https://piratez.skillz-edu.org/static/c785238d5a9dbb1feea8f1b057b06393958cfe2ff34c8ee820d7bb2df4a2bc33/environment/docs/Python/PirateGame.html#capsule_pickup_range
CAPSULE_PICKUP_RANGE = None
CAPSULE_SPAWN_TURNS = None
MAP_SIZE = None
MAX_POINTS = None
TURNS = None
MOTHERSHIP_UNLOAD_RANGE = None
NUM_PUSHES_FOR_CAPSULE_LOSS = None
PIRATE_MAX_SPEED = None
PIRATE_SPAWN_TURNS = None
PUSH_DISTANCE = None
PUSH_COOLDOWN = None
PUSH_RANGE = None
MOVE_SIZE = None

POINTS_LOSE_SUICIDE_THRESHOLD = None
TIME_LOSE_SUICIDE_POINT_THRESHOLD = None
TIME_LOSE_SUICIDE_THRESHOLD = None

THREAT_DECAY_RATE = 1

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
            previous_locations[i.unique_id] = i.get_location()
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
    global MOVE_SIZE; MOVE_SIZE = game.pirate_max_speed
    
    global POINTS_LOSE_SUICIDE_THRESHOLD; POINTS_LOSE_SUICIDE_THRESHOLD = int(0.8 * MAX_POINTS)  # 6
    global TIME_LOSE_SUICIDE_POINT_THRESHOLD; TIME_LOSE_SUICIDE_POINT_THRESHOLD = int(0.4 * TURNS)
    global TIME_LOSE_SUICIDE_THRESHOLD; TIME_LOSE_SUICIDE_THRESHOLD = int(0.8 * TURNS)


def dbg(msg):
    DEBUG and GAME.debug(msg)  # builtin


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


def generate_weights(loc, turn=0):
    DANGER_MULTIPLIERS = {
        'Pirate': 10**8.0,
        'Asteroid': 10**8.0,
        'Wall': 10**7.0
    }
    fears = GAME.get_enemy_living_pirates() + GAME.get_living_asteroids()
    #locations += [expected_location(i) for i in locations]
    locations_and_weights = [(expected_location(f, turn), DANGER_MULTIPLIERS[type(f).__name__]) for f in fears]
    locations_and_weights.append((closest_wall(loc), DANGER_MULTIPLIERS['Wall']))
    return locations_and_weights
    
def closest(loc, items):
    return sort_by_distance_from(items, loc.get_location())[0]


# ---------------------------------------------------- SMARTP ------------------------------------------------


class SmartPirate(object):
    def __init__(self, pirate, game, index):
        self.p = pirate
        self.g = game
        self.i = index

    def smart_sail(self, destination):
        '''
        Receives either a single destination or a list of possible ones, sails towards the best one.
        Written by Yoav Shai.
        '''
        
        def move_value(origin, dest, goal, locs_and_weights, IMPORTANCE_OF_GETTING_THERE=5000):
            advancement = origin.distance(goal) - dest.distance(goal)
            dangers_in_new_place = 0
            for lw in locs_and_weights:
                dangers_in_new_place += lw[1]/(dest.distance(lw[0])+1)**THREAT_DECAY_RATE
            # TODO find a better calculation method using the same principles
            return advancement*IMPORTANCE_OF_GETTING_THERE - dangers_in_new_place
        
        def sub_locations(origin, dest, OPTIONS=8, ANGLE_THRESHOLD=math.pi/2, move_sizes=[MOVE_SIZE, MOVE_SIZE/2]):
            dest_vector = dest.subtract(origin)
            dest_angle = math.atan2(dest_vector.get_location().col, dest_vector.get_location().row)
            
            subs = [origin] # we can stay put
            for angle in [float(i)/OPTIONS*2*math.pi for i in xrange(OPTIONS)] + [dest_angle]:
                diff = abs((angle+2*math.pi)%(2*math.pi)-(dest_angle+2*math.pi)%(2*math.pi))
                if diff < ANGLE_THRESHOLD:
                    for move_size in move_sizes:
                        subs.append(origin.towards(origin.add(Location(1000*math.cos(angle), 1000*math.sin(angle))), move_size))
            #print subs
            return subs
        
        def best_move(origin, dest, path=[], value=0, rec_level=2):
            if rec_level == 0:
                return path, value
            sub_locs = sub_locations(origin, dest)
            
            return max([best_move(subl, dest, path + [subl], value+move_value(origin, subl, dest, generate_weights(subl, len(path)+1)), rec_level-1) for subl in sub_locs], key=lambda x: x[1])
            
        if isinstance(destination, list):
            # find the best destination using simulations
            dests_and_diffs = []
            for possible_target in destination:
                possible_target = possible_target.get_location()
                loc = self.p.get_location()
                difficulty = 0
                turn = 0
                while loc != possible_target:
                    loc = loc.towards(possible_target, self.p.max_speed)
                    difficulty += sum(lw[1]/(loc.distance(lw[0])+1)**THREAT_DECAY_RATE for lw in generate_weights(loc, turn))
                    difficulty += sum(lw[1]/(loc.distance(lw[0])+1)**THREAT_DECAY_RATE for lw in generate_weights(loc, 0))
                    # adding twice, both for the ones that will be there and the ones already there
                    turn += 1
                difficulty += turn*300 # TODO smarter way or a better value
                dests_and_diffs.append((possible_target, difficulty))
            destination = min(dests_and_diffs, key=lambda x: x[1])[0]
            
        route, value = best_move(origin=self.p.get_location(), dest=destination.get_location())
        #print value
        self.p.sail(route[0])
        
        
    def threats(self, turns_forward=3, rad=200):
        '''Returns a list of threats, sorted by most to least critical/feasible.'''
        global movement_vectors
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
        my_mines = [c.initial_location for c in my_capsules]
        enemy_mines = [c.initial_location for c in enemy_capsules]
        asteroids = game.get_living_asteroids()
        

        # first of all - if we're gonna lose, let's try to make them crash. Perhaps they're dumb.
        if game.get_myself().score + POINTS_LOSE_SUICIDE_THRESHOLD <= game.get_enemy().score or (
                game.turn > TIME_LOSE_SUICIDE_THRESHOLD and game.get_myself().score + TIME_LOSE_SUICIDE_POINT_THRESHOLD <= game.get_enemy().score):
            self.p.sail(closest_wall(self.p))
            return
        print len(my_capsules)
        if len(my_capsules) == 0: # one man army
            if len(enemy_pirates) == 1:
                if self.p.can_push(enemy_pirates[0]):
                    self.p.push(enemy_pirates[0], closest_wall(enemy_pirates[0]))
            else:
                for ep in enemy_pirates:
                    if ep.capsule is not None and self.p.can_push(ep):
                        self.p.push(ep, closest_wall(ep))
            return
                
        if self.p.capsule is not None:
            # if I have a capsule
            threats = self.threats(turns_forward=0, rad=PUSH_RANGE)
            if len(threats) == 0:
                self.smart_sail(my_motherships)
            else:
                for t in threats:
                    if self.p.can_push(t):
                        self.p.push(t, closest_wall(t))
                        return
                else:
                    self.smart_sail(my_motherships)
            return
        # if I don't have a capsule
        closest_capsule = closest(self.p, my_capsules)
        index_from_capsule = sort_by_distance_from(my_pirates, closest_capsule).index(self.p)
        if index_from_capsule == 0:
            self.smart_sail(closest_capsule)
        elif index_from_capsule > len(my_pirates)/2:
            if closest(self.p, enemy_capsules).holder is not None:
                # if their capsule has a holder
                self.smart_sail(closest(self.p, enemy_capsules))
            else:
                self.smart_sail(closest(self.p, enemy_mines))
        else:
            self.smart_sail(closest(self.p, my_capsules))
        return            
        '''
        if sort_by_distance_from(my_capsules, self.p)[0].holder is not None:  # if we have the capsule
            if sort_by_distance_from(my_capsules, self.p)[0].holder == self.p:
                self.smart_sail(my_motherships)
            else:
                self.smart_sail(expected_location(my_capsules[0].holder))
        else:
            self.smart_sail(my_capsules)

        for ep in enemy_pirates:
            if ep.capsule is not None and self.p.can_push(ep):
                self.p.push(ep, closest_wall(ep))
        '''
        # TODO much more
        
        
    def retrieve(self):
        pass
    
    
    def wait_for_capsules(self):
        if len(self.g.get_my_capsules()) == 1:
            self.smart_sail(self.g.get_my_capsules()[0].initial_location)
        else:
            self.smart_sail(self.g.get_my_capsules()[0].initial_location)
            pass
            #TODO: make the ship pick the best capsule location
        pass
    
    
    def sabotage_enemy_retreiving(self):
        pass
    
    
    def sabotage_enemy_waiting(self):
        pass
        
        

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
    
