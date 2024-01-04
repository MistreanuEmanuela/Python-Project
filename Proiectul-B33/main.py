import random
import sys

DEFAULT_PRIME = 2 ** 275111 - 1  # a very large prime number that will help us to increase security of our shares


def euclid_alg(a, b, x=0, y=1, last_x=1, last_y=0):
    """
    Calculate the greatest common divisor between a and b and also the coefficients of
    the formula:

     ax + by = GCD(a, b)

    The function verifies, at each step, the break condition:
        - If b is 0, then it returns the values of x and y.
        - Otherwise, it calculates recursively, updating the values for a, b, x, y, last_x, and last_y.

        Parameters:
            :param a: an integer
            :param b: another integer
            :param x: a parameter to be updated during recursive calculations
            :param y: a parameter to be updated during recursive calculations
            :param last_x: a parameter to retain the last calculated information
            :param last_y: a parameter to retain the last calculated information

        Returns:
            :return: last_x and last_y calculated representing the coefficients in the equation ax + by = GCD(a, b)
    """
    if b == 0:
        return last_x, last_y
    else:
        remain = a // b
        a, b = b, a % b
        x, last_x = last_x - remain * x, x
        y, last_y = last_y - remain * y, y
        return euclid_alg(a, b, x, y, last_x, last_y)


def division_modulo(numerator, denominator, p):
    """
    Use the euclid_alg function to calculate (numerator/denominator) mod p like this: instead of making the division
    and lose some information it calculates the modular inverse of the denominator that it multiplies with the numerator

        Parameters:
            :param numerator: an integer
            :param denominator: another integer
            :param p: the large prime number
        Returns:
            :return: result of (numerator/denominator) mod p, i.e. modular inverse of denominator multiply by numerator
    """
    inv, x = euclid_alg(denominator, p)
    return numerator * inv


