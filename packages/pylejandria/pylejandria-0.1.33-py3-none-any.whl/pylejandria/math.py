"""
Set of functions and classes that facilitate mathematics in python, we are
aware that there are specialized libraries, but the idea of this module is
that it is easy and fast access.
"""

import math
import pylejandria
from pylejandria.constants import Number, Array, Coordinate
from typing import Any


class Vector:
    """
    The class Vector is always necessary for videogames or school, its basic
    funcionality is give all the components of the vector and be able to use
    all its operators, vector addition, subtraction, scalar multiplication,
    cross and dot product.
    """
    def __init__(self, *args: Array) -> None:
        if len(args) < 2:
            if not isinstance(args, (list, tuple)):
                raise NotImplementedError("Not enough values")
            else:
                self.args = list(args[0])
        else:
            self.args = list(args)
        self.magnitude = sum(map(lambda x: x*x, self.args))

    def eval(self, result: Any, other: Any, valid: tuple[Any]) -> bool:
        """
        eval takes a result, an object and the type of objects it
        can receive, it checks if the type of the object is in
        the accepted objects and returns the result if so, else
        raises an error.
        """
        if isinstance(other, valid):
            return result
        raise NotImplementedError("Invalidad operation")

    def __getitem__(self, index: Coordinate) -> int | float:
        """
        returns index-nth component of the vector.
        """
        if index < len(self) and index >= -len(self):
            return self.args[index]
        raise NotImplementedError("Component out of range.")

    def __setitem__(self, index: Coordinate, value: int | float) -> None:
        """
        sets the index-nth component of the vector to the given value.
        """
        if index < len(self) and index >= -len(self):
            self.args[index] = value
        else:
            raise NotImplementedError("Component out of range.")

    def __add__(self, other):
        """
        returns the sum of this vector and another vector.
        """
        if isinstance(other, (Vector, )):
            a, b = self.args, other.args
            if len(self) < len(other):
                a += [0] * (len(other) - len(self))
            else:
                b += [0] * (len(self) - len(other))
            return Vector(map(lambda x, y: x+y, a, b))

    def __sub__(self, other):
        return self + (-other)

    def __neg__(self):
        return self * -1

    def __len__(self):
        return len(self.args)

    def __mul__(self, other):
        return self.eval(
            Vector(
                map(
                    lambda x: other*x,
                    self.args
                )
            ),
            other,
            (int, float)
        )

    def __rmul__(self, other):
        return self * other

    def __gt__(self, other):
        return self.eval(self.magnitude > other.magnitude, other, (Vector, ))

    def __lt__(self, other):
        return self.eval(self.magnitude < other.magnitude, other, (Vector, ))

    def __ge__(self, other):
        return self.eval(self.magnitude >= other.magnitude, other, (Vector, ))

    def __le__(self, other):
        return self.eval(self.magnitude <= other.magnitude, other, (Vector, ))

    def __ne__(self, other):
        return self.eval(self.args != other.args, other, (Vector, ))

    def __eq__(self, other):
        return self.eval(self.args == other.args, other, (Vector, ))

    def __repr__(self):
        return str(self.args)


