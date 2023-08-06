(**** Calculation ****)
Sin[Pi]

E ^ (Pi I) (* Euler's famous equation *)
N[E, 30] (* 30-digit Numeric approximation of E *)

30! (* Factorial *)
% // N

Sum[2 i + 1, {i, 0, 10}] (* Sum of 1st n odd numbers (n+1)**2 *)

n = 8; 2 ^ # & /@ Range[0, n] (* Powers of 2 *)

Total[%] (* Sum is 2 ^ n - 1 *)
