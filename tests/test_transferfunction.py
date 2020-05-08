#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  8 18:36:32 2020 .

Test the CheckNumeric class.

@author: repa
"""
from practicon import CheckTransferFunction
from control import TransferFunction
import pytest

"""
Returns
-------
None
"""
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
    with pytest.raises(RuntimeError):
        check1(0, ref, locals())
    
    # set back to normal
    a = TransferFunction([1, 1], [1, 1, 0])
    
    # succeed for all in range
    for v in range(1, 5):
        testname, score, result, modelanswer = check1(v, ref, locals())
        # print(testname, score, result, modelanswer, sep='\n')
        assert testname == "Check transfer function 'a'"
        assert score < 1.0
        assert result != "answered correctly"
        # assert modelanswer == f"Reference {10+v} (± 0.1)"
    
    # correct answer
    testname, score, result, modelanswer = check1(0, ref, locals())
    assert testname == "Check transfer function 'a'"
    assert score == 1.0
    assert result == "answered correctly"
    # assert modelanswer == f"Reference {10} (± 0.1)"
    
    # ratio test
    testname, score, result, modelanswer = check3(0, ref, locals())
    assert score == 1.0
    assert modelanswer == "$$\\frac{s + 1}{s^2 + s}$$"
    
    # incorrect number of zeros/poles
    a = TransferFunction([1], [1, 1, 1, 0])
    
    testname, score, result, modelanswer = check1(0, ref, locals())
    assert testname == "Check transfer function 'a'"
    assert score < 1.0
    assert result != "answered correctly"
    # assert modelanswer == f"Reference {10} (± 0.1)"
