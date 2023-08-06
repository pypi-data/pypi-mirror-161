class Segment:
    def __init__(self, number, id, name, rus_name, owner_planet, deg_from, deg_to):
        self.number = number
        self.id = id
        self.deg_from = deg_from
        self.deg_to = deg_to
        self.name = name
        self.rus_name = rus_name
        self.owner_planet = owner_planet

    def getDegNumber(self):
        return self.number

    def getDegFrom(self):
        return self.deg_from

    def getDegTo(self):
        return self.deg_to

