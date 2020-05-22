# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 13:32:35 2013

@author: repa
"""
import pyparsing as PP

# basic regexes for float and complex numbers
floater = PP.Regex(r"-?\d+(\.\d*)?([Ee][+-]?\d+)?")
floater.setParseAction(lambda toks: float(toks[0]))
ifloater = PP.Regex(r"-?\d+(\.\d*)?([Ee][+-]?\d+)?[ji]")
ifloater.setParseAction(lambda toks: 1j*complex(float(toks[0][:-1])))
pluscomplex = floater + PP.Suppress(u'+') + ifloater
pluscomplex.setParseAction(lambda toks: toks[0]+toks[1])
minuscomplex = floater + PP.Suppress(u'-') + ifloater
minuscomplex.setParseAction(lambda toks: toks[0]-toks[1])
specials = PP.Literal(u'nan') | PP.Literal(u'inf') | PP.Literal(u'-inf')
specials.setParseAction(lambda toks: float(toks[0]))

# any kind of number
anumber = pluscomplex | minuscomplex | ifloater | floater | specials

# tokens
comma = PP.Suppress(',')
openlist = PP.Suppress('[')
closelist = PP.Suppress(']')
assignment = PP.Suppress('=')
rowend = PP.Suppress(';')

# contents of a python list
p_contents = PP.ZeroOrMore(anumber + comma) + PP.Optional(anumber)
p_alist = openlist + p_contents + closelist
p_alist.setParseAction(lambda toks: [toks])

# compound python list
p_listlist = openlist + PP.ZeroOrMore(p_alist + comma) + \
    p_alist + PP.Optional(comma) + closelist + PP.Optional(rowend)
p_listlist.setParseAction(lambda toks: toks)

# contents of a Matlab list
m_contents = PP.OneOrMore(anumber + PP.Optional(comma))
m_alist = PP.ZeroOrMore(m_contents + rowend) + PP.Optional(m_contents)
m_contents.setParseAction(lambda toks: [toks])
m_listlist = openlist + m_alist + rowend + closelist + rowend | \
    openlist + m_alist + closelist + rowend | \
    openlist + closelist + PP.Optional(rowend)
m_listlist.setParseAction(lambda toks: toks)


def parseMatrix(name, text, checkempty=True):
    r"""Parse Matlab or Python/Numpy style matrices entered.

    Always returns a 2-D list

    Examples
    --------
    >>> print(parseMatrix('A', 'A=[]', checkempty=False))
    []

    >>> print(parseMatrix('A', 'A=[]'))
    Traceback (most recent call last):
        ...
    ValueError: Empty matrix "A"

    >>> print(parseMatrix('A', 'A = [ 1 2 ]'))
    [[1.0, 2.0]]

    >>> print(parseMatrix('A', 'A  = [1, 3, 2; 4, 5, 6]'))
    [[1.0, 3.0, 2.0], [4.0, 5.0, 6.0]]

    >>> print(parseMatrix('A', '''A  = [1 2; 3 4 - 2i]'''))
    [[1.0, 2.0], [3.0, (4-2j)]]

    >>> print(parseMatrix('A', '''A  = [1 2; 3 4 5]'''))
    Traceback (most recent call last):
        ...
    ValueError: Matrix "A", rows have different lengths

    >>> print(parseMatrix('A', 'A  = [1, 3 5;5 6 7]'))
    [[1.0, 3.0, 5.0], [5.0, 6.0, 7.0]]

    >>> print(parseMatrix('A', 'A  = [3, 4, 5, 6];'))
    [[3.0, 4.0, 5.0, 6.0]]

    >>> print(parseMatrix('A', 'A  = [3, 4.3; 5, 6];'))
    [[3.0, 4.3], [5.0, 6.0]]

    >>> print(parseMatrix('A', 'A = [3 4.3\n5 6]'))
    [[3.0, 4.3], [5.0, 6.0]]

    Python examples:
    >>> print(parseMatrix('A','A  = [[]]'))
    Traceback (most recent call last):
        ...
    ValueError: Empty matrix "A"

    >>> print(parseMatrix('A','A  = [[1, 0], [2, 3]]'))
    [[1.0, 0.0], [2.0, 3.0]]

    >>> print(parseMatrix('A','A  = [[1, 0], [2, 3, 4]]'))
    Traceback (most recent call last):
        ...
    ValueError: Matrix "A", rows have different lengths

    >>> print(parseMatrix('A','A  = [[1,0],[2,3]]'))
    [[1.0, 0.0], [2.0, 3.0]]

    >>> print(parseMatrix('A','A  = [[1+1j,0, 3.0 - 9j],[2,3, 3.0 - -9j]]'))
    [[(1+1j), 0.0, (3-9j)], [2.0, 3.0, (3+9j)]]

    >>> print(parseMatrix('A','A  = [2, 3, 4]'))
    [[2.0, 3.0, 4.0]]

    >>> print(parseMatrix('A','A  = [[1+1e-6j,0],[2,3]]'))
    [[(1+1e-06j), 0.0], [2.0, 3.0]]

    >>> print(parseMatrix('num', 'num = [[ nan, inf], [-inf, 2]]'))
    [[nan, inf], [-inf, 2.0]]

    >>> print(parseMatrix('D', 'D = [0;     -5;]'))
    [[0.0], [-5.0]]

    >>> print(parseMatrix('D', 'D = [0;     -5]'))
    [[0.0], [-5.0]]

    >>> print(parseMatrix('D', 'D = [0;     xx]'))
    Traceback (most recent call last):
        ...
    ValueError: Cannot parse matrix "D"
    """
    try:
        # first try parsing Matlab style
        res = parseMatlab(name, text)
    except PP.ParseException:
        # second shot, Python style
        try:
            res = parseNumpy(name, text)
        except PP.ParseException:
            raise ValueError('Cannot parse matrix "%s"' % name)

    # report empty matrices (in most cases)
    if not res or res == [[]]:
        if checkempty:
            raise ValueError('Empty matrix "%s"' % name)
        else:
            return res

    # check length of rows
    ncol = len(res[0])
    for r in res[1:]:
        if ncol != len(r):
            raise ValueError('Matrix "%s", rows have different lengths' % name)

    return res


def parseMatlab(name, text):
    """
    Parse a string as a Matlab matrix.

    Parameters
    ----------
    name : str
        Name of the variable.
    text : str
        Matrix data.

    Returns
    -------
    list of list of floats
        Parsed representation.

    """
    tlist = list(map(str.strip, text.strip().split('\n')))
    for i in range(len(tlist)-1, -1, -1):
        if tlist[i][-3:] == '...':
            tlist[i] = tlist[i][:-3]
        elif tlist[i][-1] != ';':
            tlist.insert(i+1, ';')
        # print(>>sys.stderr, tlist
    return (PP.Suppress(name) + assignment +
            m_listlist).parseString(''.join(tlist)).asList()


def parseNumpy(name, text):
    """
    Parse a string as a numpy array.

    Parameters
    ----------
    name : str
        Name of the variable.
    text : str
        Matrix data.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    return (PP.Suppress(name) + assignment +
            p_listlist).parseString(text).asList()


if __name__ == "__main__":
    import doctest
    doctest.testmod()
