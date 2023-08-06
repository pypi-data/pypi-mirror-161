
import re

def _fgrep(fname, pattern):
    regex = re.compile(pattern)

    result = ''
    with open(fname, 'r') as handle:
        for line in handle:
            if pattern in line or regex.match(line):
                result += line

    return result

def _shead(s, n):
    i = 0
    for j in range(n):
        i = s.find('\n', 0)
    return s[:i]



