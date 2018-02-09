class Utils(object):
    @staticmethod
    def closest_wall(loc):
        loc = loc.get_location()
        x = loc.row
        y = loc.col
        distances = [x, MAP_ROWS - x, y, MAP_COLS - y]
        index = distances.index(min(distances))
        if index == 0:
            return Location(0, y)
        if index == 1:
            return Location(MAP_ROWS, y)
        if index == 2:
            return Location(x, 0)
        return Location(x, MAP_COLS)
