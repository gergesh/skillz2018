from pirates import *
from utils import *
util = Utils()

class Action(object):
    def __init__(self, game, pirate, target):
        self.game = game
        self.pirate = pirate
        self.target = target
    
    def cost(self):
        return distance_and_difficulty(self)
    
    def distance_and_difficulty(self):
        loc = self.pirate.get_location()
        cost = 0
        turn = 0
        while loc != target:
            cost += sum(lw[1]/(loc.distance(lw[0])+1)**THREAT_DECAY_RATE for lw in util.generate_weights(loc, turn))
            cost += sum(lw[1]/(loc.distance(lw[0])+1)**THREAT_DECAY_RATE for lw in util.generate_weights(loc, 0))
            # twice, both for the ones there and the ones that may be there.
            loc += self.pirate.max_speed
            turn += 1
        cost += sum(lw[1]/(loc.distance(lw[0])+1)**THREAT_DECAY_RATE for lw in util.generate_weights(loc, turn))
        return cost

    def distance_score(self):
        return self.pirate.get_location().distance(target.get_location())

class FetchCapsule(Action):
    pass
