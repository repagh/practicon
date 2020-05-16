#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May 16 20:45:54 2020

@author: repa
"""


__student_program__ = r"""
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
"""

import json
import sys
import subprocess
from practicon import CheckNumeric, CheckTransferFunction, \
    CheckMatrix, CheckStateSpace
from control import TransferFunction, StateSpace

# figure out if we need to generate reference or run student code and test
complete = True
ref = 68
complete = complete and ref > 0
ref = 136
complete = complete and ref > 0
ref = 268
complete = complete and ref > 0
ref = 100
complete = complete and ref > 0

# if complete, run the student's code
if complete:

    output = []
    failed = True
    try:
        outcome = subprocess.run(
            ['python3', '-c', __student_program__],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout = 2, # 2 second timeout MUST BE LESS THAN DEFAULT FOR QUESTION TYPE
            universal_newlines=True,
            check=True
        )
        
        if outcome.stderr:
            output.append("*** Error output ***\n")
            output.extend(('<pre>', outcome.stderr, '</pre>'))

        __student_dict__ = json.loads(
            outcome.stdout.split('\n<#@1234509876@#>\n')[-1])
        failed = False
    
    except subprocess.CalledProcessError as e:
        output.append("Task failed: {}".format(e))
    except subprocess.TimeoutExpired as e:
        output.append("Task timed out: {}".format(e))
    except Exception as e:
        output.append("Error when reading process output: {}".format(e))

if failed:
    print(json.dumps({ 'fraction': 0.0, 'testresults': [], 
        'epiloguehtml': '<br>'.join(output) }))
    sys.exit(1)
    

#"""
#{x { dump() } x}
#"""

# load the configuration parameters
parameters = json.loads("""{"nvariants":3,"variant":1,"answerfeedback":1,"tau":[0.40000000000000002,0.5,0.69999999999999996]}""")

# function with the question reference code
from control import TransferFunction, tf2ss
import numpy as np

def ref_answer(variant):
    a = 5 + variant*0.2
    tau = parameters['tau'][variant]
    s = TransferFunction.s
    tf = (1+tau*s)/(s**3+3*s**2+2*s +17)
    I = np.eye(3)*a
    sys = tf2ss(tf)
    return locals()

# variant, if defined, selects a specific question configuration
variant = "1"
variant = (variant and int(variant)) or 0
nvariants = "3"
nvariants = (nvariants and int(nvariants)) or 1

sum_score, sum_points = 0.0, 0.0
is_precheck = 1
display_feedback = 1
hide_result = is_precheck or (not display_feedback) 


# room for the result object
if complete:
    __result = {
        'testresults':
        [ ['iscorrect', 'testcode', 'got', 'awarded', 'expected'] ]
    }
else:
    __result = {
        'fraction': 1.0,
        'testresults':
        [[ 'got' ]]
    }
    
ref = """QlpoOTFBWSZTWY9Xrf4AAAaaAEAFVgAACiAAIZBk0IMmIoZrKPMSeLuSKcKEhHq9b/A="""
check = CheckNumeric('a', 0.1, 0.01)

# if refs not empty, we are in question asking mode. Check each answer
if complete:
    try:
        sum_points += 1.000
        testname, score, result, modelanswer = check(
            variant, ref, __student_dict__)
        if hide_result:
            okmark = None
        else:
            okmark = score == 1.0
        # modify transfer function
        if modelanswer[0] == '\n':
            modelanswer = "({0})/({2})".format(
                *map(str.strip, modelanswer.strip().split('\n')))
            
        __result['testresults'].append(
            [ okmark, 
              testname, 
              (hide_result and "variable exists") or result, 
              (hide_result and "hidden") or score, 
              (hide_result and "--") or modelanswer])
              
        sum_score  += 1.000 * score

    except RuntimeWarning as e:
        __result['testresults'].append(
            [ False,
              "Check '{}'".format(check.var),
              "missing variable",
              (hide_result and "hidden") or 0.0,
              '--'
            ])

else:
        
    # generate coded answer strings
    _ref = check.encode(nvariants, ref_answer)
    __result['testresults'].append([_ref])
    
ref = """QlpoOTFBWSZTWSzPE/kAAEcbgFAFfpAACgYDBgogAHBRoyBo0yNBFIp6mAHpGlB2YBgYLst2w+sjz13whg7ZZGzZlC7A7tGAaNm6FR3/jr+Hxw4atWXbQzfhdyRThQkCzPE/kA=="""
check = CheckTransferFunction('tf', 0.01, 0.001)

# if refs not empty, we are in question asking mode. Check each answer
if complete:
    try:
        sum_points += 1.000
        testname, score, result, modelanswer = check(
            variant, ref, __student_dict__)
        if hide_result:
            okmark = None
        else:
            okmark = score == 1.0
        # modify transfer function
        if modelanswer[0] == '\n':
            modelanswer = "({0})/({2})".format(
                *map(str.strip, modelanswer.strip().split('\n')))
            
        __result['testresults'].append(
            [ okmark, 
              testname, 
              (hide_result and "variable exists") or result, 
              (hide_result and "hidden") or score, 
              (hide_result and "--") or modelanswer])
              
        sum_score  += 1.000 * score

    except RuntimeWarning as e:
        __result['testresults'].append(
            [ False,
              "Check '{}'".format(check.var),
              "missing variable",
              (hide_result and "hidden") or 0.0,
              '--'
            ])

else:
        
    # generate coded answer strings
    _ref = check.encode(nvariants, ref_answer)
    __result['testresults'].append([_ref])
    
