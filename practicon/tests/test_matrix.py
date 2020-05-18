#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 11 10:45:45 2020 .

Test the CheckMatrix class.

@author: repa
"""

# to run as script, set the execution folder to practicon

try:
    import sys
    import os
    sys.path.append(os.sep.join(__file__.split(os.sep)[:-2]))
    from check_matrix import CheckMatrix
    from tests.custom_json import conv
except ImportError:
    from practicon import CheckMatrix
    from .custom_json import conv

import pytest
import numpy as np
import json

def test_matrix():

    # no variable found, runtimewarning
    check1 = CheckMatrix('a', 0.1, 0.00)
    check2 = CheckMatrix('b', 0.1, 0.00)
    check3 = CheckMatrix('a', 0.0, 0.15)
    check4 = CheckMatrix('a', 0.1111111111111111, 0.1500012121212, 1)

    # reference function
    def myfunc(variant: int):
        return {'a': np.eye(2) + np.matrix(((0, 1), (0, 0))) * variant,
                'b1': np.ones((3,)) + variant,
                'b2': np.ones((3, 1)) + variant}

    # generate encoding
    ref = check1.encode(5, myfunc)

    # when no answer found, this should raise a runtime warning
    with pytest.raises(RuntimeWarning):
        check2(0, ref, locals())

    # fail for incorrect/unreadable
    a = (2, 3)
    assert check1(0, ref, locals())[1] == 0.0

    # set back to normal
    a = conv(np.eye(2))

    tol = np.array([[0.1, 0.1], [0.1, 0.1]])

    # succeed for all in range
    for v in range(1, 5):
        testname, score, result, sa, modelanswer = check1(v, ref, locals())
        assert testname == "Matrix 'a'"
        assert score == 0.0
        assert result == "1 incorrect elements"
        ma_ref = "{v10}\n(± {tol})".format(
            v10=myfunc(v)['a'], tol=tol)
        assert(modelanswer == ma_ref)

    # correct answer
    testname, score, result, sa, modelanswer = check1(0, ref, locals())
    assert testname == "Matrix 'a'"
    assert score == 1.0
    assert result == "answer is correct"
    # assert modelanswer == "Reference 10 (± 0.1)"

    # ratio test
    testname, score, result, sa, modelanswer = check3(0, ref, locals())
    assert score == 1.0
    # assert modelanswer == "Reference 10 (± 1.5)"

    # accept one failing for partial score
    a[0][1] = 10
    testname, score, result, sa, modelanswer = check4(0, ref, locals())
    assert score == 0.5
    # assert modelanswer == "Reference 10 (± 1.5)"

    checkb1 = CheckMatrix('b1', 0.01, 0.01)
    checkb2 = CheckMatrix('b2', 0.01, 0.01)
    refb1 = checkb1.encode(5, myfunc)
    refb2 = checkb2.encode(5, myfunc)
    ab1 = np.ones((3,)) + 1
    ab2 = np.ones((3, 1)) + 2
    ab3 = np.ones((4,))
    testname, score, result, sa, modelanswer = checkb1(1, refb1, dict(b1=ab1))
    assert score == 1
    testname, score, result, sa, modelanswer = checkb1(2, refb2, dict(b1=ab2))
    assert score == 1
    testname, score, result, sa, modelanswer = checkb2(2, refb1, dict(b2=ab2))
    assert score == 1
    testname, score, result, sa, modelanswer = checkb2(1, refb2, dict(b2=ab1))
    assert score == 1
    testname, score, result, sa, modelanswer = checkb2(2, refb2, dict(b2=a))
    assert score == 0
    assert result == "incorrect matrix size"
    testname, score, result, sa, modelanswer = check4(0, ref, dict(a=ab3))
    assert score == 0
    assert result == "incorrect matrix shape"


if __name__ == '__main__':
    test_matrix()