class Matrix:
    def __init__(
        self,
        matrix: list[Array],
        dim: Coordinate | None=()
    ) -> None:
        """
        Matrix is a representation of algebra matrix, is takes a list of lists
        of numbers. It contains functions matrix addition, subtraction,
        multiplication, scalar multiplication, get determinant and many
        things we plan to add.
        params:
            matrix: list of lists with integers and/or floats.
            dim:    coordinate with the dimensions of the matrix, its used to
                    make empty matrices, if used matrix parameter should
                    be None.
        """
        if matrix is not None:
            if any([len(row) != len(matrix[0]) for row in matrix]):
                raise NotImplementedError('Invalid Matrix dimension.')
            self.matrix = matrix
        else:
            if len(dim) != 2:
                raise NotImplementedError("Invalid Matrix dimension.")
            if dim[0] < 1 or dim[1] < 1:
                raise NotImplementedError("Dimension must be greater than 0.")
            if dim[0] == 1 and dim[1] == 1:
                raise NotImplementedError("Matrix cannot be 1x1.")
            self.matrix = [
                [1 for _ in range(dim[0])]
                for _ in range(dim[1])
            ]
        self.rows, self.cols = len(self.matrix), len(self.matrix[0])
        self.is_square = len(self.matrix) == len(self.matrix[0])
        self.dim = (self.cols, self.rows)
        if self.is_square:
            self.determinant = self.get_determinant(self.matrix)
        else:
            self.determinant = None

    def get_determinant(self, matrix: list[list]) -> float:
        """
        this function is made to get determinant of the given matrix, it can be
        used externally but it wasnt intended at first. The determinant is
        calculated using recursion, if the dimension is 2 then we return ad-bc.
        params:
            matrix: list of lists with integers and/or floats.
        """
        if len(matrix) == 2:
            return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]

    def valid_value(self, index: Coordinate) -> bool:
        """
        generic function of Matrix to check if the given pair of coordinates is
        in the range of the matrix.
        params:
            index:  pair of coordinates representing the position to valid in
                    the matrix.
        """
        x, y = index
        return all([
            x < self.cols,
            x >= -self.cols,
            y < self.rows,
            y >= -self.rows
        ])

    def return_value(self, index: Coordinate) -> float:
        """
        checks if the given index is valid and if so returns the
        corresponding value, if not raise an error.
        params:
            index:  pair of coordinates representing the position to return
                    from the matrix.
        """
        x, y = index
        if not self.valid_value(index):
            raise NotImplementedError("Invalid Matrix index.")
        return self.matrix[y][x]

    def row(self, index: int) -> list:
        """
        returns index-nth row of the matrix.
        params:
            index: integer representing the wanted row.
        Example:
            a = Matrix(
                [
                    [1, 2, 3],
                    [4, 5, 6],
                    [7, 8, 9]
                ]
            )
            a.row(2) -> [7, 8, 9]
        """
        if index < self.rows and index >= -self.rows:
            return self.matrix[index]
        raise NotImplementedError("Invalid row index.")

    def col(self, index: int) -> list:
        """
        returns index-nth column of the matrix.
        params:
            index: integer representing the wanted column.
        Example:
            a = Matrix(
                [
                    [1, 2, 3],
                    [4, 5, 6],
                    [7, 8, 9]
                ]
            )
            a.col(1) -> [2, 5, 8]
        """
        if index < self.cols and index >= -self.cols:
            return [row[index] for row in self.matrix]
        raise NotImplementedError("Invalid column index.")

    def __getitem__(
        self, indices: Coordinate | tuple[Coordinate]
    ) -> float | Array:
        """
        if index is a single pair of numbers then it returns the corresponding
        value of the matrix, but if multiple indices in form of tuples are
        given inside the [] then returns a list of the corresponding values
        for each index.
        Example:
            a = Matrix(
                [
                    [1, 2, 3],
                    [4, 5, 6],
                    [7, 8, 9]
                ]
            )
            a[2, 1] -> 6
            a[(0, 0), (1, 1), (2, 2)] -> [1, 5, 9]
        """
        if not isinstance(indices[0], tuple):
            return self.return_value(indices)
        return [self.return_value((x, y)) for x, y in indices]

    def __add__(self, other):
        if isinstance(other, Matrix):
            if self.dim != other.dim:
                raise NotImplementedError("Matrices must be same order.")
            return Matrix(
                [
                    [
                        self[x, y] + other[x, y]
                        for x in range(self.cols)
                    ]
                    for y in range(self.rows)
                ]
            )
        raise NotImplementedError("Invalid Matrix addition.")

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Matrix(
                [
                    [
                        other*self[x, y]
                        for x in range(self.cols)
                    ]
                    for y in range(self.rows)
                ]
            )
        elif isinstance(other, Matrix):
            if self.cols != other.rows:
                raise NotImplementedError("Invalid Matrices dimensions.")
            c = Matrix(None, (other.cols, self.rows))
            for i in range(self.rows):
                for j in range(other.cols):
                    c[j, i] = sum(
                        map(
                            lambda x, y: x*y,
                            self.row(i), other.col(j)
                        )
                    )
            return c
        raise NotImplementedError("Invalid Matrix multiplication.")

    def __repr__(self):
        return pylejandria.tools.prettify(self.matrix, separator=' ')

    def __rmul__(self, other):
        return self * other

    def __neg__(self):
        return self * -1

    def __sub__(self, other):
        return self + (-other)

DEGREES = False


def set_degrees(value: bool = False) -> None:
    """
    set_degrees receives a boolean as input to globally change
    the angle functions, normally in programming angles are used in
    radians, but for quick calculations of for not used to people
    it can be useful to use degrees.
    params:
        value: the new value to degree mode.
    """
    global DEGREES
    DEGREES = value


def sin(x: Number) -> Number:
    """
    returns the sin of the given number, depending on the mode it takes
    radians or degrees. Check set_degrees to do so.
    params:
        x: angle to take sin of.
    """
    return math.sin(x if not DEGREES else math.radians(x))


def cos(x: Number) -> Number:
    """
    returns the cos of the given number, depending on the mode it takes
    radians or degrees. Check set_degrees to do so.
    params:
        x: angle to take cos of.
    """
    return math.cos(x if not DEGREES else math.radians(x))


def tan(x: Number) -> Number:
    """
    returns the tan of the given number, depending on the mode it takes
    radians or degrees. Check set_degrees to do so.
    params:
        x: angle to take tan of.
    """
    return math.tan(x if not DEGREES else math.radians(x))


def acos(x: Number) -> Number:
    """
    returns the acos of the given number, depending on the mode it can return
    radians or degrees. Check set_degrees to do so.
    params:
        x: angle to take acos of.
    """
    return math.acos(x) if not DEGREES else math.degrees(math.acos(x))


