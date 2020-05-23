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
import zlib as cmpr
from .matrixparser import parseMatrix


class CheckMatrix:
    """Generate check codes and check answers."""

    def __init__(self, var: str,
                 d_abs: float = 0.0, d_rel: float = 0.0, threshold: int = 0,
                 elts=None):
        """Create a Matrix value check object.

        Parameters
        ----------
        var : str
            Variable name to check. If this contains (start/ends with a) a
            comma (','), the matrix is parsed from a string with Python or
            Matlab syntax.
        d_abs : float, optional
            Absolute error margin.
        d_rel : float, optional
            Relative error margin.
        threshold : int, optional
            Determines how many elements of the matrix may be erroneous for
            partial score. E.g., 3 means one missing/erroneous element gives
            a score of 0.75, beyond 3 score will be zero. A transposed shape
            will also count as one erroneous element.
        elts : str, optional
            Alternative name for composing the var object a string variables,
            This uses parsing with Matlab or Python compatibility. Note that
            the name "var" is still used for creating the reference data,
            and that it will be a first candidate for the user's answer.
            Let "var" start with "_", to force the user to enter individual
            matrices.

        Returns
        -------
        None.

        Create a check object
        >>> check = CheckMatrix('var', 0.01)

        """
        if elts is not None:
            if not elts.isidentifier():
                raise ValueError("Incorrect variable name '{}'".format(elts))
        if not var.isidentifier():
            raise ValueError("Incorrect variable name '{}'".format(var))

        self.var = var
        self.d_abs = d_abs
        self.d_rel = d_rel
        self.threshold = threshold
        self.elts = elts

    def _return(self, fraction, report, value, ref, tol):
        """Produce return value."""
        return ("Matrix '{var}'".format(var=self.var),
                fraction, report, str(value),
                "{ref}\n(± {tol})".format(ref=ref, tol=tol))

    def _extractValue(self, _dict: dict):
        """
        Obtain answer from student answer dictionary.

        Parameters
        ----------
        _dict : dict
            Should contain the student answer.

        Returns
        -------
        list of list of float
            Matrix answer by student.

        """
        if self.var[0] != '_' or self.elts is None:
            try:
                return _dict[self.var]
            except KeyError:
                if self.elts is None:
                    raise RuntimeWarning(
                        "variable {var} not found".format(var=self.var))

        # second attempt, individual elements to be parsed
        try:
            return parseMatrix(self.elts, "{} = {}".format(
                self.elts, _dict[self.elts]))
        except KeyError:
            if self.var[0] != '_':
                raise RuntimeWarning(
                    "variable '{}' nor string matrix {} found"
                    "".format(self.var, self.elts))
            else:
                raise RuntimeWarning(
                    "matrix {} not found".format(self.elts))
        except ValueError as v:
            raise RuntimeWarning(str(v))

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
        studentanswer : str
            Student answer, as interpreted
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
        value = np.array(self._extractValue(_globals))

        if ref.shape != value.shape:
            # accept 1d answers vs column or row ref, or the reverse
            if len(ref.shape) != len(value.shape) and \
                np.count_nonzero(np.array(ref.shape) != 1) == 1 and \
                    np.count_nonzero(np.array(value.shape) != 1) == 1:
                ref.size == value.size
                value.reshape(ref.shape)
            elif ref.size != value.size:
                return self._return(
                    0.0, "incorrect matrix size",
                    value, ref, tol)
            elif ref.shape == value.T.shape:
                fails += 1
                result.append("matrix is transposed")
                value = value.transpose()
            else:
                return self._return(
                    0.0, "incorrect matrix shape",
                    value, ref, tol)

        try:
            nfails = np.count_nonzero(np.abs(ref - value) > tol)
            if nfails:
                result.append("{nfails} incorrect elements"
                              "".format(nfails=nfails))
            fails += nfails
        except Exception:
            return self._return(
                0.0, "cannot check variable as matrix",
                value, ref, tol)

        score = max(
            round((self.threshold + 1 - fails) / (self.threshold + 1), 3), 0.0)
        good = fails == 0
        return self._return(
            score,
            (good and "answer is correct") or "\n".join(result),
            value, ref, tol)

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
