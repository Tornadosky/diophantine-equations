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

class ParseSTerm(Parser):
    """
    >>> res = result(ParseSTerm().parse("x *2abc"))
    >>> print(res)
    (x * 2)
    >>> res = result(ParseSTerm().parse("2*  (y + 2) * 2"))
    >>> print(res)
    (2 * ((y + 2) * 2))
    """
    def __init__(self):
        self.parser = (ParseSFactor() >> (lambda n:
                       ParseSymbol("*") >> (lambda _:
                       ParseSTerm() >> (lambda m:
                       Return(Times(n, m)))))) ^ ParseSFactor()

class ParseSExpr(Parser):
    """
    >>> res = result(ParseSExpr().parse("x"))
    >>> print(res)
    x
    >>> res = result(ParseSExpr().parse("x + 2*y"))
    >>> print(res)
    (x + (2 * y))
    >>> res = result(ParseSExpr().parse("15 + x * x"))
    >>> print(res)
    (15 + (x * x))
    >>> res = result(ParseSExpr().parse("(x - y) - z"))
    >>> print(res)
    ((x - y) - z)
    >>> res = result(ParseSExpr().parse("x - y - z"))
    >>> print(res)
    (x - (y - z))
    >>> res = result(ParseSExpr().parse("-x-y"))
    >>> print(res)
    (0 - (x - y))
    """
    def __init__(self):
        self.parser = (ParseSTerm() >> (lambda n:
                       ParseSymbol("+") >> (lambda _:
                       ParseSExpr() >> (lambda m:
                       Return(MyPlus(n, m)))))) ^ \
                            ParseSTerm() >> (lambda n:
                            ParseSymbol("-") >> (lambda _:
                            ParseSExpr() >> (lambda m:
                            Return(MyMinus(n, m))))) ^ \
                                ParseSymbol("-") >> (lambda _:
                                ParseSExpr() >> (lambda m:
                                Return(MyMinus(Con(0), m)))) ^ ParseSTerm()

class ParseEqu(Parser):
    """
    >>> ParseEqu().parse(" =y")
    []
    >>> ParseEqu().parse("x == 1")
    []
    >>> res = result(ParseEqu().parse("2*x   +y = 1asav"))
    >>> print(res)
    (((2 * x) + y) == 1)
    >>> res = result(ParseEqu().parse("x = 1"))
    >>> print(res)
    (x == 1)
    >>> res = result(ParseEqu().parse("x = ab1"))
    >>> print(res)
    (x == ab1)
    """
    def __init__(self):
        self.parser = (ParseSExpr() >> (lambda n:
                       ParseSymbol("=") >> (lambda _:
                       ParseSExpr() >> (lambda m:
                       Return(Equal(n, m))))))

class ParseEquSys(Parser):
    def __init__(self):
        self.parser = (ParseEqu() >> (lambda n:
                       ParseSymbol(",") >> (lambda _:
                       ParseEquSys() >> (lambda m:
                       Return(Parser.consType(n, m, [Equal])))))) ^ \
                            ParseEqu() >> (lambda n:
                            Return([n]))

class ParseConstr(Parser):
    """
    >>> res = result(ParseConstr().parse("x< y"))
    >>> print(res)
    (x < y)
    >>> res = result(ParseConstr().parse("x*2 + 4 * y*y > 1"))
    >>> print(res)
    (((x * 2) + (4 * (y * y))) > 1)
    """
    def __init__(self):
        self.parser = (ParseSExpr() >> (lambda n:
                       ParseSymbol("<") >> (lambda _:
                       ParseSExpr() >> (lambda m:
                       Return(SmallerThan(n, m)))))) ^ \
                            ParseSExpr() >> (lambda n:
                            ParseSymbol(">") >> (lambda _:
                            ParseSExpr() >> (lambda m:
                            Return(BiggerThan(n, m)))))

class ParseConj(Parser):
    """
    >>> res = result(ParseConj().parse("x < y*1 -2"))
    >>> print(res)
    (x < ((y * 1) - 2))
    >>> res = result(ParseConj().parse("(x < 5 and y > 0)"))
    >>> print(res)
    ((x < 5) and (y > 0))
    >>> res = result(ParseConj().parse("x > 1 and y<2 or y < 1"))
    >>> print(res)
    (x > 1)
    """
    def __init__(self):
        self.parser = ParseConstr() ^ \
                      (ParseSymbol("(") >> (lambda _:
                      ParseBool() >> (lambda e:
                      ParseSymbol(")") >> (lambda _:
                      Return(e)))))

class ParseDisj(Parser):
    """
    >>> ParseDisj().parse("x or y < 0")
    []
    >>> ParseDisj().parse("x = 3 and y < 0")
    []
    >>> ParseDisj().parse("y <= 0")
    []
    >>> res = result(ParseDisj().parse("x*2 + 4 * y*y > 1 and y<2"))
    >>> print(res)
    ((((x * 2) + (4 * (y * y))) > 1) and (y < 2))
    >>> res = result(ParseDisj().parse("x > 1 and y<2 or y < 1"))
    >>> print(res)
    ((x > 1) and (y < 2))
    """
    def __init__(self):
        self.parser = (ParseConj() >> (lambda n:
                       ParseSymbol("and") >> (lambda _:
                       ParseDisj() >> (lambda m:
                       Return(MyAnd(n, m)))))) ^ ParseConj()

class ParseBool(Parser):
    """
    >>> ParseBool().parse("x or y < 0")
    []
    >>> ParseBool().parse("x = 3 and y < 0")
    []
    >>> ParseBool().parse("y <= 0")
    []
    >>> res = result(ParseBool().parse("x*2 + 4 * y*y > 1 and y<2"))
    >>> print(res)
    ((((x * 2) + (4 * (y * y))) > 1) and (y < 2))
    >>> res = result(ParseBool().parse("x > 1 and y<2 or y < 1"))
    >>> print(res)
    (((x > 1) and (y < 2)) or (y < 1))
    >>> res = result(ParseBool().parse("x > 1 and y<2 or ((y < 1 or y < 1) and y<2)"))
    >>> print(res)
    (((x > 1) and (y < 2)) or (((y < 1) or (y < 1)) and (y < 2)))
    """
    def __init__(self):
        self.parser = (ParseDisj() >> (lambda n:
                       ParseSymbol("or") >> (lambda _:
                       ParseBool() >> (lambda m:
                       Return(MyOr(n, m)))))) ^ ParseDisj()

class ParseBoolSys(Parser):
    def __init__(self):
        self.parser = (ParseBool() >> (lambda n:
                       ParseSymbol(",") >> (lambda _:
                       ParseBoolSys() >> (lambda m:
                       Return(Parser.consType(n, m, [MyOr, MyAnd, SmallerThan, BiggerThan])))))) ^ \
                            ParseBool() >> (lambda n:
                            Return([n]))
            
class ParseSys(Parser):
    def __init__(self):
        self.parser = (ParseSymbol("Solve") >> (lambda _:
                       ParseEquSys() >> (lambda n:
                       ParseSymbol("such ") >> (lambda _:
                       ParseSymbol("that") >> (lambda _:
                       ParseBoolSys() >> (lambda m:
                       ParseString(".") >> (lambda _:
                       Return([n, m])))))))) ^ \
                            ParseSymbol("Solve") >> (lambda _:
                            ParseEquSys() >> (lambda n:
                            ParseString(".") >> (lambda _:
                            Return([n, []]))))