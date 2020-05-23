#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Custom coder for JSON strings.

Created on Mon May 18 12:34:33 2020

@author: repa
"""

# import libraries with desired types
import control
import numpy
import json


# extend a json serializer
class PRJSONEncoder(json.JSONEncoder):
    """Extension of JSON encoder for control."""

    def default(self, obj):
        """
        Re-code transfer functions, state-space systems and numpy arrays.

        Parameters
        ----------
        obj : any
            Object to convert to JSON.

        Returns
        -------
        JSONEncoder
            Default encoder result.

        """
        if isinstance(obj, control.TransferFunction):
            return {'__class__': 'TransferFunction',
                    'num': obj.num, 'den': obj.den, 'dt': obj.dt}
        elif isinstance(obj, control.StateSpace):
            return {'__class__': 'StateSpace',
                    'A': obj.A, 'B': obj.B,
                    'C': obj.C, 'D': obj.D, 'dt': obj.dt}
        elif isinstance(obj, numpy.ndarray):
            return obj.tolist()
        elif isinstance(obj, (numpy.int64, numpy.int32, numpy.int16,
                              numpy.int8, numpy.uint64, numpy.uint32,
                              numpy.uint16, numpy.uint8)):
            return int(obj)
        elif isinstance(obj, (numpy.float64, numpy.float32)):
            return float(obj)
        elif isinstance(obj, (numpy.complex128, numpy.complex64)):
            return complex(obj)
        elif isinstance(numpy.bool_):
            return bool(obj)
        return json.JSONEncoder.default(self, obj)


# specific encoder type
encoder = PRJSONEncoder()


def conv(x):
    """
    Convert objects to JSONified version.

    Parameters
    ----------
    x : any
        Object to convert.

    Returns
    -------
    any
        Encoded/decoded version in struct/array.

    """
    return json.loads(encoder.encode(x))
