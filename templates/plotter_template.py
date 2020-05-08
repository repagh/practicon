import matplotlib
import json
import base64
import subprocess
import re
import os.path
from hashlib import sha1

def make_data_uri(filename):
    """Given a png, svg or jpeg image filename (which must end in .png, .svg or .jpg/.jpeg
       resp.) return a data URI as a UTF-8 string.
    """
    with open(filename, 'br') as fin:
        contents = fin.read()
    contents_b64 = base64.b64encode(contents).decode('utf8')
    digest = sha1(contents).hexdigest()
    if filename.endswith('.png'):
        return "data:image/png;base64,{}".format(contents_b64), digest
    elif filename.endswith('.svg'):
        return "data:image/svg;base64,{}".format(contents_b64), digest
    elif filename.endswith('.jpeg') or filename.endswith('.jpg'):
        return "data:image/jpeg;base64,{}".format(contents_b64), digest
    else:
        raise Exception("Unknown file type passed to make_data_uri")

def tweak_line_numbers(error):
    """Adjust the line numbers in the error message to account for extra lines"""
    new_error = ''
    for line in error.splitlines():
        match = re.match("(.*, line )([0-9]+)", line)
        if match:
            line = match.group(1) + str(int(match.group(2)) - len(PREFIX))
        new_error += line + '\n'
    return new_error

# Define lines of code to insert before student's code
PREFIX = """
import matplotlib
matplotlib.use('Agg')
"""

POSTFIX = """
import matplotlib.pyplot as __plt__
if __plt__.get_fignums():
    __plt__.savefig('matplotliboutput.png')
"""

expected = """{{ TEST.expected | e('py') }}"""
student_code = '\n'.join( (
PREFIX, 
"""{{ STUDENT_ANSWER | e('py') }}""",
POSTFIX) )
output = ''
failed = False

try:
    outcome = subprocess.run(
        ['python3', '-c', student_code],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout = 2, # 2 second timeout MUST BE LESS THAN DEFAULT FOR QUESTION TYPE
        universal_newlines=True,
        check=True
    )
except subprocess.CalledProcessError as e:
    outcome = e
    output = "Task failed with return code = {}\n".format(outcome.returncode)
    failed = True
except subprocess.TimeoutExpired as e:
    outcome = e
    output = "Task timed out\n"

output += outcome.stdout
if outcome.stderr:
    output += "*** Error output ***\n"
    output += tweak_line_numbers(outcome.stderr)

html = ''
digest = ''
if output:
    html += "<pre>{}</pre>".format(output)
if not failed and os.path.isfile('matplotliboutput.png'):
    data_uri, digest = make_data_uri('matplotliboutput.png')
    html += """<img class="data-uri-example" title="Matplotlib plot" src="{}" alt="matplotliboutput.png">
    """.format(data_uri)
failed = failed or expected != digest

# Lastly print the JSON-encoded result required of a combinator grader
print(json.dumps({'digest': digest, 'epiloguehtml': html, 'got': digest,
                  'fraction': 0.0 if failed else 1.0
}))
