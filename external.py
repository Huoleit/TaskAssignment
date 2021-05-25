from datetime import datetime
from math import sqrt, inf

class Target:
    def __init__(self, x: float, y: float):
        self._x = x
        self._y = y
        self._create_time = datetime.now()

    def get_position(self):
        return (self._x, self._y)
    
    def get_position_int(self):
        return (int(round(self._x)), int(round(self._y)))

    def get_idle_time(self):
        return (datetime.now() - self._create_time).total_seconds()
    
    def get_distance(self, pos):
        return sqrt((pos[0]-self._x)**2 + (pos[1]-self._y)**2)


class Trolley(Target):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)
    
    def get_reward(self) -> float:
        return self.get_idle_time() / 60.0 + 10


class Worker(Target):
    def __init__(self, x: float, y: float):
        super().__init__(x, y)

class TrolleyGroup(Trolley):
    def __init__(self, x: float, y: float, trolley: list[Trolley]):
        super().__init__(x, y)
        self._trolley = trolley
    
    def get_reward(self) -> float:
        reward = 0
        for i in self._trolley:
            reward += i.get_reward()
        return reward

    def get_trolleys(self) -> list[Trolley]:
        return self._trolley
        
    def get_trolleys_pos(self) -> list:
        pos = []
        for t in self.get_trolleys():
            pos.append(t.get_position())
        return pos

    def get_closest_trolley(self, pos):
        min_dis = inf
        min_index = -1
        for i, t in enumerate(self.get_trolleys()):
            dis = t.get_distance(pos)
            if dis < min_dis:
                min_dis = dis
                min_index = i
        return min_index