def asin(x: Number) -> Number:
    """
    returns the asin of the given number, depending on the mode it can return
    radians or degrees. Check set_degrees to do so.
    params:
        x: angle to take asin of.
    """
    return math.asin(x) if not DEGREES else math.degrees(math.asin(x))


def atan(x: Number) -> Number:
    """
    returns the atan of the given number, depending on the mode it can return
    radians or degrees. Check set_degrees to do so.
    params:
        x: angle to take atan of.
    """
    return math.atan(x) if not DEGREES else math.degrees(math.atan(x))


def atan2(y: Number, x: Number) -> Number:
    """
    returns the atan of the given number, depending on the mode it can return
    radians or degrees. Check set_degrees to do so.
    the difference between atan and atan2 is that atan2 returns the sign,
    while atan range is between 0 <= x <= pi/2 but atan2 range is between
    -pi <= x <= pi.
    params:
        y: number representing the height.
        x: number representing the width.
    """
    return math.atan2(y, x) if not DEGREES else math.degrees(math.atan2(y, x))


class Symbol:
    def __init__(
        self, name: str, value: Number | None=1,
        exponent: Number | None=1
    ) -> None:
        self.name = name
        self.value = value
        self.exponent = exponent

    def __repr__(self):
        if self.exponent == 0:
            return '1'
        result = ''
        if abs(self.value) != 1:
            result += str(self.value)
        elif self.value == -1:
            result += '-'
        result += self.name
        if self.exponent != 1:
            result += f'^{self.exponent}'
        return result

    def __eq__(self, other):
        if isinstance(other, int | float):
            if other == 0:
                return self.value == 0
            raise NotImplementedError(f'invalid comparison {type(other)} and Symbol')

    def __mul__(self, other):
        if isinstance(other, Number):
            return Symbol(self.name, self.value * other, self.exponent)
        elif isinstance(other, Symbol):
            if self.name == other.name:
                return Symbol(
                    self.name, self.value * other.value,
                    self.exponent + other.exponent
                )
            elif self.name != other.name:
                return Symbol(self.name + other.name, self.value * other.value)
        elif isinstance(other, Polynomial):
            return Polynomial([
                monomial * self
                for monomial in other.monomials
            ])
        raise NotImplementedError(
            f'invalid operation. {type(self)}, {type(other)}'
        )

    def __add__(self, other):
        if isinstance(other, Symbol):
            if self.name == other.name and self.exponent == other.exponent:
                return Symbol(self.name, self.value+other.value, self.exponent)
            elif self.name == other.name and self.exponent != other.exponent:
                return Polynomial(self, other)
            elif self.name != other.name:
                return Polynomial(self, other)
        elif isinstance(other, Polynomial):
            return Polynomial(*other.monomials, self)
        elif isinstance(other, int | float):
            return Polynomial(self, other)

        raise NotImplementedError('invalid operation or implemented yet.')

    def __neg__(self):
        return self * -1

    def __sub__(self, other):
        return self + (-other)

    def __rsub__(self, other):
        if isinstance(other, int | float):
            return Polynomial(other, -self)

    def __pow__(self, other):
        if isinstance(other, (Number, complex)):
            return Symbol(self.name, self.value**other, self.exponent*other)

    def __rmul__(self, other):
        return self * other

    def __radd__(self, other):
        return self + other

    def __truediv__(self, other):
        if isinstance(other, Number):
            return self * (1/other)
        elif isinstance(other, Symbol):
            if self.name == other.name:
                return Symbol(
                    self.name, self.value/other.value,
                    self.exponent-other.exponent
                )


class Polynomial:
    def __init__(self, *monomials, exponent=1):
        self.monomials = self.reduce(monomials)
        self.exponent = exponent

    def reduce(self, monomials):
        counts = {}
        for monomial in monomials:
            if isinstance(monomial, Symbol):
                key = f'{monomial.name}{monomial.exponent}'
            else:
                key = str(monomial)
            if counts.get(key):
                counts[key] += monomial
            else:
                counts[key] = monomial
        return [monomial for monomial in counts.values() if monomial != 0]

    def __repr__(self):
        result = ' + '.join([str(monomial) for monomial in self.monomials])
        result = result.replace('+ -', '- ')
        if self.exponent != 1:
            return f'({result})^{self.exponent}'
        return result

    def __neg__(self):
        return Polynomial(
            *[-monomial for monomial in self.monomials]
        )

    def __mul__(self, other):
        if isinstance(other, int | float | Symbol):
            return Polynomial(*[
                monomial * other
                for monomial in self.monomials
            ])
        if isinstance(other, Polynomial):
            monomials = [a*b for a in self.monomials for b in other.monomials]
            return Polynomial(*monomials)

    def __rmul__(self, other):
        return self * other

    def __sub__(self, other):
        return self + (-other)

    def __pow__(self, other):
        if isinstance(other, int):
            result = 1
            for _ in range(other):
                result *= self
            return result
        elif isinstance(other, (complex, float)):
            return Polynomial(*self.monomials, exponent=self.exponent * other)

if __name__ == '__main__':
    x, y = Symbol('x'), Symbol('y')
    print(x * (x + y))
