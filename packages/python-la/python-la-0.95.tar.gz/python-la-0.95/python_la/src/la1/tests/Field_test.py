from ...la1 import Field, Complex as c, RealField, ComplexField, DefaultComplexField, DefaultRealField, DefaultRationalField


def test_is_field():
    assert Field.is_field(DefaultComplexField)
    assert Field.is_field(DefaultRealField)
    assert Field.is_field(DefaultRationalField)


def test_clone():
    r3 = RealField(3)
    r21 = r3.classOfInstance(2)
    r23 = r3.classOfInstance.create(r3._name, 2)
    assert r21 == r23
