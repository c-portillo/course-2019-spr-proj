def union (R, S):
    return R + S

def difference (R, S):
    # R - S
    return [t for t in R if t not in S]

def intersect (R, S):
    return [t for t in R if t in S]

def createQuadraticFunction(a, b, c):
    return lambda x : a*x**2 + b*x + c

def project (R, p):
    return [p(t) for t in R]

def product (R, S):
    return [(a, b) for a in S for b in R]

def select (R, p):
    return [t for t in R if p(t)]

#aggregates all the values for a particular key in R
def aggregate(R, a):
     keys = {r[0] for r in R}
     return [(key, a([v for (k, v) in R if k == key])) for key in keys]


def map (f, R):
    return [f(k, v) for (k, v) in R]

def reduce (f, R):
    keys = {k for (k, v) in R}
    return [f(k1, [v for (k, v) in R if k == k1]) for k1 in keys]
