#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check True/False values.

Created on Mon May 18 16:30:29 2020

@author: repa
"""
from base64 import b64encode, b64decode
import json


class CheckTrueFalse:
    """Generate check codes and check answers."""

    def __init__(self, var: str):
        """Create a bool check object.

        Parameters
        ----------
        var : str
            Variable name to check.

        Returns
        -------
        None.

        """
        self.var = var

    def _return(self, fraction, report, value, ref):
        """Produce check return value."""
        return ("TrueFalse '{var}'".format(var=self.var),
                fraction,
                report,
                str(value),
                str(ref))

    def __call__(self, variant: int, codeddata: str, _globals: dict):
        """
        Check logical value against reference.

        Parameters
        ----------
        variant : int
            Variant of the answer.
        codeddata : str
            Encoded answer array.
        _globals : dict
            Dictionary with the answer variable.

        Returns
        -------
        testname : str
            Short name for the test
        score : float
            Normalized score, 0 or 1
        result : str
            Text describing the result
        studentanswer : str
            Student's answer, as interpreted
        modelanswer : str
            Reference answer

        """
        dec = json.JSONDecoder()
        ref = dec.decode(b64decode(codeddata.encode('ascii')).
                         decode('utf-8'))[variant]

        try:
            tf = _globals[self.var]
        except KeyError:
            raise RuntimeWarning(
                "TrueFalse {} not found".format(self.var))
        try:
            tf = bool(tf)
        except Exception:
            return self._return(
                0.0, "not a true/false object", tf, ref)

        if tf == ref:
            return self._return(
                1.0, "answer is correct", tf, ref)
        return self._return(
            0.0, "answer is wrong", tf, ref)

    def encode(self, nvariants: int, fn):
        """
        Generate reference data for answer & variants.

        Parameters
        ----------
        nvariants : int
            Number of different variants.
        fn : function
            Calculates reference data, given a variant.

        Returns
        -------
        refdata : str
            Encoded reference data.

        """
        # generate for all variants
        ref = []
        for v in range(nvariants):
            res = fn(v)[self.var]
            ref.append(res)

        enc = json.JSONEncoder(ensure_ascii=True)
        return b64encode(
            enc.encode(ref).encode('utf-8')).decode('ascii')
