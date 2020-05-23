#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check state-space systems.

Created on Tue May 12 15:18:33 2020

@author: repa
"""

from practicon import CheckStateSpace, conv

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
        # sys5.A = Ab
        # sys5.B = Bb
        # sys5.C = Cb
        return locals()

    check1 = CheckStateSpace('sys1', 0.01, 0.01, 3)
    ref1 = check1.encode(3, myfunc)

    # answer not present
    with pytest.raises(RuntimeWarning):
        check1(0, ref1, locals())

    # wrong type for answer, now also runtime warning
    sys1 = 'adfa'
    testname, score, result, sa, modelanswer = check1(0, ref1, locals())

    # correct answer
    sys1 = conv(myfunc(0)['sys1'])
    testname, score, result, sa, modelanswer = check1(0, ref1, locals())
    assert score == 1.0
    assert result == 'answer is correct'
    # print(sa, modelanswer)
    assert sa == modelanswer

    # modified, but still same function
    testname, score, result, studentanswer, modelanswer = check1(
        0, ref1, dict(sys1=conv(myfunc(0)['sys2'])))
    assert score == 1.0

    # Schur modified, but still same function
    testname, score, result, sa, modelanswer = check1(
        0, ref1, dict(sys1=conv(myfunc(0)['sys3'])))
    assert score == 1.0

    # D matrix affected
    testname, score, result, sa, modelanswer = check1(
        0, ref1, dict(sys1=conv(myfunc(0)['sys4'])))
    assert score == 0.75
    assert result == '1 incorrect elements in D matrix'

    # improperly reduced; does not work because StateSpace is so
    # efficient!
    sys5 = conv(myfunc(0)['sys5'])
    # print(sys5)
    testname, score, result, sa, modelanswer = check1(
        0, ref1, dict(sys1=sys5))
    # assert score == 0.5
    # assert result == 'system is not minimal realization'

    def myfunc2(variant: int):
        s = TransferFunction.s
        tf = (1+ 0.5*s)/(s**3+3*s**2+2*s +17)
        sysx = tf2ss(tf)
        return locals()
    
    check6 = CheckStateSpace('sysx', 0.01, 0.01, 1)
    ref6 = check6.encode(1, myfunc2)
    testname, score, result, sa, modelanswer = check6(
        0, ref6, dict(sysx=conv(myfunc2(0)['sysx'])))
    assert score == 1.0
    # print(result, sa, modelanswer)

    def myfunc3(variant: int):
        s = TransferFunction.s
        tf = (1+ 0.5*s)/(s**3+3*s**2+2*s +17)
        sysx = tf2ss(tf)
        A = str(sysx.A.tolist())
        B = str(sysx.B.tolist())
        C = str(sysx.C.tolist())
        D = str(sysx.D.tolist())
        return locals()

    check7 = CheckStateSpace('sysx', 0.01, 0.01, 1, ('A', 'B', 'C', 'D'))
    ref7 = check7.encode(1, myfunc3)
    testname, score, result, sa, modelanswer = check7(
        0, ref7, dict(
            A=conv(myfunc3(0)['A']), B=conv(myfunc3(0)['B']),
            C=conv(myfunc3(0)['C']), D=conv(myfunc3(0)['D'])))
    assert score == 1.0
    # print(result, sa, modelanswer)

if __name__ == '__main__':
    test_statespace()
