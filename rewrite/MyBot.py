from pirates import *
from utils import *
util = Utils()

class Action(object):
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
    
    def get_possible_actions(game):
        pass

    def get_participants(self):
        pass

class FetchCapsule(Action):
    def __init__(self, g, p, c):
        self.game = g
        self.pirate = p
        self.capsule = c
    @staticmethod
    def get_possible_actions(game):
        return [FetchCapsule(game, pirate, capsule) for pirate in game.get_my_living_pirates() for capsule in game.get_my_capsules() if not (capsule.holder or pirate.capsule)]
    def exec(self):
        self.pirate.sail(self.capsule)
    def get_participants(self):
        return self.pirate, self.capsule
    def score(self):
        return Action.distance_and_difficulty(self)*MODIFIERS['FetchCapsule']

class ScoreCapsule(Action):
    def __init__(self, g, p, m):
        self.game = g
        self.pirate = p
        self.mothership = m
    @staticmethod
    def get_possible_actions(game):
        return [ScoreCapsule(game, pirate, mothership) for pirate in game.get_my_living_pirates() for mothership in game.get_my_motherships() if pirate.capsule]
    def exec(self):
        self.pirate.sail(self.mothership)
    def get_participants(self):
        return self.pirate # no need to put the mothership here, I guess
    def score(self):
        return Action.distance_and_difficulty(self)*MODIFIERS['ScoreCapsule']

class CommitSudoku(Action):
    def __init__(self, p):
        self.pirate = p
        self.target = util.suicide_wall(p)
    @staticmethod
    def get_possible_actions(game):
        return [CommitSudoku(pirate) for pirate in game.get_my_living_pirates()]
    def get_participants(self):
        return self.pirate
    def score(self):
        return Action.distance_score(self)*MODIFIERS['CommitSudoku']
    def exec(self):
        self.pirate.sail(self.target)

class PushAsteroid(Action):
    def __init__(self, g, p, a):
        self.game = game
        self.pirate = p
        self.asteroid = a
    @staticmethod
    def get_possible_actions(game):
        return [PushAsteroid(game, pirate, asteroid) for pirate in game.get_my_living_pirates() for asteroid in game.get_living_asteroids() if pirate.can_push(Asteroid)]
    def get_participants(self):
        return self.pirate, self.asteroid
    def score(self):
        # TODO
        # Perhaps separate it into several classes (i.e KillWithAsteroid, DefendWithAsteroid, MoveAsteroid)?
        pass
    def exec(self):
        pass

