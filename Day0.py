from pirates import *

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


def expected_location(pirate):
    """Receives a pirate, returns its expected location in the next turn."""
    return pirate.location.towards(directions[pirate.id], MOVE_SIZE)


def update_directions(pirates=enemy_living_pirates, d={}, prevlocs={}):
    """A dictionary of locations, (dx, dy) in last turn"""
    for pirate in pirates:
        if pirate.id in prevlocs:
            d[pirate.id] = pirate.location.substract(prevlocs[pirate.id])
            prevlocs[pirate.id] = pirate.location
        else:
            d[pirate.id] = Location(0, 0)
            prevlocs[pirate.id] = pirate.location
    return d, prevlocs


def should_push_to(enemy_pirate):  # TODO probably incorrect calculations.
    """Gets an enemy pirate, returns location you should push it to."""
    if not expected_location(enemy_pirate).towards(closest_wall(expected_location(enemy_pirate)), PUSH_DISTANCE).in_map:
        # if you can knock him out, do it
        return closest_wall(expected_location(enemy_pirate))
    elif enemy_pirate.capsule is not None:
        # if he's holding a capsule, turn him away from his base
        return expected_location(enemy_pirate).subtract(enemy_mothership.location)
    else:
        # we'll just foil his plans
        return previous_locations[enemy_pirate.id].substract()

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
        # if ship.distance(PirateGame.get_enemy_capsule.initial_location)>1200:
        has_pushed = False
        closest_enemies_to_mine = sort_by_distance_from(enemy_living_pirates, enemy_capsule.initial_location)
        for i in closest_enemies_to_mine:
            if ship.can_push(i):
                push_away_from_mothership(ship, i)
                has_pushed = True
                break
        if not has_pushed:
            ship.sail(enemy_capsule.initial_location)
    else:
        if ship.can_push(enemy_capsule.holder):
            push_away_from_mothership(ship, enemy_capsule.holder)
        else:
            ship.sail(enemy_capsule.holder)


def push_away_from_mine(ship, enemy):
    enemy_mine = enemy_capsule.initial_location
    enemy_mine_vector = enemy.location.subtract(enemy_mine)
    ship.push(enemy, enemy.location.towards(enemy_mine_vector, PUSH_DISTANCE))


def push_away_from_mothership(my_pirate, enemy_pirate):
    mothership = enemy_mothership.location
    enemy_mothership_vector = enemy_pirate.location.subtract(mothership)
    my_pirate.push(enemy_pirate, enemy_pirate.location.towards(enemy_mothership_vector, PUSH_DISTANCE))


def closest_wall(obj):
    """Gets either a GameObject or a location, returns Location of nearest wall"""
    if isinstance(obj, Location):
        x = obj.row
        y = obj.col
    else:
        x = obj.location().row
        y = obj.location().col
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


def camp(ship):
    # for ship in ships:
    if ship.location.distance(enemy_capsule.initial_location) > PICKUP_RANGE:
        ship.sail(enemy_capsule.initial_location)
    else:
        to_push = sort_by_distance_from(ship, enemy_living_pirates)[0]
        if ship.can_push(to_push):
            ship.push(to_push, closest_wall(to_push))


# ---------------------------------------END BEN --------------------------------


def threatened_by(pirate):
    """Gets a pirate, returns None if nobody is threatening him, a list of threats if there are."""
    threats = [i for i in enemy_living_pirates if i.can_push(pirate)]
    if len(threats) == 0:
        return None
    else:
        return sort_by_distance_from(threats, pirate.location)


def sort_by_distance_from(objects, location):
    if isinstance(location, GameObject):
        location = GameObject.location
    return sorted(objects, key=lambda o: location.distance(o.location))


def do_turn(game):
    global my_capsule, enemy_capsule, my_mothership, enemy_mothership, my_living_pirates, enemy_living_pirates
    my_capsule = PirateGame.get_my_capsule(game)
    enemy_capsule = PirateGame.get_enemy_capsule(game)
    my_mothership = PirateGame.get_my_mothership(game)
    enemy_mothership = PirateGame.get_enemy_mothership(game)
    my_living_pirates = PirateGame.get_my_living_pirates(game)
    enemy_living_pirates = PirateGame.get_enemy_living_pirates(game)

    global directions, previous_locations
    directions, previous_locations = update_directions(enemy_living_pirates)

    if my_capsule.holder is None:
        enemies_to_push = []
        # if none of our pirates have our capsule
        my_closest_pirate = sort_by_distance_from(my_living_pirates, my_capsule.location)[0]
        my_closest_pirate.sail(my_capsule.location)
        for my_pirate in sort_by_distance_from(my_living_pirates, my_closest_pirate.location)[1:3]:
            threat = threatened_by(my_pirate)[0]
            if threat is None:
                my_pirate.sail(my_closest_pirate.location)
            else:
                my_pirate.push(threat, closest_wall(threat))

        if len(retrievers) > 2:
            last_pirate = sort_by_distance_from(my_living_pirates, my_closest_pirate.location)[-1]
            if threatened_by(last_pirate) is not None:
                last_pirate.push(threatened_by(last_pirate))
            elif last_pirate.location.distance(my_capsule.initial_location) > PICKUP_RANGE:
                last_pirate.sail(my_capsule.initial_location.towards(my_mothership.location, PICKUP_RANGE - 1))
                # move the closest I can to my base that will also let me pick up the capsule
        # TODO else - protect himself

        for attacker in sort_by_distance_from(my_living_pirates, my_capsule.initial_location)[4:6]:
            attack(attacker)
            # TODO other pirates
        for camper in sort_by_distance_from(my_living_pirates, my_capsule.initial_location)[6:8]:
            camp(camper)

    else:
        # if we have the capsule
        my_capsule.holder.sail(my_mothership.location)
        enemies_to_push = []

        for my_pirate in sort_by_distance_from(my_living_pirates, my_capsule.holder.location)[1:2]:
            threat = threatened_by(my_pirate)[0]
            if threat is None:
                my_pirate.sail(my_capsule.holder.location.towards(my_mothership.location, 200))
            else:
                my_pirate.push(threat, closest_wall(threat))
        camper_pirates = sort_by_distance_from(my_living_pirates, my_capsule.holder)[2:4]

        for camper in camper_pirates:
            if camper.location.distance(my_capsule.initial_location) > PICKUP_RANGE:
                camper.sail(my_capsule.initial_location)
            else:
                camper.sail(camper.location.add(Location(1, 0)))

        # TODO protect himself

        for attacker in sort_by_distance_from(my_living_pirates, my_capsule.holder.location)[4:6]:
            attack(attacker)
            # TODO other pirates
        for camper in sort_by_distance_from(my_living_pirates, my_capsule.holder.location)[6:8]:
            camp(camper)

# TODO we have two groups of campers, we should *really* find a better name for them