ref = """QlpoOTFBWSZTWUXGJxkAAQDaAEAAQAd/4AAKMAD4AoaaYAChppgAG1CGmSamT37AAt0fhx1Zw8HJAV0hi3TmBC2fDiTmyiDqJRPWcSYcZDEHg2adfkQr6ZYyYLg9NZNztrRgqD4oY2sPE7MXweJOosg0aIKGEmyWb2jYw6Mlj+Gkn5tGdPONJUYNGMHDdEjOEEFkFTogmjOis6GOHJneSyYMaKNNw6l0ZMhhhkmGTIZl+98PShyEiRy/bycP4u5IpwoSCLjE4yA="""
check = CheckStateSpace('sys', 0.01, 0.01)

# if refs not empty, we are in question asking mode. Check each answer
if complete:
    try:
        sum_points += 1.000
        testname, score, result, modelanswer = check(
            variant, ref, __student_dict__)
        if hide_result:
            okmark = None
        else:
            okmark = score == 1.0
        # modify transfer function
        if modelanswer[0] == '\n':
            modelanswer = "({0})/({2})".format(
                *map(str.strip, modelanswer.strip().split('\n')))
            
        __result['testresults'].append(
            [ okmark, 
              testname, 
              (hide_result and "variable exists") or result, 
              (hide_result and "hidden") or score, 
              (hide_result and "--") or modelanswer])
              
        sum_score  += 1.000 * score

    except RuntimeWarning as e:
        __result['testresults'].append(
            [ False,
              "Check '{}'".format(check.var),
              "missing variable",
              (hide_result and "hidden") or 0.0,
              '--'
            ])

else:
        
    # generate coded answer strings
    _ref = check.encode(nvariants, ref_answer)
    __result['testresults'].append([_ref])
    
ref = """QlpoOTFBWSZTWUsy8i4AAEiaAEAFVgAACiAAVCU9KZNAiKBpBHW+ULahgHqyKxfC44ySSLUqQUUBBMwpp2b8XckU4UJBLMvIuA=="""
check = CheckMatrix('I', 0.0001, 0.0001)

# if refs not empty, we are in question asking mode. Check each answer
if complete:
    try:
        sum_points += 1.000
        testname, score, result, modelanswer = check(
            variant, ref, __student_dict__)
        if hide_result:
            okmark = None
        else:
            okmark = score == 1.0
        # modify transfer function
        if modelanswer[0] == '\n':
            modelanswer = "({0})/({2})".format(
                *map(str.strip, modelanswer.strip().split('\n')))
            
        __result['testresults'].append(
            [ okmark, 
              testname, 
              (hide_result and "variable exists") or result, 
              (hide_result and "hidden") or score, 
              (hide_result and "--") or modelanswer])
              
        sum_score  += 1.000 * score

    except RuntimeWarning as e:
        __result['testresults'].append(
            [ False,
              "Check '{}'".format(check.var),
              "missing variable",
              (hide_result and "hidden") or 0.0,
              '--'
            ])

else:
        
    # generate coded answer strings
    _ref = check.encode(nvariants, ref_answer)
    __result['testresults'].append([_ref])
    

# if only generating reference data, quickly return
if not complete:
    print(json.dumps(__result))
    sys.exit(0)

fraction = sum_score/sum_points
if __result.get('abort', False):
    __result['fraction'] = (hide_result and 0.00002) or 0.0
elif sum_points:
    __result['fraction'] = (
        hide_result and max(0.00002, min(fraction, 0.99998))) or fraction
else:
    __result['fraction'] = (hide_result and 0.99998) or 1.0

def tablerow(row, rowdata, lastrow=''):
    res = [ '<tr class="r{} {}">'.format(row % 2, lastrow) ]
    res.append('<td class="cell c0" style><i class="icon fa ')
    if rowdata[0] is None:
        res.append('fa-hand-o-right text-success fa-fw" title="Found"'
            ' aria-label="Found">')
    elif rowdata[0]:
        res.append('fa-check text-success fa-fw" title="Correct"'
            ' aria-label="Correct">')
    else:
        res.append('fa-remove text-danger fa-fw" title="Incorrect"'
            ' aria-label="Incorrect">')
    res.append('</i></td>')
    for c, it in enumerate(rowdata[1:-1]):
        res.append(
            '<td class="cell c{}"><pre class="tablecell">{}</pre></td>'
            ''.format(c+1, it))
    if rowdata[-1][:2] == '\(':
        res.append(
            '<td class="cell c{} lastcol><span class="tablecell">{}</span></td>'
            ''.format(len(rowdata)-1, rowdata[-1]))
    else:
        res.append(
            '<td class="cell c{} lastcol><pre class="tablecell">{}</pre></td>'
            ''.format(len(rowdata)-1, rowdata[-1]))
    res.append('</tr>')
    return ''.join(res)
    
html = [ """<div class="coderunner-test-results">
<table class="coderunner-test-results"><thead>
<tr><th class="header c0"></th><th class="header c1">Test</th>
<th class="header c2">Result</th><th class="header c3">Awarded</th>
<th class="header c4">Expected</th></tr></thead><tbody>""" ]
for i in range(1,len(__result['testresults'])):
    html.append(tablerow(i, __result['testresults'][i], 
        (i+1 == len(__result['testresults']) and " lastrow") or ""))
html.append('</tbody></table></div>')
__result['epiloguehtml'] = ''.join(html)

del __result['testresults']

print(json.dumps(__result))