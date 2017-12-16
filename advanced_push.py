def advanced_push(my_ships, team_capsule_holder, enemies, enemy_capsule_holder, enemy_mothership):
    push_together_threshold = 100
    ships_not_assigned = my_ships
    enemy_ships_not_pushed = enemies
    move_threshold = 3
    closest_to_capsule_holder = sorted(ships_not_assigned, key=lambda d: d.distance(enemy_capsule_holder))
    if closest_to_capsule_holder[1].can_push(enemy_capsule_holder):
        (can_push_out, push_location) = can_be_pushed_to_wall(enemy_capsule_holder, 2)
        if can_push_out:
            closest_to_capsule_holder[0].push(enemy_capsule_holder, push_location)
            closest_to_capsule_holder[1].push(enemy_capsule_holder, push_location)
        else:
            closest_to_capsule_holder[0].push(enemy_capsule_holder, enemy_mothership.get_location())
            closest_to_capsule_holder[1].push(enemy_capsule_holder, enemy_mothership.get_location())
        ships_not_assigned.remove(closest_to_capsule_holder[0])
        ships_not_assigned.remove(closest_to_capsule_holder[1])
        ships_not_assigned.remove(team_capsule_holder)
        enemy_ships_not_pushed.remove(enemy_capsule_holder)
    else:
        ships_not_assigned.remove(team_capsule_holder)
        closest_to_capsule_holder.remove(team_capsule_holder)
        if can_be_at_location(closest_to_capsule_holder[1], expected_location(enemy_capsule_holder, move_threshold),
                              move_threshold) and can_be_at_location(closest_to_capsule_holder[0],
                                                                     expected_location(enemy_capsule_holder,
                                                                                       move_threshold),
                                                                     move_threshold):
            closest_to_capsule_holder[1].sail(enemy_capsule_holder)
            closest_to_capsule_holder[0].sail(enemy_capsule_holder)
            ships_not_assigned.remove(closest_to_capsule_holder[1])
            ships_not_assigned.remove(closest_to_capsule_holder[0])

    # TODO: make all other ships left push other enemy ships in a smart manner
    for ship in ships_not_assigned:
        for enemy in enemy_ships_not_pushed:
            if ship.can_push(enemy):
                backwards_direction = enemy.get_location().add(multiply_location_vector(enemy.get_location().subtract(expected_location(enemy)), 100 ))
                ship.push(enemy, backwards_direction)
                enemy_ships_not_pushed.remove(enemy)

def can_be_at_location(ship, location, num_of_turns):
    if ship.get_location().distance(location) < num_of_turns * MOVE_DISTANCE:
        return True
    return False


def closest_wall(obj):
    """Gets either a GameObject or a location, returns Location of nearest wall"""
    x = get_location(obj).row
    y = get_location(obj).col

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


def get_location(obj):
    # gets anything, returns its location
    if isinstance(obj, Location):
        return obj
    else:
        return obj.get_lcoation()


def can_be_pushed_to_wall(enemy, num_of_ships_pushing=1):
    if expected_location(enemy).distance(closest_wall(expected_location(enemy))) < num_of_ships_pushing * PUSH_DISTANCE:
        return True, closest_wall(expected_location(enemy))
    return False, None

def multiply_location_vector(vector, multiplier):
    return Location(vector.row*multiplier, vector.col*multiplier)
