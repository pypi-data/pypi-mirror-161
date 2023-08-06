from __future__ import annotations
from enum import Enum
import random
from ..utils import are_operators_implemnted, almost_equal
from .Complex import Complex
from typing import Any, Callable


class Fields(Enum):
    Q = "Q"
    R = "R"
    C = "C"
    M = "M"


class Field:
    @staticmethod
    def create(name: Fields, degree: int = 1, modulu: int = 1) -> Field:
        match name:
            case Fields.Q:
                return RationalField(degree, modulu)
            case Fields.R:
                return RealField(degree, modulu)
            case Fields.C:
                return ComplexField(degree, modulu)
            case Fields.M:
                # TODO Field create function for Fields.M
                pass
                # return MatrixField(name, zero, one, degree, modulu)

    @staticmethod
    def is_field(field: Field) -> bool:
        N = 100
        if not are_operators_implemnted(type(field.random())):
            raise NotImplementedError(
                "One of the nescesary operators for calculation was not implemented")

        def checker(var_count: int, rule: Callable[[], bool], exclude=None) -> bool:
            if exclude is None:
                exclude = []
            for _ in range(N):
                vars = [field.random() for _ in range(var_count)]
                for v in vars:
                    if v in exclude:
                        break
                else:
                    if not rule(*vars):
                        pass
                    if not rule(*vars):
                        return False
            return True

        def associativity() -> bool:
            def addition() -> bool:
                return checker(3, lambda a, b, c: almost_equal((a+b)+c, a+(b+c)))

            def multiplication() -> bool:
                return checker(3, lambda a, b, c: almost_equal((a*b)*c, a*(b*c)))
            return all([addition(), multiplication()])

        def commutativity() -> bool:
            def addition() -> bool:
                return checker(2, lambda a, b: almost_equal(a+b, b+a))

            def multiplication() -> bool:
                return checker(2, lambda a, b: almost_equal(a*b, b*a))
            return all([addition(), multiplication()])

        def distributivity() -> bool:
            def addition() -> bool:
                return checker(3, lambda a, b, c: almost_equal(a*(b+c), a * b + a * c))

            def multiplication() -> bool:
                return checker(3, lambda a, b, c: almost_equal((a+b)*c, a * c + b * c))
            return all([addition(), multiplication()])

        def identity() -> bool:
            def addition() -> bool:
                return checker(1, lambda a: almost_equal(a+field._zero, a, field._zero+a))

            def multiplication() -> bool:
                return checker(1, lambda a: almost_equal(a*field._one, a, field._one*a))
            return all([addition(), multiplication()])

        def inverses() -> bool:
            def addition() -> bool:
                return checker(1, lambda a: almost_equal(a + (-a), field._zero, (-a)+a))

            def multiplication() -> bool:
                return checker(1, lambda a: almost_equal(a * (1/a), field._one, (1/a)*a), [0])
            return all([addition(), multiplication()])
        return all([associativity(), commutativity(), distributivity(), identity(), inverses()])

    def __init__(self, name: Fields,  zero, one, degree: int = 1, modulu: int = 1, validate: bool = False) -> None:
        if not isinstance(name, Fields):
            raise TypeError("'name' must be from enum 'Fields'")
        if not isinstance(degree, int):
            raise TypeError("'degree' must be of type 'int'")
        if not isinstance(modulu, int):
            raise TypeError("'modulu' must be of type 'int'")
        self._name = name
        self._modulu = modulu
        self._degree = degree
        self._zero = zero
        self._one = one
        if validate:
            if not Field.is_field(self):
                raise ValueError(
                    "This is not a field as one or more of the axioms do not check-out")

    @property
    def classOfInstance(self) -> Field:
        # raise NotImplementedError("This is a virtual method")
        return type(self)

    def __str__(self) -> str:
        return f"{self._name.value}{self._degree}%{self._modulu}"

    def __eq__(self, other: Field) -> bool:
        return self._name == other._name and self._modulu == other._modulu and self._degree == other._degree and self._zero == other._zero and self._one == other._one

    # def __contains__(self, obj: Any) -> bool:
    #     """
    #     """
    #     raise NotImplementedError("This is a virtual method")

    def random(self, min: int = -10, max: int = 10) -> Any:
        """
        This is a virtual method for derived classes to generate a random element from current field with degree 1
        e.g. if self is Rn hen Rn._generate_one() will return an elemnt from R1
        the generation of a full vector is with 'random' function
        """
        raise NotImplementedError("This is a virtual method")

    # def random(self, min: float = -10, max: float = 10) -> Vector:
    #     """
    #     will generate a random vector from this field
    #     """
    #     self._generate_one(min, max)
    #     return Vector .Vector([
    #         self._generate_one(min, max)
    #         for _ in range(self._degree)
    #     ], self)


class RationalField(Field):
    def __init__(self, degree=1, modulu=1):
        super().__init__(Fields.Q, 0, 1, degree, modulu)

    def random(self, min: int = -10, max: int = 10) -> float:
        if min == max:
            raise ValueError(
                "if 'min'=='max' you shouldnt use this function becuase there's no use to it")
        if min > max:
            raise ValueError("'min' should be less than 'max'")
        f = random.randint
        sign = 1 if f(0, 1) == 1 else -1
        nominator = f(min, max)
        denominator = f(min, max)
        while(denominator == 0):
            denominator = f(min, max)
        return sign*nominator/denominator

    # def __contains__(self, obj) -> bool:
    #     """
    #     NOT IMPLEMENTED
    #     Due to how numbers are stored in python all fractional numbers are rational so this function is irrelevant
    #     """
    #     raise NotImplementedError(
    #         "Due to how numbers are stored in python all fractional numbers are rational so this function is irrelevant")


DefaultRationalField = RationalField()


class RealField(Field):
    def __init__(self, degree=1, modulu=1):
        super().__init__(Fields.R, 0, 1, degree, modulu)

    def random(self, min: int = -10, max: int = 10) -> float:
        return random.uniform(min, max)

    # def __contains__(self, obj: Union[int, float, Vector.Vector]) -> bool:
    #     if isinstance(obj, float) or isinstance(obj, int) and self._degree == 1:
    #         return True
    #     else:
    #         if not isinstance(obj, Vector.Vector):
    #             raise ValueError(
    #                 "Can't check if object is not of type 'Vector'")
    #         return obj.field == self


DefaultRealField = RealField()


class ComplexField(Field):
    def __init__(self, degree=1, modulu=1):
        super().__init__(Fields.C, Complex(0, 0),
                         Complex(1, 0), degree, modulu)

    def random(self, min: int = -10, max: int = 10) -> Complex:
        return Complex.random(min, max, random.uniform)

    # def __contains__(self, obj: Union[int, float, Complex, Vector.Vector]) -> bool:
    #     if (isinstance(obj, Complex.Complex) or isinstance(obj, float) or isinstance(obj, int)) and self._degree == 1:
    #         return True
    #     else:
    #         if not isinstance(obj, Vector.Vector):
    #             raise ValueError(
    #                 "Can't check if object is not of type 'Vector'")
    #         return obj.field == self


DefaultComplexField = ComplexField()


# class MatrixField(Field):
#     # TODO MatrixFIeld

#     def __init__(self, n: int, field: Field,) -> None:

#         pass

#     def _generate_one(self, min: int = -10, max: int = 10) -> Matrix.Matrix:
#         pass

#     # def __contains__(self, v) -> bool:
#     #     pass
