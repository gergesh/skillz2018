from pirates import *
from MyBot import *
import math
PUSH_RANGE = 200
PUSH_DISTANCE = 600
MOVE_SIZE = 200
MAP_SIZE = 6400

def advanced_push(my_ships, team_capsule_holder, enemies, enemy_capsule_holder, enemy_mothership, directions):
    global glob_directions
    glob_directions = directions
    push_together_threshold = 100
    ships_not_assigned = list(my_ships)
    enemy_ships_not_pushed = enemies
    move_threshold = 3
    if enemy_capsule_holder is not None:
        closest_to_capsule_holder = sorted(ships_not_assigned, key=lambda d: d.distance(enemy_capsule_holder))
        if closest_to_capsule_holder[1].can_push(enemy_capsule_holder) and closest_to_capsule_holder[0].can_push(enemy_capsule_holder):
            (required_ships, can_push_out, push_location) = can_be_pushed_to_wall(enemy_capsule_holder, 2)
            if can_push_out:
                closest_to_capsule_holder[0].push(enemy_capsule_holder, push_location)
                closest_to_capsule_holder[1].push(enemy_capsule_holder, push_location)
            else:
                closest_to_capsule_holder[0].push(enemy_capsule_holder, enemy_mothership.get_location())
                closest_to_capsule_holder[1].push(enemy_capsule_holder, enemy_mothership.get_location())
            ships_not_assigned.remove(closest_to_capsule_holder[0])
            ships_not_assigned.remove(closest_to_capsule_holder[1])
            if team_capsule_holder in ships_not_assigned: ships_not_assigned.remove(team_capsule_holder)
            if enemy_capsule_holder in enemy_ships_not_pushed: enemy_ships_not_pushed.remove(enemy_capsule_holder)
        else:
            if team_capsule_holder in ships_not_assigned: ships_not_assigned.remove(team_capsule_holder)
            if team_capsule_holder in closest_to_capsule_holder: closest_to_capsule_holder.remove(team_capsule_holder)
            if can_be_near_location(closest_to_capsule_holder[1], expected_location(enemy_capsule_holder, glob_directions, move_threshold),
                                  move_threshold) and can_be_near_location(closest_to_capsule_holder[0],
                                                                         expected_location(enemy_capsule_holder, glob_directions,
                                                                                           move_threshold),
                                                                         move_threshold):
                closest_to_capsule_holder[1].sail(enemy_capsule_holder)
                closest_to_capsule_holder[0].sail(enemy_capsule_holder)
                #print "advanced push sailed"
                ships_not_assigned.remove(closest_to_capsule_holder[1])
                ships_not_assigned.remove(closest_to_capsule_holder[0])

    # TODO: make all other ships left push other enemy ships in a smart manner
    if team_capsule_holder in ships_not_assigned: ships_not_assigned.remove(team_capsule_holder)
    for ship in ships_not_assigned:
        for enemy in enemy_ships_not_pushed:
            if ship.can_push(enemy):
                closest_ships = sorted(ships_not_assigned, key = lambda d: d.distance(enemy))
                ships_that_can_help = [ship]
                for close_ship in closest_ships:
                    if close_ship.can_push(enemy):
                        ships_that_can_help += [close_ship]
                (required_ships, _, the_wall) = can_be_pushed_to_wall(enemy) #oh yeah G.O.T
                if required_ships>len(ships_that_can_help):
                    backwards_direction = enemy.get_location().add(enemy.get_location().subtract(expected_location(enemy, glob_directions)).multiply(1000))
                    ship.push(enemy, enemy.get_location().add(backwards_direction))
                    ships_not_assigned.remove(ship)
                else:
                    print "we can push the enemy out, hooray!!!"
                    for i in range(required_ships):
                        closest_ships[i].push(enemy, the_wall)
                        ships_not_assigned.remove(closest_ships[i])
                    enemy_ships_not_pushed.remove(enemy)
    
    return ships_not_assigned
    
def can_be_near_location(ship, location, num_of_turns):
    if ship.get_location().distance(location) < num_of_turns * MOVE_SIZE - PUSH_RANGE:
        return True
    return False


def closest_wall(obj):
    """Gets either a GameObject or a location, returns Location of nearest wall"""
    x = obj.get_location().row
    y = obj.get_location().col

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
def get_location(obj):
    # gets anything, returns its location
    if type(obj) == type(Location(0,0)):
        return obj
    else:
        return obj.get_location()
'''

def can_be_pushed_to_wall(enemy, num_of_ships_pushing=1):
    required_ships = int(expected_location(enemy, glob_directions).distance(closest_wall(expected_location(enemy, glob_directions)))/float(PUSH_DISTANCE)+1)
    if expected_location(enemy, glob_directions).distance(closest_wall(expected_location(enemy, glob_directions))) < num_of_ships_pushing * PUSH_DISTANCE:
        return required_ships, True, closest_wall(expected_location(enemy, glob_directions))
    return required_ships, False, closest_wall(expected_location(enemy, glob_directions))
