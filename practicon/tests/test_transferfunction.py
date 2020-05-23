"""
Test the CheckTransferFunction class.

To run test from within Spyder and with source dir, 
set run dir to practicon3, and dedicated console

Created on Fri May  8 18:36:32 2020

@author: repa
"""

from practicon import CheckTransferFunction, conv
from control import TransferFunction
import pytest


def test_transferfunction():
    # no variable found, runtimewarning
    check1 = CheckTransferFunction('a', 0.1, 0.00)
    check2 = CheckTransferFunction('b', 0.1, 0.00)
    check3 = CheckTransferFunction('a', 0.0, 0.15)

    # reference function
    def myfunc(variant: int):
        return {'a': TransferFunction([1, 1], [1, 1, variant])}

    # generate encoding
    ref = check1.encode(5, myfunc)

    # when no answer found, this should raise a runtime warning
    with pytest.raises(RuntimeWarning):
        check2(0, ref, locals())

    # fail for incorrect/unreadable
    a = (2, 3)
    assert check1(0, ref, locals())[1] == 0.0

    # set back to normal
    a = conv(TransferFunction([1, 1], [1, 1, 0]))

    # succeed for all in range
    for v in range(1, 5):
        testname, score, result, sa, odelanswer = check1(v, ref, locals())
        # print(testname, score, result, modelanswer, sep='\n')
        assert testname == "Transfer function 'a'"
        assert score < 1.0
        assert result != "answered correctly"
        # assert modelanswer == f"Reference {10+v} (± 0.1)"

    # correct answer
    testname, score, result, sa, modelanswer = check1(0, ref, locals())
    assert testname == "Transfer function 'a'"
    assert score == 1.0
    assert result == "answered correctly"
    assert sa == modelanswer
    # assert modelanswer == f"Reference {10} (± 0.1)"

    # with numerical stuff in numerator
    a = conv(TransferFunction([1.0e-17, 1, 1], [1, 1, 0]))
    # correct answer
    testname, score, result, sa, modelanswer = check1(0, ref, locals())
    assert testname == "Transfer function 'a'"
    assert score == 1.0
    assert result == "answered correctly"

    # ratio test
    testname, score, result, sa, modelanswer = check3(0, ref, locals())
    assert score == 1.0
    assert modelanswer == "\n s + 1\n-------\ns^2 + s\n"

    # incorrect number of zeros/poles
    a = conv(TransferFunction([1], [1, 1, 1, 0]))

    testname, score, result, sa, modelanswer = check1(0, ref, locals())
    assert testname == "Transfer function 'a'"
    assert score < 1.0
    assert result != "answered correctly"
    # assert modelanswer == f"Reference {10} (± 0.1)"

    tf = TransferFunction([1, 2], [1, 1, 0])
    num, den = conv(tf.num[0][0]), conv(tf.den[0][0])

    check4 = CheckTransferFunction('notfound', 0.1, 0.0, ('num', 'den'))
    ref4 = check4.encode(1, lambda v: {'notfound': tf})
    testname, score, result, sa, modelanswer = check4(0, ref4, locals())
    assert score == 1.0
    print(result)

if __name__ == '__main__':
    test_transferfunction()
