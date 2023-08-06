import dispositor.planet as planet
from dispositor.segment import Segment


class Space:
    """
    Класс пространства.
    Для создания необходима дата и сегменты (деление пространства)
    Обязанность: Создание сегментов и планет.
    """
    def __init__(self, date, segmentData):
        self.date = date
        self.segmentData = segmentData
        self.deg_count = 360
        self.segments = self.createSegments()
        self.planets = self.createPlanets()

    def createPlanets(self):
        """
        Уникальные значения планет из списка сегментов
        """
        planets = []
        for owner_planet in [segment.owner_planet for segment in self.segments]:
            if owner_planet.__name__ not in [planet_class.__class__.__name__ for planet_class in planets]:
                planets.append(owner_planet(self))
        return planets

    def createSegments(self):
        """
        Фабрика сегментов
        """
        segments = []
        for i, segment_data in enumerate(self.segmentData):
            deg_in_segment = self.getDegCount() / self.getSegmentCount()
            deg_from = i * deg_in_segment
            deg_to = deg_from + deg_in_segment
            segments.append(Segment(
                i+1,
                segment_data['name'],
                segment_data['rus_name'],
                segment_data['owner_planet'],
                deg_from, deg_to
            ))
        return segments

    def getSegmentCount(self):
        """
        Получить количество сегментов
        """
        return len(self.segmentData)

    def getDegCount(self):
        """
        Получить количество градусов в окружности (пространстве)
        """
        return self.deg_count

    def getPlanets(self):
        """
        Получить список планет
        """
        return self.planets

    def getSegments(self):
        """
        Получить список сегментов
        """
        return self.segments


def classicSegmentData():
    """
    Классическое расположение сегментов и планет
    """
    return [
        {'name': 'Aries', 'rus_name': 'Овен', 'owner_planet': planet.Mars},
        {'name': 'Taurus', 'rus_name': 'Телец', 'owner_planet': planet.Venus},
        {'name': 'Gemini', 'rus_name': 'Близнецы', 'owner_planet': planet.Mercury},
        {'name': 'Cancer', 'rus_name': 'Рак', 'owner_planet': planet.Moon},
        {'name': 'Leo', 'rus_name': 'Лев', 'owner_planet': planet.Sun},
        {'name': 'Virgo', 'rus_name': 'Дева', 'owner_planet': planet.Mercury},
        {'name': 'Libra', 'rus_name': 'Весы', 'owner_planet': planet.Venus},
        {'name': 'Scorpio', 'rus_name': 'Скорпион', 'owner_planet': planet.Pluto},
        {'name': 'Sagittarius', 'rus_name': 'Стрелец', 'owner_planet': planet.Jupiter},
        {'name': 'Capricorn', 'rus_name': 'Козерог', 'owner_planet': planet.Saturn},
        {'name': 'Aquarius', 'rus_name': 'Водолей', 'owner_planet': planet.Uranus},
        {'name': 'Pisces', 'rus_name': 'Рыбы', 'owner_planet': planet.Neptune},
    ]