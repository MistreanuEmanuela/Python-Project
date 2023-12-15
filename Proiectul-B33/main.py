import random
import sys

DEFAULT_PRIME = 2 ** 275111 - 1


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


def reconstruct_file(lista_files, prime):
    points_interpolate = []
    for file in lista_files:
        try:
            with open(file, 'r') as f:
                line = f.readlines()
                line = line[0]
                line = line.split(',')
                x, y = int(line[0]), int(line[1])
                points_interpolate.append((x, y))
        except Exception:
            print("An error occurred while open the split file, try to split the information first")

    result_reconstruct = lagrange_interpolation(0, points_interpolate, prime)
    try:
        with open("result.txt", 'wb') as file:
            file.write(result_reconstruct.to_bytes((result_reconstruct.bit_length() + 7) // 8, 'big'))
    except Exception:
        print("An error occurred while creating the result file ")
    print("If the information is not readable you may pay attention on numbers of files")
    return lagrange_interpolation(0, points_interpolate, prime)


class ShamirSecretShareFiles:
    def __init__(self, file_path, minim_participants, n):
        if n < minim_participants:
            raise Exception("You should enter a smaller number or the information will be lost")
        if n < 3:
            raise Exception("You should enter a biggest number")
        if minim_participants < 2:
            raise Exception("You should enter a biggest number")
        self.__n = n
        self.__file_path = file_path
        self.__minim_participants = minim_participants
        self.__coefficients = []
        self.points = []
        self.__secret = self.__determinate_secret()
        self.__prime = DEFAULT_PRIME

    def __determinate_secret(self):
        try:
            with open(self.__file_path, "rb") as f:
                secret = f.read()
            number = int.from_bytes(secret, 'big')
            return number
        except FileNotFoundError:
            print("The path to file is not correct, please check")

    def coefficients_det(self):
        self.__coefficients.append(self.__secret)
        for i in range(self.__minim_participants - 1):
            random_coefficients = random.randint(1, self.__prime - 1)
            self.__coefficients.append(random_coefficients)

    def run(self):
        self.coefficients_det()
        self.compute_points()
        self.split_info()

    def _calc_function(self, x):
        result_function = self.__secret
        for i in range(1, self.__minim_participants):
            result_function += (x ** i * self.__coefficients[i]) % self.__prime
        return result_function

    def compute_points(self):
        for i in range(1, self.__n + 1):
            point = self._calc_function(i)
            self.points.append((i, point))

    def split_info(self):
        for index, point in enumerate(self.points):
            file_split = f'file{index + 1}.secret'
            try:
                with open(file_split, 'w') as f:
                    string = str(point[0]) + " , " + str(point[1])
                    f.write(string)
            except Exception:
                print("An error occurred while creating the files")

    def reconstruct(self, lista_files):
        if len(lista_files) != self.__minim_participants:
            raise Exception("Too few files, we can reconstruct the main file")
        print(reconstruct_file(lista_files, DEFAULT_PRIME))


def main():
    if sys.argv[1] == "-help":
        print("-split -n -m path_to file")
        print("     - n - number of files in which you want to share the information")
        print("     - m - number of minim files you want to use to reconstruct the information")
        print("     - path_to_file - the file whose information you want to share ")
        print("-recompose file_name1 file_name2 ... file_name_m")
        print("  BE CAREFUL THE NUMBERS OF FILENAME SHOULD BE AT LEAST M")

    elif sys.argv[1] == "-split":
        print("split")
        if len(sys.argv) != 5:
            raise Exception("Wrong number of parameters try main.py -help")
        else:
            shamir = ShamirSecretShareFiles(sys.argv[4], int(sys.argv[3]), int(sys.argv[2]))
            shamir.run()
    elif sys.argv[1] == "-recompose":
        if len(sys.argv) < 4:
            raise Exception(" you need more file, try main.py -help for more information")
        else:
            files = []
            for i in range(2, len(sys.argv)):
                files.append(sys.argv[i])
            print(files)
            reconstruct_file(files, DEFAULT_PRIME)
    else:
        raise Exception(f"command {sys.argv[1]} not found")


if __name__ == "__main__":
    main()
