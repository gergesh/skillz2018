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