def lagrange_basis(points_interpolate, index, x):
    """
    Calculate the formula from Shamir secret share protocol.

    l0(x) = (x - x1) / (x0 - x1) * (x - x2) / (x0 - x2) * ... * (x - xm) / (x0 - xm)

    Parameters:
        :param points_interpolate: an array with points from which we want to reconstruct the representation of the
        secret (list of tuples)
        :param index: represents the index of the point for which we calculate the formula
        :param x: parameter to be replaced in the formula, preferably 0 for simplification
        (only interested in the last term)

    Returns:
        :return: free term of the polynomial as a tuple [denominator, numerator]
    """
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
    """
    Calculate another formula from Shamir Secret Share protocol, more specifically the formula
    that helps calculate the main polynomial, where the free term is the representation of
    the content to be secured:

    f(x) = SUM yj * lj(x) mod PRIME
        where yj represents the y coordinate of the points, and lj represents the Lagrange basis polynomial.

    For each point, calculate the Lagrange basis multiplied by y, retaining numerators and denominators.
    Use the division_modulo function and the euclid_alg to calculate modular inverses to avoid information loss.

    Parameters:
        :param x: the x element from the Lagrange basis formula
        :param points_interpolate: the points representing the content from which to obtain the initial secret
        (list of tuples)
        :param p: the large prime number for calculations

    Returns:
        :return: the content intended to be secured, obtained from some parts of it (points)
    """

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
    """
    This function extracts information from files specified in the list of file names (each file containing one point).
    It reconstructs the polynomial, with the constant term being the content of the initial file,
    using the Lagrange interpolation function.
    A new file is created, and the content of the initial file is written in binary format.

    Parameters:
        :param lista_files: an array containing the names of the files from which to extract points
        :param prime: the prime number used in the calculations

    Returns:
        :return: the content of the reconstructed polynomial file
    """
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
    """
    A class representing Shamir Secret Sharing for files.

    This class takes a binary representation of a file and creates a random polynomial of a degree
    equal to the number of parts to split minus 1. The free term of the polynomial is the secret,
    which is the representation of the file. To split the information, it calculates points and stores
    their coordinates in files. Later, it can read these files, use Lagrange interpolation to reconstruct
    the polynomial, and find the secret.

    Attributes:
        n : int
            The number of files in which we want to share the information.
        minim_participants: int
            The minimum number of files from which we can reconstruct the information.
        file_path : str
            The path to the file we want to secure.
        coefficients : list
            The coefficients of the polynomial.
        points : list of tuples
            The points calculated from the polynomial.
        secret : int
            The representation of the file content.
        prime : int
            A large prime number used in calculations.

    """
    def __init__(self, file_path, minim_participants, n):
        """
        Constructs all the necessary attributes for the class and initialized the rest.

        Parameters
            :param file_path: the path to file
            :param minim_participants: the minim number of file from witch we can reconstruct the main file
            :param n: the number of file in witch we want to split information
        """
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
        """
        This method open the file and read the information in a binary mode, so obtain an int from the content of file
        Return:
            :return: the int representation of file
        """
        try:
            with open(self.__file_path, "rb") as f:
                secret = f.read()
            number = int.from_bytes(secret, 'big')
            return number
        except FileNotFoundError:
            print("The path to file is not correct, please check")

    def coefficients_det(self):
        """
        Create a random polynomial of degree the number of minimum files from which we want to reconstruct -1 with
        coefficients between 1 and the prime number
        """
        self.__coefficients.append(self.__secret)
        for i in range(self.__minim_participants - 1):
            random_coefficients = random.randint(1, self.__prime - 1)
            self.__coefficients.append(random_coefficients)

    def run(self):
        """
        This method split the secret into several files by calling other methods
        """
        self.coefficients_det()
        self.compute_points()
        self.split_info()

    def _calc_function(self, x):
        """
        Calculate the value of the polynomial for a given x.

        Parameters:
            :param x: int
                The value for which to calculate the polynomial.

        Returns:
            :return: The result of the polynomial calculation.
        """
        result_function = self.__secret
        for i in range(1, self.__minim_participants):
            result_function += (x ** i * self.__coefficients[i]) % self.__prime
        return result_function

    def compute_points(self):
        """
        Calculate the value of the polynomial for x in the range from 1 to the number of files.

        Uses the calc_function method for the calculation.
        """
        for i in range(1, self.__n + 1):
            point = self._calc_function(i)
            self.points.append((i, point))

    def split_info(self):
        """
        Create a file for each point and write the coordinates in it.
        """
        for index, point in enumerate(self.points):
            file_split = f'file{index + 1}.secret'
            try:
                with open(file_split, 'w') as f:
                    string = str(point[0]) + " , " + str(point[1])
                    f.write(string)
            except Exception:
                print("An error occurred while creating the files")

    def reconstruct(self, lista_files):
        """
        receives a list of files and calls the function reconstruct_file to find the content of main file
        Parameters:
            :param lista_files: list of strings
        """
        if len(lista_files) != self.__minim_participants:
            raise Exception("Too few files, we can reconstruct the main file")
        print(reconstruct_file(lista_files, DEFAULT_PRIME))


def main():
    if sys.argv[1] == "-help":
        # Check if the script is invoked with a command-line argument '-help'.
        # If true, display help information.

        print("-split -n -m path_to file")
        print("     - n - number of files in which you want to share the information")
        print("     - m - number of minim files you want to use to reconstruct the information")
        print("     - path_to_file - the file whose information you want to share ")
        print("-recompose file_name1 file_name2 ... file_name_m")
        print("  BE CAREFUL THE NUMBERS OF FILENAME SHOULD BE AT LEAST M")

    elif sys.argv[1] == "-split":

        # Check if the script is invoked with a 'split' command and correct parameters.
        # If true, create a new instance of a class and call its 'run' method to process files and split information.


        print("split")
        if len(sys.argv) != 5:
            raise Exception("Wrong number of parameters try main.py -help")
        else:
            shamir = ShamirSecretShareFiles(sys.argv[4], int(sys.argv[3]), int(sys.argv[2]))
            shamir.run()
    elif sys.argv[1] == "-recompose":

        # Check if the script is invoked with a 'recompose' command and correct parameters.
        # If true, call the 'reconstruct' function to obtain the content from the list of given files.

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
