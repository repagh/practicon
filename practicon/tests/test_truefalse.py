#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test the True/False question type.

Created on Mon May 18 16:46:33 2020

@author: repa
"""

from practicon import CheckTrueFalse

import pytest

def test_truefalse():
    """Test CheckTrueFalse."""
    
    # reference function
    def myfunc(variant: int):
        b = variant % 2 == 0
        return locals()
    
    check1 = CheckTrueFalse('b')
    ref1 = check1.encode(3, myfunc)
    
    # no answer
    with pytest.raises(RuntimeWarning):
        check1(0, ref1, locals())
        
    # wrong answer
    b = False
    testname, score, result, sa, ma = check1(0, ref1, locals())
    assert testname == "TrueFalse 'b'"
    assert score == 0.0
    assert result == "answer is wrong"
    assert sa == "False"
    assert ma == "True"
    
    testname, score, result, sa, ma = check1(1, ref1, locals())
    assert testname == "TrueFalse 'b'"
    assert score == 1.0
    assert result == "answer is correct"
    assert sa == "False"
    assert ma == "False"
     
    
if __name__ == '__main__':
    test_truefalse()
