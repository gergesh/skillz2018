def advanced_push(my_ships, team_capsule_holder, enemies, enemy_capsule_holder, enemy_mothership):
    push_together_threshold = 100
    ships_not_assigned = my_ships
    move_threshold = 4
    closest_to_capsule_holder = sorted(ships_not_assigned, key=lambda d: d.distance(enemy_capsule_holder))
    if closest_to_capsule_holder[1].can_push(enemy_capsule_holder):
        closest_to_capsule_holder[0].push(enemy_capsule_holder, enemy_mothership.get_location())
        closest_to_capsule_holder[1].push(enemy_capsule_holder, enemy_mothership.get_location())
        ships_not_assigned.remove(closest_to_capsule_holder[0])
        ships_not_assigned.remove(closest_to_capsule_holder[1])
        ships_not_assigned.remove(team_capsule_holder)
    else:
        ships_not_assigned.remove(team_capsule_holder)
        closest_to_capsule_holder.remove(team_capsule_holder)
        if can_be_there(closest_to_capsule_holder[1], expected_location(enemy_capsule_holder, move_threshold),
                        move_threshold) and can_be_there(closest_to_capsule_holder[0],
                                                         expected_location(enemy_capsule_holder, move_threshold),
                                                         move_threshold):
            closest_to_capsule_holder[1].sail(enemy_capsule_holder)
            closest_to_capsule_holder[0].sail(enemy_capsule_holder)
            ships_not_assigned.remove(closest_to_capsule_holder[1])
            ships_not_assigned.remove(closest_to_capsule_holder[0])

    # TODO: make all other ships left push other enemy ships
    


def can_be_there(ship, location, num_of_turns):
    if ship.get_location().distance(location) < num_of_turns * MOVE_DISTANCE:
        return True
    return False
