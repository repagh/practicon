#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  8 18:30:45 2020 .

Test the CheckNumeric class.

@author: repa
"""

from practicon import CheckNumeric
import pytest


def test_numeric():
    # no variable found, runtimewarning
    check1 = CheckNumeric('a', 0.1, 0.00)
    check2 = CheckNumeric('b', 0.1, 0.00)
    check3 = CheckNumeric('a', 0.0, 0.15)

    # reference function
    def myfunc(variant: int):
        return {'a': 10+variant}

    # generate encoding
    ref = check1.encode(5, myfunc)

    # when no answer found, this should raise a runtime warning
    with pytest.raises(RuntimeWarning):
        check2(0, ref, locals())

    # fail for incorrect/unreadable
    a = (2, 3)
    with pytest.raises(RuntimeError):
        check1(0, ref, locals())

    # set back to normal
    a = 10

    # succeed for all in range
    for v in range(1, 5):
        testname, score, result, modelanswer = check1(v, ref, locals())
        assert testname == "Check result 'a'"
        assert score == 0.0
        assert result == "Answer is incorrect"
        assert modelanswer == "Reference {v10} (± 0.1)".format(v10=v+10)

    # correct answer
    testname, score, result, modelanswer = check1(0, ref, locals())
    assert testname == "Check result 'a'"
    assert score == 1.0
    assert result == "Answer is correct"
    assert modelanswer == "Reference 10 (± 0.1)"

    # ratio test
    testname, score, result, modelanswer = check3(0, ref, locals())
    assert score == 1.0
    assert modelanswer == "Reference 10 (± 1.5)"
