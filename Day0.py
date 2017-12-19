from pirates import *
from advancedpush import *

# CONSTANTS
PICKUP_RANGE = 200
PUSH_DISTANCE = 600
MOVE_SIZE = 200
MAP_SIZE = 6400

# BETAH ATA GLOBAL
my_capsule = None
enemy_capsule = None
my_mothership = None
enemy_mothership = None
my_living_pirates = None
enemy_living_pirates = None

prevlocs = {}
directions = {}

def enemy_assignments(enemies, enemy_mothership, my_mothership, enemy_capsule, my_capsule):
    num_of_enemy_gatherers = 0
    num_of_enemy_attackers = 0
    for enemy in enemies:
        gather_distance = enemy.distance(enemy_mothership) + enemy.distance(enemy_capsule.initial_location)
        attack_distance = enemy.distance(my_mothership) + enemy.distance(my_capsule.initial_location)
        if gather_distance > attack_distance:
            num_of_enemy_attackers += 1
        else:
            num_of_enemy_gatherers += 1
    return num_of_enemy_gatherers, num_of_enemy_attackers

def expected_location(pirate, num_of_turns = 1):
    """Receives a pirate, returns its expected location in the next turn."""
    global directions
    return pirate.get_location().towards(pirate.get_location().add(directions[pirate.unique_id]), num_of_turns*MOVE_SIZE)


def update_directions(pirates):
    global directions, prevlocs
    for pirate in pirates:
        if pirate.unique_id in prevlocs:
            directions[pirate.unique_id] = pirate.get_location().subtract(prevlocs[pirate.unique_id])
            prevlocs[pirate.unique_id] = pirate.get_location()
        else:
            directions[pirate.unique_id] = Location(0, 0)
            prevlocs[pirate.unique_id] = pirate.get_location()

def should_push_to(enemy_pirate):  # TODO probably incorrect calculations.
    """Gets an enemy pirate, returns location you should push it to."""
    # if there's no escape for him, we won't take risks with expected location.
    if not enemy_pirate.location.towards(closest_wall(enemy_pirate.location), PUSH_DISTANCE - 200).in_map:
        return closest_wall(enemy_pirate.location)
    # if we expect him to be in a place where we can take him out, let's do so.
    elif not expected_location(enemy_pirate).towards(closest_wall(expected_location(enemy_pirate)), PUSH_DISTANCE).in_map:
        # if you can knock him out, do it
        return closest_wall(expected_location(enemy_pirate))
    elif enemy_pirate.capsule is not None:
        # if he's holding a capsule, turn him away from his base
        return expected_location(enemy_pirate).subtract(enemy_mothership.location)
    else:
        # we'll just foil his plans # TODO this doesn't work as intended, need some physicist
        return previous_locations[enemy_pirate.unique_id].subtract(enemy_pirate.location)

# SHITTY FUNCTION
def should_push_out(enemy_pirates):
    for ep in enemy_pirates:
        enemy_end_location = expected_location(ep).towards(closest_wall(ep), PUSH_DISTANCE)
        #                    expected location in next turn, 200 steps towards the closest wall
        if not enemy_end_location.in_map:
            return ep
    return None


def attack(ship):
    """Instruct ship to perform attacking moves."""
    if enemy_capsule.holder is None:
        ship.sail(enemy_mothership.get_location())
    else:
        ship.sail(expected_location(enemy_capsule.holder, enemy_capsule.holder.distance(enemy_mothership.get_location())/350))
    '''
    if enemy_capsule.holder is None:
        # if ship.distance(PirateGame.get_enemy_capsule.initial_location)>1200:
        has_pushed = False
        closest_enemies_to_mine = sort_by_distance_from(enemy_living_pirates, enemy_capsule.initial_location)
        for i in closest_enemies_to_mine:
            if ship.can_push(i):
                push_away_from_mothership(ship, i)
                has_pushed = True
                break
        if not has_pushed:
            ship.sail(enemy_mothership.get_location())
    else:
        if ship.can_push(enemy_capsule.holder):
            push_away_from_mothership(ship, enemy_capsule.holder)
        else:
            ship.sail(enemy_capsule.holder)
    '''

def push_away_from_mine(ship, enemy):
    enemy_mine = enemy_capsule.initial_location
    enemy_mine_vector = enemy.location.subtract(enemy_mine)
    ship.push(enemy, enemy.location.towards(enemy_mine_vector, PUSH_DISTANCE))


