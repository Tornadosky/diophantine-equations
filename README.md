# Diophantine Equations
Solving Systems of Diophantine Equations with Constraints using parsers, symbolic expressions and z3 solver
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