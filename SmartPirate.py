import math

class SmartPirate(Pirate):
    def smart_sail(self, locations_and_weights, destination):
        '''Receives a list of tuples, each containing a location and its weight.'''

        moves = round(self.get_location().distance(destination.get_location())/MOVE_SIZE) + 1
        _, best_destination = get_path_cost(self.get_location(), locations_and_weights, destination, moves)

        def get_path_cost(self, locations_and_weights, destination, available_moves):
            if available_moves == 0:
                return 99999999, None # inf
            else:
                cost_of_move = 0
                for loc in locations_and_weights:
                    cost_of_move += self.get_location().distance(loc[0]) * loc[1]

                if self.get_location().distance(destination.getlcoation) < MOVE_SIZE:
                    return cost_of_move, destination.getlcoation
                else:
                    side_destinations = []
                    number_of_possibilities = 8
                    for i in range(number_of_possibilities):
                        angle = i/number_of_possibilities*2*math.pi
                        x = int(math.cos(angle)*10000)
                        y = int(math.sin(angle)*10000)
                        side_destinations.append(self.get_location().towards(Location(x,y), MOVE_SIZE))

                    costs = []
                    for i in range(number_of_possibilities):
                        costs.append(get_path_cost(side_destinations[i], locations_and_weights, destination, available_moves-1))

                    minimum = min([cost[0] for cost in costs])


                    for cost in costs:
                        if cost[0] == minimum:
                            minimum_loc = cost[1]
                            break

                    return cost_of_move + minimum, minimum_loc

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


def do_turn(game):
    if my_capsule.holder is None:
