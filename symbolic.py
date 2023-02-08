from z3 import *

class Expr:
    def __add__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            other = Con(other)

        if isinstance(other, str):
            other = MyVar(other)
            
        if isinstance(other, Expr):
            return MyPlus(self, other)

        print(f"Non-matching types for +: {type(self)} and {type(other)}")
        return None
    
    def __sub__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            other = Con(other)

        if isinstance(other, str):
            other = MyVar(other)
            
        if isinstance(other, Expr):
            return MyMinus(self, other)

        print(f"Non-matching types for -: {type(self)} and {type(other)}")
        return None

    def __mul__(self, other):
        if isinstance(other, int) or isinstance(other, float):
            other = Con(other)

        if isinstance(other, str):
            other = MyVar(other)
            
        if isinstance(other, Expr):
            return Times(self, other)

        print(f"Non-matching types for *: {type(self)} and {type(other)}")
        return None
    
class Con(Expr):
    def __init__(self, val : float):
        self.val = val

    def ev(self, env={}):
        return self.val
    
    def toZ3(self):
        return self.val

    def __str__(self):
        return str(self.val)

    def __eq__(self, other):
        if isinstance(other, Con):
            return self.val == other.val
        return False
    
    def __mul__(self, other):
        return self.val * other

    def vars(self):
        return []

class MyVar(Expr):
    def __init__(self, name : str):
        self.name = name

    def ev(self, env={}):
        return env[self.name]
    
    # vars translate to Z3 integer variables.
    def toZ3(self):
        return Int(f"{self.name}")

    def __str__(self):
        return self.name

    def __eq__(self, other):
        if isinstance(other, MyVar):
            return self.name == other.name
        return False

    def vars(self):
        return [self.name]

class BinOp(Expr):
    def __init__(self, left : Expr, right : Expr):
        self.left  = left
        self.right = right

    def ev(self, env={}):
        return self.op(self.left.ev(env), self.right.ev(env))

    def __str__(self):
        return f"({self.left} {self.name} {self.right})"

    def __eq__(self, other):
        if isinstance(other, BinOp) and self.name == other.name:
            return self.left == other.left and self.right == other.right

        return False

    def vars(self):
        return self.left.vars() + self.right.vars()
    
class MyPlus(BinOp):

    name = '+'
    
    def op(self, x, y):
        return x + y
    
    def toZ3(self):
        return self.left.toZ3() + self.right.toZ3()

class MyMinus(BinOp):

    name = '-'
    
    def op(self, x, y):
        return x - y
    
    def toZ3(self):
        return self.left.toZ3() - self.right.toZ3()
    
class Times(BinOp):

    name = '*'
    
    def op(self, x, y):
        return x * y
    
    def toZ3(self):
        return self.left.toZ3() * self.right.toZ3()

class Equal(BinOp):

    name = '=='
    
    def op(self, x, y):
        return x == y
    
    def toZ3(self):
        return self.left.toZ3() == self.right.toZ3()

class MyAnd(BinOp):

    name = 'and'
    
    def op(self, x, y):
        return x and y

    def toZ3(self):
        return z3.And(self.left.toZ3(), self.right.toZ3())
    
class MyOr(BinOp):

    name = 'or'
    
    def op(self, x, y):
        return x or y
    
    def toZ3(self):
        return z3.Or(self.left.toZ3(), self.right.toZ3())

class SmallerThan(BinOp):

    name = '<'
    
    def op(self, x, y):
        return x < y
    
    def toZ3(self):
        return self.left.toZ3() < self.right.toZ3()

class BiggerThan(BinOp):

    name = '>'
    
    def op(self, x, y):
        return x > y
    
    def toZ3(self):
        return self.left.toZ3() > self.right.toZ3()
