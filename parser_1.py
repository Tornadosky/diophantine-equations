from symbolic import *

result = lambda p: p[0][0]
rest   = lambda p: p[0][1]

class Parser:
    def __xor__(self, other):
        return OrElse(self, other)

    def __rshift__(self, pfun):
        return Seq(self, pfun)

    def parse(self, s):
        return self.parser.parse(s)

    def cons(x, xs):
        if type(xs) == str:
            return x + xs
        elif type(x) == str and xs == []:
            return x
        else:
            return [x] + xs

    # similar to cons but fixes nested
    # lists for several objectTypes
    def consType(x, xs, objType : list):
        if type(xs) in objType:
            return [x] + [xs]
        else:
            return [x] + xs
    
########################################
# Core combinators:                    #
# they override the function "parse".  #
########################################

class Seq(Parser):
    def __init__(self, parser, and_then):
        self.parser   = parser
        self.and_then = and_then

    def parse(self, inp):
        p = self.parser.parse(inp)
        if p != []:
            return self.and_then(result(p)).parse(rest(p))

        return []

class OrElse(Parser):
    def __init__(self, parser1, parser2):
        self.parser1 = parser1
        self.parser2 = parser2

    def parse(self, inp):
        p = self.parser1.parse(inp)
        if p != []:
            return p

        return self.parser2.parse(inp)

class ParseItem(Parser):
    def parse(self, inp):
        if inp == "":
            return []
        return [(inp[0], inp[1:])]

class Return(Parser):
    def __init__(self, x):
        self.x = x
        
    def parse(self, inp):
        return [(self.x, inp)]

class Fail(Parser):
    def parse(self, inp):
        return []
