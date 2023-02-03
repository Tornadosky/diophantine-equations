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

########################################
## Derived primitives
##
## Below this line, no more implementations
## of the "parse" method!
########################################

class ParseSome(Parser):
    def __init__(self, parser):
        self.parser = parser >> (lambda x: \
                                (ParseSome(parser) ^ Return([])) >> (lambda xs: \
                                 Return(Parser.cons(x, xs))))

class ParseIf(Parser):
    def __init__(self, pred):
        self.pred   = pred
        self.parser = ParseItem() >> (lambda c: \
                                      Return(c) if self.pred(c) else Fail())

class ParseMany(Parser):
    def __init__(self, parser):
        self.parser = ParseSome(parser) ^ Return([])

class ParseNat(Parser):
    def __init__(self):
        """
        >>> ParseNat().parse("00089abc")
        [(89, 'abc')]
        >>> ParseNat().parse("a89b")
        []
        >>> ParseNat().parse("-89")
        []
        """
        self.parser = ParseSome(ParseDigit()) >> (lambda ds: \
                                                  Return(int(ds)))

class ParseChar(Parser):
    """
    >>> ParseChar('-').parse("-89abc")
    [('-', '89abc')]
    >>> ParseChar('a').parse("89")
    []
    >>> ParseChar('a').parse("abc")
    [('a', 'bc')]
    """
    def __init__(self, c):
        self.parser = ParseIf(lambda x: c == x)
        
class ParseDigit(Parser):
    """
    >>> ParseDigit().parse("89abc")
    [('8', '9abc')]
    >>> ParseDigit().parse("a89b")
    []
    """
    def __init__(self):
        self.parser = ParseIf(lambda c: c in "0123456789")

# Problem specific combinators        

class ParseInt(Parser):
    def __init__(self):
        """
        >>> ParseInt().parse("89abc")
        [(89, 'abc')]
        >>> ParseInt().parse("-007xyz")
        [(-7, 'xyz')]
        >>> ParseInt().parse("abc")
        []
        """
        # if inp starts with minus, then check that the rest is a natural number
        # else, check if inp is a natural number
        # else, fail.
        self.parser = (ParseChar('-') >> (lambda _: \
                                         ParseNat() >> (lambda n: \
                                                        Return(-n)))) ^ ParseNat()

class ParseSpace(Parser):
    def __init__(self):
        self.parser = ParseMany(ParseIf(str.isspace)) >> (lambda _:
        Return([]))

class ParseToken(Parser):
    def __init__(self, parser):
        self.parser = ParseSpace() >> (lambda _:
        parser >> (lambda x:
        ParseSpace() >> (lambda _:
        Return(x))))

class ParseInteger(Parser):
    def __init__(self):
        self.parser = ParseToken(ParseInt())

class ParseString(Parser):
    def __init__(self, string):
        self.string = string
        self.parser = ParseChar(self.string[0]) >> (lambda x:
                      ParseString(self.string[1:]) >> (lambda xs:
                      Return(Parser.cons(x, xs)))) if self.string else Return('')

class ParseSymbol(Parser):
    def __init__(self, string):
        self.parser = ParseToken(ParseString(string))

class ParseLower(Parser):
    def __init__(self):
        self.parser = ParseIf(str.islower)

class ParseAlphanum(Parser):
    def __init__(self):
        self.parser = ParseIf(str.isalnum)

class ParseIdent(Parser):
    def __init__(self):
        self.parser = ParseLower() >> (lambda x:
        ParseMany(ParseAlphanum()) >> (lambda xs:
        Return(Parser.cons(x, xs))))

class ParseIdentifier(Parser):
    def __init__(self):
        self.parser = ParseToken(ParseIdent())

# Parse expression with variables

class ParseSInteger(Parser):
    """
    >>> res = result(ParseSInteger().parse("89abc"))
    >>> print(res)
    89
    >>> res = result(ParseSInteger().parse("-007xyz"))
    >>> print(res)
    -7
    >>> ParseSInteger().parse("abc")
    []
    """
    def __init__(self):
        self.parser = ParseInteger() >> (lambda n: Return(Con(n)))

class ParseSIdentifier(Parser):
    """
    >>> res = result(ParseSIdentifier().parse("x4  32"))
    >>> print(res)
    x4
    >>> res = result(ParseSIdentifier().parse("x*4= *5"))
    >>> print(res)
    x
    >>> res = result(ParseSIdentifier().parse("xop*4= y*5"))
    >>> print(res)
    xop
    >>> ParseSIdentifier().parse("3x")
    []
    """
    def __init__(self):
        self.parser = ParseIdentifier() >> (lambda var: Return(MyVar(var)))

class ParseSFactor(Parser):
    """
    >>> res = result(ParseSFactor().parse("x2 *2abc"))
    >>> print(res)
    x2
    >>> res = result(ParseSFactor().parse("(y + 2) * 2"))
    >>> print(res)
    (y + 2)
    >>> res = result(ParseSFactor().parse("(y + 2) * 2"))
    >>> print(res)
    (y + 2)
    """
    def __init__(self):
        self.parser = ParseSInteger() ^ ParseSIdentifier() ^ \
                      (ParseSymbol("(") >> (lambda _:
                      ParseSExpr() >> (lambda e:
                      ParseSymbol(")") >> (lambda _:
                      Return(e)))))