def push_away_from_mothership(my_pirate, enemy_pirate):
    mothership = enemy_mothership.location
    enemy_mothership_vector = enemy_pirate.location.subtract(mothership)
    my_pirate.push(enemy_pirate, enemy_pirate.location.towards(enemy_mothership_vector, PUSH_DISTANCE))

'''
def closest_wall(obj):
    """Gets either a GameObject or a location, returns Location of nearest wall"""
    if isinstance(obj, Location):
        x = obj.row
        y = obj.col
    else:
        x = obj.location.row
        y = obj.location.col
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
'''

def camp(ship):
    # for ship in ships:
    if ship.location.distance(enemy_capsule.initial_location) > 0:
        ship.sail(enemy_capsule.initial_location)


def retrieve(retrievers):
    need_to_act = list(retrievers)
    if my_capsule.holder is None:
        if len(retrievers)>0:
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
    
            if len(retrievers) > 2:
                last_pirate = sort_by_distance_from(need_to_act, my_closest_pirate.location)[-1]
                last_pirate.sail(my_capsule.initial_location.towards(my_mothership.location, PICKUP_RANGE - 1))
                    # move the closest I can to my base that will also let me pick up the capsule
            

    else:
        my_capsule.holder.sail(my_mothership.location)
        need_to_act.remove(my_capsule.holder)
        # TODO else - protect himself
        for my_pirate in sort_by_distance_from(need_to_act, my_capsule.holder.location)[0:len(need_to_act)/2]:
            my_pirate.sail(my_capsule.holder.location.towards(my_mothership.location, 200))
            need_to_act.remove(my_pirate)
        
        camper_pirates = sort_by_distance_from(need_to_act, my_capsule.holder)[len(need_to_act)/2:len(need_to_act)]

        for camper in camper_pirates:
            if camper.location.distance(my_capsule.initial_location) > PICKUP_RANGE:
                camper.sail(my_capsule.initial_location)



# ---------------------------------------END BEN --------------------------------


def threatened_by(pirate):
    """Gets a pirate, returns a list of threats."""
    return sort_by_distance_from([i for i in enemy_living_pirates if i.can_push(pirate)], pirate.get_location())


def sort_by_distance_from(objects, place):
    place = place.get_location()
    return sorted(objects, key=lambda o: place.distance(o.get_location()))


def do_turn(game):
    # main functions right now are attack, camp and retrieve
    global my_capsule, enemy_capsule, my_mothership, enemy_mothership, my_living_pirates, enemy_living_pirates
    my_capsule = PirateGame.get_my_capsule(game)
    enemy_capsule = PirateGame.get_enemy_capsule(game)
    my_mothership = PirateGame.get_my_mothership(game)
    enemy_mothership = PirateGame.get_enemy_mothership(game)
    my_living_pirates = PirateGame.get_my_living_pirates(game)
    enemy_living_pirates = PirateGame.get_enemy_living_pirates(game)
    
    update_directions(enemy_living_pirates)
    
    num_of_enemy_gatherers, num_of_enemy_attackers = enemy_assignments(enemy_living_pirates, enemy_mothership, my_mothership, enemy_capsule, my_capsule)

    num_of_my_gatherers = (len(my_living_pirates)*num_of_enemy_attackers)/(num_of_enemy_attackers+num_of_enemy_gatherers)
    num_of_my_attackers = len(my_living_pirates) - num_of_my_gatherers

    need_to_act = advanced_push(game.get_my_living_pirates(), game.get_my_capsule().holder, game.get_enemy_living_pirates(), game.get_enemy_capsule().holder, game.get_enemy_mothership(), directions)

    gather_location = my_capsule.get_location().add(my_mothership.get_location()).multiply(0.5)
    
    all_yoavs_ships = sort_by_distance_from(my_living_pirates, gather_location)[0:num_of_my_gatherers]
    if my_capsule.holder is not None:
        all_yoavs_ships = list(set(all_yoavs_ships + [my_capsule.holder]))
    yoavs_ships = [ship for ship in all_yoavs_ships if ship in need_to_act]
    retrieve(yoavs_ships)
    
    bens_ships = sort_by_distance_from(my_living_pirates, gather_location)[num_of_my_gatherers:num_of_my_gatherers+num_of_my_attackers]

    for attacker in sorted(bens_ships, key = lambda p: p.unique_id)[0:num_of_my_attackers/2]:
        if attacker in need_to_act:
            attack(attacker)
        # TODO other pirates
    for camper in sorted(bens_ships, key = lambda p: p.unique_id)[num_of_my_attackers/2:num_of_my_attackers]:
        if camper in need_to_act:
            camp(camper)

# TODO we have two groups of campers, we should *really* find a better name for them
