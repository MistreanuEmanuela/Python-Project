import random


def combination(vector_elements, k, current_combination=None, start=0):
    if current_combination is None:
        current_combination = []

    if k == 0:
        return [tuple(current_combination)]

    comb_list = set()
    for i in range(start, len(vector_elements)):
        current_combination.append(vector_elements[i])
        comb_list.update(combination(vector_elements, k - 1, current_combination, i + 1))
        current_combination.pop()

    return comb_list


def lagrange_basis(points, i):
    result = []
    xi = points[i][0]
    denominator = 1
    free_t = 1
    vector = []
    for j, item in enumerate(points):
        if j != i:
            xj, yj = item
            denominator *= (xi - xj)
            free_t *= xj
            vector.append(xj)

    result.append(1 / denominator)
    for i in range(1, len(points) - 1):
        x = combination(vector, i)
        sum = 0
        for item in x:
            product = 1
            for element in item:
                product *= element
            sum += product
        coeff = sum/denominator if (len(points) - i) % 2 == 1 else (-sum)/denominator
        result.append(coeff)
    free_t = free_t/denominator if len(points) % 2 == 1 else -free_t/denominator
    result.append(free_t)
    return result


def lagrange_interpolation(points, coefficients):
    f_x = []
    for i in range(len(points)):
        coeff = 0
        for j in range(len(points)):
            coeff += points[j][1] * coefficients[j][i]
        f_x.append(coeff)
    return f_x


class ShamirSecretShare:
    def __init__(self, number, minim_participants, n):
        self.__n = n
        self.__number = number
        self.__minim_participants = minim_participants
        self.__coef = []
        self.points = []

    def coefficients_det(self):
        self.__coef.append(self.__number)
        for i in range(self.__minim_participants - 1):
            random_coeff = random.randint(1, 50)
            self.__coef.append(random_coeff)
        print(self.__coef)

    def _calc_function(self, x):
        result = self.__number
        for i in range(1, self.__minim_participants):
            result += x ** i * self.__coef[i]
        print(result)
        return result

    def compute_points(self):
        for i in range(1, self.__n + 1):
            point = self._calc_function(i)
            self.points.append((i, point))

    def split_info(self):
        for i in self.points:
            print(i)


#testare:

shair = ShamirSecretShare(1234, 3, 6)
shair.coefficients_det()
shair.compute_points()
shair.split_info()
points = []
for i in shair.points:
    if(len(points) < 3):
        points.append(i)
l_0 = lagrange_basis(points, 0)
l_1 = lagrange_basis(points, 1)
l_2 = lagrange_basis(points, 2)
coef = [l_0, l_1, l_2]
l_in = lagrange_interpolation(points, coef)
print(l_in[-1])