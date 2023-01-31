# diophantine-equations
Solving Systems of Diophantine Equations with Constraints
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