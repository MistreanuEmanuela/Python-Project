import random

class Shamir_secret_share():
    def __init__(self, number, minim_participants, n):
        self.__n = n
        self.__number = number
        self.__minim_participants = minim_participants
        self.__coef = []
        self.__points = []

    def coefficients_det(self):
        for i in range(self.__minim_participants - 1):
            random_coeff = random.randint(1, self.__number)
            self.__coef.append(random_coeff)

    def _calc_function(self, x):
        result = self.__number
        for i in range(1, self.__minim_participants - 1):
            result += x ** i * self.__coef[i-1]
        return result

    def compute_points(self):
        for i in range(1, self.__n+1):
            point = self._calc_function(i)
            self.__points.append((i, point))

    def split_info(self):
        for i in self.__points:
            print(i)
