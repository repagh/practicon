#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  7 22:18:06 2020 .

@author: repa
"""

from base64 import b64encode, b64decode
import json
from math import log10


class CheckNumeric:
    """Generate check codes and check answers."""

    def __init__(self, var: str,
                 d_abs: float = 0.0, d_rel: float = 0.0):
        """
        Create a numeric value check object.

        Parameters
        ----------
        var : str
            Variable name to check.
        d_abs : float
            Absolute error margin.
        d_rel : float, optional
            Relative error margin.

        Returns
        -------
        None.

        Create a check object
        >>> check = CheckNumeric('var', 0.01)

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

    def __call__(self, variant: int, codeddata: str, _globals: dict):
        """
        Check whether a given answer is within a numeric range.

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
        ref = dec.decode(b64decode(codeddata).decode('ascii'))[variant]
        tol = max(self.d_abs, abs(self.d_rel*ref))
        tol = round(tol, 2-int(log10(tol)))
        try:
            value = _globals[self.var]
        except KeyError:
            raise RuntimeWarning(
                "Variable {} not found".format(self.var))

        try:
            good = abs(ref - value) < tol
        except Exception as exc:
            raise RuntimeError(
                "Cannot check {var}: {exc}".format(
                    dict(var=self.var, exc=str(exc))))

        return (
            "Check result '{}'".format(self.var),
            1.0*good,
            (good and "Answer is correct") or "Answer is incorrect",
            "Reference {ref} (± {tol})".format(locals()))

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
            tol = max(self.d_abs, abs(self.d_rel*value))
            value = round(value, 2-int(log10(tol)))
            ref.append(value)

        enc = json.JSONEncoder(ensure_ascii=True)
        return b64encode(enc.encode(ref).encode('ascii')).decode('ascii')
