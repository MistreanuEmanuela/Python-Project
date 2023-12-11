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
    denominator = 1

    for i in denominators:
        denominator *= i

    num = sum([division_modulo(numerators[i] * denominator * points_interpolate[i][1] % p, denominators[i], p)
               for i in range(len(points_interpolate))])

    return (division_modulo(num, denominator, p) + p) % p


class ShamirSecretShareFiles:
    def __init__(self, file_path, minim_participants, n):
        if n < minim_participants:
            raise Exception("You should enter a smaller number or the information will be lost")
        if n < 3:
            raise Exception("You shoud enter a biggest number")
        if minim_participants < 2:
            raise Exception("You should enter a biggest number")
        self.__n = n
        self.__file_path = file_path
        self.__minim_participants = minim_participants
        self.__coefficients = []
        self.points = []
        self.__secret = self.__determinate_secret()

    def __determinate_secret(self):
        try:
            with open(self.__file_path, "rb") as f:
                secret = f.read()
            number = int.from_bytes(secret, 'big')
            print(number)
            return number
        except FileNotFoundError:
            print("The path to file is not correct, please check")

    def coefficients_det(self):
        self.__coefficients.append(self.__secret)
        for i in range(self.__minim_participants - 1):
            random_coefficients = random.randint(1, _PRIME-1)
            self.__coefficients.append(random_coefficients)

    def run(self):
        self.coefficients_det()
        self.compute_points()

    def _calc_function(self, x):
        result = self.__secret
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

    def reconstruct(self, lista_index):
        points_interpolate = []
        for i in lista_index:
            points_interpolate.append(self.points[i])
        return lagrange_interpolation(0, points_interpolate, _PRIME)


#testare:

shair = ShamirSecretShareFiles("C:\\Users\\My Pc\\Desktop\\file.txt", 4, 7)
shair.run()
result = shair.reconstruct([1, 2, 3, 5])
print(result)