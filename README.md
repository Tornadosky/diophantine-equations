# Diophantine Equations

Solving Systems of Diophantine Equations with Constraints using parsers, symbolic expressions and Z3 solver

# Project description

The aim of this project is to implement a function that solves systems of diophantine equations (i.e., the variables involved are integers) under constraints. The system is given in a file having the form shown in the following example:
```
Solve
x + y + z = 10,
x - z = 5
such that
x > 5 or x < -5 and y > 0,
z < 0.
```

The _solve_ function takes as argument the file name and returns one of the solutions to the system, represented as a dictionary, or prints an error message if no solutions exist. For example, if the above system is in the file _sys.txt_, the _solve_ function could act as follows:
```
>>> sol = solve(”sys.txt”)
>>> sol
{’x’: -6, ’y’: 27, ’z’: -11}
```
while the system
```
Solve
x + y + z = 10,
x - z = 5
such that
x > 5 or (x < -5 and y < 0),
z < 0.
```
would lead to
```
>>> sol = solve(”sys.txt”)
No solution!
```

### Note:

I assume that the input file is well formed, i.e.
+ there are no dangling parentheses or missing commas
+ no variables are called ’such’ or ’that’
+ there are no non-integer numbers

# Project finished

The project consists of several parts:
+ a BNF grammar for systems of diophantine equations with constraints
+ classes for representing symbolic expressions (arithmetic and boolean)
+ a parser for system descriptions
+ a method of translating the equations and constraints to Z3 expressions
+ an application of Z3 to solving the systems.

# BNF grammar for the Parser

```
int ::= INTEGER
var ::= IDENTIFIER
```
+ equation
```
equ-sys ::= equ | equ ',' equ-sys
equ ::= expr '=' expr
expr ::= term | term '+' expr | term '-' expr | '-' expr
term ::= factor | factor '*' term
factor ::= int | var | '(' expr ')'
```
+ constraints
```
bool-sys ::= bool | bool ',' bool-sys
bool ::= disj 'or' bool | disj
disj ::= conj 'and' disj | conj
conj ::= constr | '(' bool ')'
constr ::= expr '<' expr | expr '>' expr
```
+ system  -> Solve equations [such that constraints]
```
sys ::= 'Solve' equ-sys '.' | 'Solve' equ-sys 'such that' bool-sys '.'
```

### Description of the grammar

After the keyword _such that_ equations are restricted and before _such that_ usage of constraints and composite boolean expressions is not acceptable.
 
This means that it would be smart to represent this in two separate blocks: constraints system and equations system.

And overall use _system_ block to represent the System of Diophantine Equations with Constraints with keywords _Solve_, _such that_.
Dot('__.__') represents the end of the system, full stop.

+ __Equations__:

Extended the symbolic grammar with equation(equ) and several equations(equ-sys) grammar.
All operations are assumed to associate to the right.

+ __Constraints__:

Extended the symbolic grammar with strict inequality constraints, boolean 
symbolic expressions and several constraints(bool-sys) grammar.
'And' binds tighter than 'or'.

# System Description

A system description starts with the keyword _Solve_ followed by one or more equations (separated by commas), followed optionally by the keywords _such that_ followed by one or more constraints separated by commas. The
system description ends with a full stop.
Examples:
+ Only equations:
```
Solve
x*x - z = u,
x + u = 0,
y - 5*z = 3.
```
    Example solution:
```
>>> sol = solve(”only_eqs”)
>>> sol
{’y’: 3, ’x’: -1, ’u’: 1, ’z’: 0}
```
+ Simple system:
```
Solve
2*x*x = -y,
2
x - z = 5
such that
x > 0,
z < 0.
```
    Example solution:
```
>>> sol = solve(”simple”)
>>> sol
{’z’: -3, ’x’: 2, ’y’: -8}
```
+ System with no solutions:
```
Solve
x + y + z = 10,
x - z = 5
such that
x > 5 or x < z and y > 0,
z < 0.
```
+ System with one equation and more complex constraints:
```
Solve
2 * x + y*y + (z - u) - 3*v = t
such that
x > 0 and v < 0 and (z < 0 or u > 0),
y < 0 and (z > 0 or t > 0 and v < 0).
```
    Example solution:
```
>>> sol = solve(”complex”)
>>> sol
{’z’: 0, ’u’: 7, ’v’: -1, ’x’: 1, ’y’: -3, ’t’: 7}
```

# Code description

## Symbolic.py 

Class _Expression_ is the base class. 

_MyVar_ and _Con_ inherit from class _Expr_ and represent variables and constants in symbolic expressions.

_BinOp_ inherit from class _Expr_ and is used as the inherited class for specific binary operators(+, -, *, =, or, and).

Each of the specific classes and _MyVar_ have a method toZ3 which translates expression to a Z3 form.
_MyVar_ is translated to z3 Int object.

## Parser-1.py

Specific parsers were used: 
- core combinators (_Seq, OrElse, ParseItem, Return, Fail_),
- derived primitives for simple elements like symbols and numbers and some helpful classes for data processing,
- problem-specific combinators for tokenized versions of integers, strings and
	identifiers.
- parsing expressions, equations, bool systems, etc. with variables. 
Each class from the last category correlates with BNF grammar e.g.
_ParseSFactor_ -> factor element in the BNF grammar.

    Note:
    For readability right shift (>>) was overloaded and now represents _Seq_, xor operation (^) was overloaded and now represents _OrElse_.

For most parsers testable examples in docstrings were included (could be tested with _doctest_ module).

## Main.py

_solve()_ function reads the file and then this data is parsed,
the result is passed to the Z3-solver. Function returns dictionary with ONE of the solutions from Z3 with the help of return_sol() function. 