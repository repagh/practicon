#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 12 15:18:33 2020

@author: repa
"""

try:
    from practicon import CheckStateSpace
except ImportError:
    import sys
    import os
    sys.path.append(os.sep.join(__file__.split(os.sep)[:-2]))
    from check_statespace import CheckStateSpace

from control import TransferFunction
import pytest
import numpy as np
from control import StateSpace, ss2tf, tf2ss
from scipy.linalg import schur


def test_statespace():
    """Test CheckStateSpace. """

    # reference function
    def myfunc(variant: int):
        """Generate test systems. """
        A = np.array((0, 0, 0,
                      1, 0, -0.9215,
                      0, 1, -0.738)).reshape((3, 3))
        B = np.array((1+0.1*variant, 0, 0)).reshape((3, 1))
        C = np.array((0, 0.151, -0.6732)).reshape((1, 3))
        D = np.zeros((1, 1))

        sys1 = StateSpace(A, B, C, D)

        sys2 = tf2ss(ss2tf(sys1))

        As, Z = schur(A)
        Bs = Z.T @ B
        Cs = C @ Z
        Ds = D
        # print(Bs)
        sys3 = StateSpace(As, Bs, Cs, Ds)

        Ds[0, 0] = 0.3
        sys4 = StateSpace(As, Bs, Cs, Ds)
        Ds[0, 0] = 0

        Ab = np.zeros((4, 4))
        Ab[:3, :3] = A
        Bb = np.zeros((4, 1))
        Bb[:3, :] = B
        Cb = np.zeros((1, 4))
        Cb[:, :3] = C
        sys5 = StateSpace(Ab, Bb, Cb, D)
        #sys5.A = Ab
        #sys5.B = Bb
        #sys5.C = Cb
        return locals()

    check1 = CheckStateSpace('sys1', 0.01, 0.01, 3)
    ref1 = check1.encode(3, myfunc)

    # answer not present
    with pytest.raises(RuntimeWarning):
        check1(0, ref1, locals())

    # wrong type for answer
    sys1 = 'adfa'
    testname, score, result, modelanswer = check1(0, ref1, locals())
    assert score == 0.0
    assert result == 'not a valid state-space system'

    # correct answer
    sys1 = myfunc(0)['sys1']
    testname, score, result, modelanswer = check1(0, ref1, locals())
    assert score == 1.0
    assert result == 'answer is correct'

    # modified, but still same function
    testname, score, result, modelanswer = check1(
        0, ref1, dict(sys1=myfunc(0)['sys2']))
    assert score == 1.0

    # Schur modified, but still same function
    testname, score, result, modelanswer = check1(
        0, ref1, dict(sys1=myfunc(0)['sys3']))
    assert score == 1.0

    # D matrix affected
    testname, score, result, modelanswer = check1(
        0, ref1, dict(sys1=myfunc(0)['sys4']))
    assert score == 0.75
    assert result == '1 incorrect elements in D matrix'

    # improperly reduced; does not work because StateSpace is so
    # efficient!
    sys5 = myfunc(0)['sys5']
    # print(sys5)
    testname, score, result, modelanswer = check1(
        0, ref1, dict(sys1=sys5))
    # assert score == 0.5
    # assert result == 'system is not minimal realization'


if __name__ == '__main__':
    test_statespace()
