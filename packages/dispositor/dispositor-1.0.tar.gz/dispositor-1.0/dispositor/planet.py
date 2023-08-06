import math


class Planet:
    """
    Данный класс содержит родительский класс планеты и дочерние каждой планеты
    Для создания планеты необходимо пространство
    """
    def __init__(self, name, space):
        self.name = name
        self.space = space

    def getDeg(self):
        ephem_planet = getattr(__import__('ephem'), self.name)()
        ephem_planet.compute(self.space.date)
        return math.degrees(ephem_planet.ra)

    def getSegment(self):
        """
        Получить сегмент для планеты
        """
        for segment in self.space.segments:
            if segment.getDegFrom() <= self.getDeg() < segment.getDegTo():
                return segment


class Sun(Planet):

    name = 'Sun'

    def __init__(self, space):
        Planet.__init__(self, self.name, space)


class Moon(Planet):

    name = 'Moon'

    def __init__(self, space):
        Planet.__init__(self, self.name, space)


class Mercury(Planet):

    name = 'Mercury'

    def __init__(self, space):
        Planet.__init__(self, self.name, space)

class Venus(Planet):

    name = 'Venus'

    def __init__(self, space):
        Planet.__init__(self, self.name, space)


class Mars(Planet):

    name = 'Mars'

    def __init__(self, space):
        Planet.__init__(self, self.name, space)


class Jupiter(Planet):

    name = 'Jupiter'

    def __init__(self, space):
        Planet.__init__(self, self.name, space)


class Saturn(Planet):

    name = 'Saturn'

    def __init__(self, space):
        Planet.__init__(self, self.name, space)


class Uranus(Planet):

    name = 'Uranus'

    def __init__(self, space):
        Planet.__init__(self, self.name, space)


class Neptune(Planet):

    name = 'Neptune'

    def __init__(self, space):
        Planet.__init__(self, self.name, space)


class Pluto(Planet):

    name = 'Pluto'

    def __init__(self, space):
        Planet.__init__(self, self.name, space)


