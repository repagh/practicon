#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 12 10:01:06 2020 .

@author: repa
"""

import json
from base64 import b64encode, b64decode
from math import log10
import numpy as np
import bz2 as cmpr


class CheckMatrix:
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
        ref = np.array(dec.decode(
            cmpr.decompress(b64decode(codeddata.encode('ascii')))
            .decode('utf-8'))[variant])

        tol = np.maximum(self.d_abs, np.abs(self.d_rel*ref))

        # round of the tolerance matrix to each element 2 digits of precision
        def tolround(x):
            if x:
                return round(x, 2-int(log10(x)))
            else:
                return x
        tolround = np.vectorize(tolround)
        tol = tolround(tol)

        result = []
        fails = 0
        try:
            value = np.array(_globals[self.var])
        except KeyError:
            raise RuntimeWarning(
                "Variable {var} not found".format(var=self.var))

        if ref.shape != value.shape:
            # accept 1d answers vs column or row ref, or the reverse
            if len(ref.shape) != len(value.shape) and \
                np.count_nonzero(np.array(ref.shape) != 1) == 1 and \
                    np.count_nonzero(np.array(value.shape) != 1) == 1:
                ref.size == value.size
                value.reshape(ref.shape)
            elif ref.size != value.size:
                return ("Check result '{var}'".format(var=self.var),
                        0.0,
                        "incorrect matrix size",
                        "Reference {ref} (± {tol})".format(ref=ref, tol=tol))
            elif ref.shape == value.T.shape:
                fails += 1
                result.append("matrix is transposed")
                value = value.transpose()
            else:
                return ("Check result '{var}'".format(var=self.var),
                        0.0,
                        "incorrect matrix shape",
                        "Reference {ref} (± {tol})".format(ref=ref, tol=tol))

        try:
            nfails = np.count_nonzero(np.abs(ref - value) > tol)
            if nfails:
                result.append("{nfails} incorrect elements"
                              "".format(nfails=nfails))
            fails += nfails
        except Exception:
            return ("Check result '{var}'".format(var=self.var),
                    0.0,
                    "cannot check variable as matrix",
                    "Reference {ref} (± {tol})".format(ref=ref, tol=tol))

        score = max((self.threshold + 1 - fails) / (self.threshold + 1), 0.0)
        good = fails == 0
        return (
            "Check result '{var}'".format(var=self.var),
            score,
            (good and "Answer is correct") or "Answer is incorrect",
            "Reference {ref} (± {tol})".format(ref=ref, tol=tol))

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

            # round off to two more digits than the precision of the
            # tolerance matrix elements
            tol = np.maximum(self.d_abs, abs(self.d_rel*value))

            def tolround(x, tol):
                return round(x, 4-int(log10(tol)))

            tolround = np.vectorize(tolround)
            value = tolround(value, tol)
            ref.append(value.tolist())

        enc = json.JSONEncoder(ensure_ascii=True)
        return b64encode(
            cmpr.compress(enc.encode(ref).encode('utf-8'))).decode('ascii')
