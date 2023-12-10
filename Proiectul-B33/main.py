import random
_PRIME = 2**275 - 1


def euclid_alg(a, b, x=0, y=1, last_x=1, last_y=0):
    if b == 0:
        return last_x, last_y
    else:
        remain = a // b
        a, b = b, a % b
        x, last_x = last_x - remain * x, x
        y, last_y = last_y - remain * y, y
        return euclid_alg(a, b, x, y, last_x, last_y)


def division_modulo(numerator, denominator, p):
    inv, x = euclid_alg(denominator, p)
    return numerator * inv


def lagrange_basis(points_interpolate, index, x):
    xi = points_interpolate[index][0]
    denominator = 1
    free_t = 1
    for j, item in enumerate(points_interpolate):
        if j != index:
            xj, yj = item
            denominator *= (xi - xj)
            free_t *= x - xj
    return [denominator, free_t]


def lagrange_interpolation(x, points_interpolate, p):
    numerators = []
    denominators = []
    for index in range(len(points_interpolate)):
        numerators.append(lagrange_basis(points_interpolate, index, x)[1])
        denominators.append(lagrange_basis(points_interpolate, index, x)[0])
    print(len(numerators))
    print(len(denominators))
    denominator = 1

    for i in denominators:
        denominator *= i

    num = sum([division_modulo(numerators[i] * denominator * points_interpolate[i][1] % p, denominators[i], p)
               for i in range(len(points_interpolate))])

    return (division_modulo(num, denominator, p) + p) % p


class ShamirSecretShare:
    def __init__(self, number, minim_participants, n):
        self.__n = n
        self.__number = number
        self.__minim_participants = minim_participants
        self.__coefficients = []
        self.points = []

    def coefficients_det(self):
        self.__coefficients.append(self.__number)
        for i in range(self.__minim_participants - 1):
            random_coefficients = random.randint(1, _PRIME-1)
            self.__coefficients.append(random_coefficients)
        print(self.__coefficients)

    def _calc_function(self, x):
        result = self.__number
        for i in range(1, self.__minim_participants):
            result += (x ** i * self.__coefficients[i]) % _PRIME
        return result

    def compute_points(self):
        for i in range(1, self.__n + 1):
            point = self._calc_function(i)
            self.points.append((i, point))

    def split_info(self):
        for i in self.points:
            print(i)


#testare:

shair = ShamirSecretShare(12344554, 3, 7)
shair.coefficients_det()
shair.compute_points()
shair.split_info()
points = []
for i in shair.points:
    if(len(points) < 3):
        points.append(i)
l_in = lagrange_interpolation(0, points, _PRIME)
print(l_in)