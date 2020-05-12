#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 12 10:01:06 2020 .

@author: repa
"""

import json
from math import log10
import numpy as np
from scipy import signal
from control import StateSpace, minreal, ss2tf, tf2ss
from scipy.linalg import schur

class ZPK:
    '''Zero-Pole-Gain representation for checking'''

    def __init__(self, z, p, k, num):
        '''Create a ZPK object
            
        
        
        '''
        self.z = z
        self.p = p
        self.k = k
        self.num = num

    def check(self, other, im, ip, within_tolerance):
        
        report = []
        if self.p.shape != other.p.shape or \
            not within_tolerance(self.p, other.p):
            report.append("Dynamics/eigenvalues differ for "
                          "input {im} to output {ip}".format(im=im+1, ip=ip+1))
            
        if ((self.z.shape != other.z.shape) or 
            (self.z.size != 0 and (not within_tolerance(self.z, other.z))) or 
            (not within_tolerance(self.k, other.k))):
            report.append("Numerator/gain does not match, {im} -> {ip}"
                          "".format(im=im+1, ip=ip+1))
        return not report, report 


def ss_to_zpk(A, B, C):
    '''Convert a state-space system to sets of Zero-Pole-Gain objects
        
    Parameters
    ---------
    A: (n,n) array_like
        State-space dynamics matrix
    B: (n,m) array_like
        Input matrix.
    C: (n,m) array_like
        Output matrix
    '''   
    zpks = []
    for im in range(B.shape[1]):
        zpks.append([])
        for ip in range(C.shape[0]):
            try:
                num, den = signal.ss2tf(
                    A, B[:, im].reshape((-1,1)), 
                    C[ip,:].reshape((1,-1)), np.zeros((1, 1)))
                nu2 = num
                
                # strip leading (close to zeros) from num
                while np.allclose(nu2[:,0], 0, 1e-14) and \
                    nu2.shape[-1] > 1:
                    nu2 = nu2[:,1:]
                    
                # to zpk
                z, p, k = signal.tf2zpk(nu2, den)
                zpks[-1].append(ZPK(z, p, k, num))
            except ValueError:
                raise RuntimeWarning("cannot analyse state-space")
    return zpks


class CheckStateSpace:
    """Generate check codes and check answers."""

    def __init__(self, var: str,
                 d_abs: float = 0.0, d_rel: float = 0.0, threshold: int = 0):
        """
        Create a Matrix value check object.

        Parameters
        ----------
        var : str
            Variable name to check.
        d_abs : float, optional
            Absolute error margin.
        d_rel : float, optional
            Relative error margin.
        threshold : int, optional
            Determines how many elements of the matrix may be erroneous for
            partial score. E.g., 3 means one missing/erroneous element gives
            a score of 0.75, beyond 3 score will be zero. A transposed shape
            will also count as one erroneous element.

        Returns
        -------
        None.

        Create a check object
        >>> check = CheckMatrix('var', 0.01)

        A function to calculate the answer values, for different variants
        >>> def myfun(variant):
        ...    return { 'var' : 5 + variant }

        Create the encoded answers for all variants
        >>> ref = check.encode(3, myfun)

        Check against a trial value for a specific variant
        >>> var = 5.01
        >>> testname, score, result, modelanswer = check(0, ref, locals())
        >>> print(score)
        1.1

        """
        self.var = var
        self.d_abs = d_abs
        self.d_rel = d_rel
        self.threshold = threshold

    def __call__(self, variant: int, codeddata: str, _globals: dict):
        """
        Check whether a given answer is within tolerance.

        This checks the variable defined in the constructor against
        a reference value in the codeddata.

        Parameters
        ----------
        variant : int
            Variant of the answer.
        codeddata : str
            Encoded answer array.

        Returns
        -------
        testname : str
            Short name for the test
        score : float
            Normalized score, 0 or 1
        result : str
            Text describing the result
        modelanswer : str
            Reference answer
        """
        dec = json.JSONDecoder()
        Aref, Bref, Cref, Dref = map(np.array, dec.decode(codeddata)[variant])
        sys_ref = StateSpace(Aref, Bref, Cref, Dref)

        # checking function
        def within_tolerance(xr, x):
            return np.allclose(xr, x, self.d_rel, self.d_abs)
        
        ref = ss_to_zpk(Aref, Bref, Cref)
        
        fails = 0        
        try:
            value = _globals[self.var]
        except KeyError:
            raise RuntimeWarning(
                "Variable {var} not found".format(var=self.var))
        report = []
        try:
            A = value.A
            B = value.B
            C = value.C
            D = value.D
            if A.shape != Aref.shape:
                value = minreal(value)
                A = value.A
                B = value.B
                C = value.C
                if A.shape == Aref.shape:
                    fails += round(self.threshold / 2)
                    report.append('system is not minimal realization')
            if A.shape != Aref.shape:
                fails += self.threshold
                report.append('incorrect system order')
            if B.shape[1] != Bref.shape[1]:
                fails += self.threshold
                report.append('incorrect number of inputs')
            if C.shape[0] != Cref.shape[0]:
                fails += self.threshold
                report.append('incorrect number of outputs')
            
            if fails >= self.threshold:
                return ("Check result '{var}'".format(var=self.var),
                        0.0,
                        '<br/>'.join(report),
                        "Reference {ref}".format(ref=ref))

            # d matrix
            ndfail = Dref.size - \
                np.sum(np.isclose(Dref, D, self.d_rel, self.d_abs))
            if ndfail:
                report.append('{ndfail} incorrect elements in D matrix'
                              ''.format(ndfail=ndfail))
                fails += ndfail

            # orders/sizes correct, can now check transfers
            zpk_ref = ss_to_zpk(Aref, Bref, Cref)
            zpk_val = ss_to_zpk(A, B, C)            
            for im in range(len(zpk_ref)):
                for ip in range(len(zpk_ref[0])):
                    ok, r = zpk_ref[im][ip].check(zpk_val[im][ip], im, ip, 
                                                       within_tolerance)
                    if not ok:
                        fails += 1
                        report.extend(r)
                        
        except Exception:
            return ("Check result '{var}'".format(var=self.var),
            0.0,
            "not a valid state-space system",
            "Reference {ref}".format(ref=ref))

        score = max((self.threshold + 1 - fails) / (self.threshold + 1), 0.0)
        return (
            "Check result '{var}'".format(var=self.var),
            score,
            (not report and "answer is correct") or "<br/>".join(report),
            "Reference {ref}".format(ref=sys_ref))

    def encode(self, nvariants: int, func):
        """
        Generate reference data for answer & variants.

        Parameters
        ----------
        nvariants : int
            Number of the variants.
        func : function
            Calculates reference data, given a variant.

        Returns
        -------
        refdata : str
            Encoded reference data.
        """
        # generate for all variants
        ref = []
        for _v in range(nvariants):
            res = func(_v)
            value = res[self.var]
            
            # balance the ABCD system, for robustness, to real shur form
            As, Z = schur(value.A)
            Bs = Z.T @ value.B
            Cs = value.C @ Z
            Ds = value.D
            n = As.shape[0]
            
            # round off to 2+size digits
            def tolround(x):
                tol = max(self.d_abs, abs(self.d_rel*x))
                return round(x, 2+n-int(log10(tol)))
            
            tolround = np.vectorize(tolround)
            ref.append((tolround(As).tolist(), 
                        tolround(Bs).tolist(), 
                        tolround(Cs).tolist(), 
                        tolround(Ds).tolist()))

        enc = json.JSONEncoder(ensure_ascii=True)
        return enc.encode(ref)
