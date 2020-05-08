#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu May  7 23:16:09 2020 .

@author: repa
"""
from control import TransferFunction

from base64 import b64encode, b64decode
import json
import numpy as np


class CheckTransferFunction:
    """Generate check codes and check answers."""

    @staticmethod
    def _cleanup(num):
        eps = 1e-13
        num[np.abs(num) < eps*np.max(np.abs(num))] = 0.0
        fnz = np.where(num != 0.0)[0][0]
        return num[fnz:]

    @staticmethod
    def _zpk(num, den):
        num = CheckTransferFunction._cleanup(num)
        den = CheckTransferFunction._cleanup(den)
        nlnz = np.where(num != 0.0)[0][-1]
        dlnz = np.where(den != 0.0)[0][-1]
        k = num[nlnz]/den[dlnz]
        z = np.roots(num)
        p = np.roots(den)
        return z, p, k

    def __init__(self, var: str,
                 d_abs: float = 0.0, d_rel: float = 0.0):
        """
        Create a transfer function check object.

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

        """
        self.var = var
        self.d_abs = d_abs
        self.d_rel = d_rel

    def __call__(self, variant: int, codeddata: str, _globals: dict):
        """
        Check transfer function within range.

        This checks the variable defined in the constructor against
        a reference value in the codeddata.

        Parameters
        ----------
        variant : int
            Variant of the answer.
        codeddata : str
            Encoded answer array.
        _globals : dict
            Dictionary with the answer variable

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

        # get the tf. If this throws, show mercy and let student provide
        # the variable
        try:
            tf = _globals[self.var]
        except KeyError:
            raise RuntimeWarning(
                "Transfer function {} not found".format(self.var))

        result = []
        score = 1.0
        try:
            assert isinstance(tf, TransferFunction)
            assert len(tf.den) == 1 and len(tf.den[0]) == 1
            assert len(tf.num) == 1 and len(tf.num[0]) == 1
            num, den = tf.num[0][0], tf.den[0][0]
            num, den = self._cleanup(num), self._cleanup(den)

            ref_num = np.array(ref['num'])
            ref_den = np.array(ref['den'])

            if len(num) != len(ref_num):
                result.append('numerator order incorrect')
            if len(den) != len(ref_den):
                result.append('denominator order incorrect')

            # cannot continue checking with incorrect orders
            z, p, k = self._zpk(num, den)
            ref_z, ref_p, ref_k = self._zpk(ref_num, ref_den)

            # fix for cases where no zeros (or no poles?) in student tf
            z, p = z.tolist(), p.tolist()

            nzwrong, nztest = max(len(num) - len(ref_num), 0), 0
            npwrong, nptest = max(len(den) - len(ref_den), 0), 0
            for _z in ref_z:
                if _z.imag >= 0.0:
                    nztest += 1
                    tol = max(self.d_abs, abs(self.d_rel*_z))
                    for i in range(len(z)):
                        if abs(_z-z[i]) <= tol:
                            del z[i]
                            break
                    else:
                        nzwrong += 1

            for _p in ref_p:
                if _p.imag >= 0.0:
                    nptest += 1
                    tol = max(self.d_abs, abs(self.d_rel*_p))
                    for i in range(len(p)):
                        if abs(_p-p[i]) <= tol:
                            del p[i]
                            break
                    else:
                        npwrong += 1

            tol = max(self.d_abs, abs(self.d_rel*ref_k))
            score = 1.0
            if abs(k - ref_k) > tol:
                score -= 0.5
                result.append('gain is incorrect')

            if nztest and nzwrong:
                score -= 1.2 * nzwrong / (nztest + nptest)
                s = (nzwrong > 1 and "s") or ""
                result.append('{nzwrong} zero{s} or zero-pair{s}'
                              ' incorrect or missing'.format(**locals()))
            if nptest and npwrong:
                score -= 1.5 * npwrong / (nptest + nztest)
                s = (npwrong > 1 and "s") or ""
                result.append('{npwrong} pole{s} or pole-pair{s}'
                              ' incorrect or missing'.format(**locals()))

            return (
                "Check transfer function '{}'".format(self.var),
                max(round(score, 3), 0.0),
                (result and ', '.join(result)) or
                'answered correctly',
                TransferFunction(
                    ref['num'], ref['den'], ref['dt'])._repr_latex_())

        except Exception as e:
            raise RuntimeError("Cannot check {var}: {e}".format(
                var=self.var, e=str(e)))

    def encode(self, maxvariant: int, fn):
        """
        Generate reference data for answer & variants.

        Parameters
        ----------
        maxvariant : int
            Maximum value of the variants, variants
            range 0..maxvariant.
        fn : function
            Calculates reference data, given a variant.

        Returns
        -------
        refdata : str
            Encoded reference data.
        """
        # generate for all variants
        ref = []
        for v in range(maxvariant+1):
            res = fn(v)
            tf = res[self.var]
            num, den, dt = tf.num[0][0], tf.den[0][0], tf.dt
            num, den = self._cleanup(num), self._cleanup(den)
            ref.append(dict(num=num.tolist(), den=den.tolist(), dt=dt))

        enc = json.JSONEncoder(ensure_ascii=True)
        return b64encode(enc.encode(ref).encode('ascii')).decode('ascii')
