#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 16 20:21:14 2020 .

@author: repa
"""


from control import TransferFunction, tf2ss
import numpy as np

a = 5
s = TransferFunction.s
tf = (1+ s)/(s**3+3*s**2+2*s +17)
I = np.eye(3)*a
sys = tf2ss(tf)

'''
student id:       4
student username: rvanpaassen
'''

# import libraries with desired types
import control
import numpy
import json

# extend a json serializer
class PRJSONEncoder(json.JSONEncoder):
    def default(self, obj):
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
encoder = PRJSONEncoder()

# copy variables left by the student, prevent accidental clash with variable
# names in this script
__student_dict__ = {}
for k, v in locals().copy().items():
    if k[:2] != '__':
        try:
            encoder.encode(v)
            __student_dict__[k] = v
        except TypeError:
            print("'{}' cannot be serialised with JSON".format(k))

# print variables as a json struct
print('\n<#@1234509876@#>')
print(encoder.encode(__student_dict__))
