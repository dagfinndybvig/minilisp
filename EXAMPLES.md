# MiniLisp Examples

A collection of interesting MiniLisp programs that demonstrate various features of the interpreter.

## Quick Start

Start the REPL:
```bash
python minilisp.py
```

Or run a file:
```bash
python minilisp.py demo.lisp
```

**Note**: The current interpreter supports numbers, booleans, symbols, and lists. 
String literals are not yet supported - use quoted symbols instead (e.g., `'hello` instead of `"hello"`).

Try the included `demo.lisp` file for a complete working example.

---

## Table of Contents
1. [Basic Arithmetic](#1-basic-arithmetic)
2. [Recursion](#2-recursion)
3. [Lexical Scoping & Closures](#3-lexical-scoping--closures)
4. [Pretty Printing](#4-pretty-printing)
5. [Higher-Order Functions](#5-higher-order-functions)
6. [List Processing](#6-list-processing)
7. [Advanced Examples](#7-advanced-examples)
8. [One-Liner Challenges](#8-one-liner-challenges)

---

## 1. Basic Arithmetic

### Simple Calculations
```lisp
(+ 1 2 3 4 5)      ; -> 15
(* 2 3 4)          ; -> 24
(- 10 3)           ; -> 7
(/ 10 2)           ; -> 5.0
(modulo 10 3)      ; -> 1
```

### Comparisons
```lisp
(> 5 3)            ; -> true
(< 3 5)            ; -> true
(>= 5 5)           ; -> true
(= 5 5)            ; -> true
(!= 5 3)           ; -> true
```

---

## 2. Recursion

### Factorial
```lisp
(define (fact n)
  (if (<= n 1)
      1
      (* n (fact (- n 1)))))

(fact 5)   ; -> 120
(fact 10)  ; -> 3628800
```

### Fibonacci
```lisp
(define (fib n)
  (if (<= n 1)
      n
      (+ (fib (- n 1)) (fib (- n 2)))))

(fib 10)  ; -> 55
```

### Sum a List
```lisp
(define (sum lst)
  (if (null? lst)
      0
      (+ (car lst) (sum (cdr lst)))))

(sum '(1 2 3 4 5))  ; -> 15
```

---

## 3. Lexical Scoping & Closures

### Make Adder (Classic Closure Example)
```lisp
;; Create a function that makes adders
(define (make-adder n)
  (lambda (x)
    (+ x n)))

;; Create specific adders
(define adder5 (make-adder 5))
(define adder10 (make-adder 10))

;; Use them
(adder5 20)   ; -> 25
(adder10 30)  ; -> 40
```

### Multiple Closures from Same Factory
```lisp
(define (make-multiplier factor)
  (lambda (x)
    (* x factor)))

(define double (make-multiplier 2))
(define triple (make-multiplier 3))

(double 5)  ; -> 10
(triple 5)  ; -> 15
```

---

## 4. Pretty Printing

### Using pprint to Format Output

The `pprint` function pretty-prints Lisp expressions in classical Lisp format with proper indentation:

```lisp
;; Simple list - prints inline
(pprint '(1 2 3))
; -> (1 2 3)

;; Nested list - prints with indentation
(pprint '(+ 1 (* 2 3)))
; -> (
;     +
;     1
;     (* 2 3)
;   )

;; Complex nested structure
(pprint '(define (square x) (* x x)))
; -> (
;     define
;     (square x)
;     (* x x)
;   )

;; Empty list
(pprint '())  ; -> ()

;; Booleans print as #t and #f
(pprint true)  ; -> #t
(pprint false) ; -> #f
```

The `pprint` function follows traditional Lisp pretty-printing conventions:
- Atoms (numbers, symbols, booleans) print as-is
- Empty lists print as `()`
- Simple lists (all atoms, short) print inline: `(1 2 3)`
- Nested lists print with each element on its own line, indented by 2 spaces
- Closing parentheses align with opening parentheses

---

## 5. Higher-Order Functions

### Map Function
```lisp
(define (map f lst)
  (if (null? lst)
      '()
      (cons (f (car lst)) (map f (cdr lst)))))

;; Double all numbers
(map (lambda (x) (* x 2)) '(1 2 3 4 5))
; -> (2 4 6 8 10)

;; Square all numbers
(map (lambda (x) (* x x)) '(1 2 3 4))
; -> (1 4 9 16)
```

### Filter Function
```lisp
(define (filter pred lst)
  (if (null? lst)
      '()
      (let ((rest (filter pred (cdr lst))))
        (if (pred (car lst))
            (cons (car lst) rest)
            rest))))

;; Get even numbers
(filter (lambda (x) (= (modulo x 2) 0)) '(1 2 3 4 5 6))
; -> (2 4 6)
```

### Twice Function (Apply function twice)
```lisp
(define (twice f x)
  (f (f x)))

;; Square 5, then square the result: 5 -> 25 -> 625
(twice (lambda (x) (* x x)) 5)
; -> 625
```

---

## 5. List Processing

### Basic List Operations
```lisp
(list 1 2 3)           ; -> (1 2 3)
(car '(1 2 3))         ; -> 1
(cdr '(1 2 3))         ; -> (2 3)
(cons 0 '(1 2 3))       ; -> (0 1 2 3)
(append '(1 2) '(3 4))  ; -> (1 2 3 4)
(length '(1 2 3))       ; -> 3
(null? '())            ; -> true
```

### List Reversal
```lisp
(define (reverse lst)
  (if (null? lst)
      '()
      (append (reverse (cdr lst)) (list (car lst)))))

(reverse '(1 2 3 4))  ; -> (4 3 2 1)
```

### List Member
```lisp
(define (member x lst)
  (if (null? lst)
      false
      (if (= x (car lst))
          true
          (member x (cdr lst)))))

(member 3 '(1 2 3 4))  ; -> true
(member 5 '(1 2 3 4))  ; -> false
```

---

## 6. Advanced Examples

### FizzBuzz
```lisp
(define (fizzbuzz n)
  (if (= (modulo n 15) 0)
      "FizzBuzz"
      (if (= (modulo n 3) 0)
          "Fizz"
          (if (= (modulo n 5) 0)
              "Buzz"
              n))))

(fizzbuzz 3)   ; -> "Fizz"
(fizzbuzz 5)   ; -> "Buzz"
(fizzbuzz 15)  ; -> "FizzBuzz"
(fizzbuzz 7)   ; -> 7
```

### Ackermann Function (Deep Recursion)
```lisp
(define (ack m n)
  (if (= m 0)
      (+ n 1)
      (if (= n 0)
          (ack (- m 1) 1)
          (ack (- m 1) (ack m (- n 1))))))

;; Warning: Grows very fast!
(ack 1 1)   ; -> 3
(ack 2 2)   ; -> 7
(ack 3 3)   ; -> 61
```

### Y Combinator (Anonymous Recursion)
```lisp
;; The Y combinator for anonymous recursion
(define Y
  (lambda (f)
    ((lambda (x) (x x))
     (lambda (x)
       (f (lambda (y)
             ((x x) y)))))))

;; Factorial using Y combinator (no define!)
(define fact
  (Y (lambda (f)
       (lambda (n)
         (if (<= n 1)
             1
             (* n (f (- n 1))))))))

(fact 5)  ; -> 120
```

### Countdown with Let
```lisp
(define (countdown n)
  (if (<= n 0)
      '(Blastoff!)
      (cons n (countdown (- n 1)))))

(countdown 5)  ; -> (5 4 3 2 1 Blastoff!)
```

---

## 7. One-Liner Challenges

Test your understanding with these one-liners:

1. **Reverse Polish Notation**:
   ```lisp
   ((lambda (x y f) (f x y)) 3 4 (lambda (a b) (* a b)))
   ```
   **Answer**: `12`

2. **Currying**:
   ```lisp
   ((lambda (a) (lambda (b) (+ a b))) 5 10)
   ```
   **Answer**: `15`

3. **List Processing**:
   ```lisp
   (car (cdr (cdr '(1 2 3 4))))
   ```
   **Answer**: `3`

4. **Boolean Logic**:
   ```lisp
   (and (> 5 3) (< 2 4) (= 1 1))
   ```
   **Answer**: `true`

5. **Nested Lambda**:
   ```lisp
   ((lambda (x) (lambda (y) (* x y)) 3) 4)
   ```
   **Answer**: `12`

6. **Conditional Expression**:
   ```lisp
   (if (> 5 3) 'yes 'no)
   ```
   **Answer**: `yes`

7. **Quote Shorthand**:
   ```lisp
   'hello
   ```
   **Answer**: `hello`

8. **Quoted List**:
   ```lisp
   '(1 2 3)
   ```
   **Answer**: `(1 2 3)`

---

## Complete Demo Program

Here's a complete session you can copy-paste into the REPL:

```lisp
;; =============================================
;; MiniLisp Complete Demo
;; =============================================

;; --- Basic Arithmetic ---
(+ 2 3)                     ; -> 5
(* 4 5)                     ; -> 20

;; --- Define Functions ---
(define (square x) (* x x))
(square 5)                   ; -> 25

;; --- Factorial (Recursion) ---
(define (fact n)
  (if (<= n 1)
      1
      (* n (fact (- n 1)))))
(fact 5)                    ; -> 120

;; --- Closures ---
(define (make-adder n)
  (lambda (x) (+ x n)))
(define add5 (make-adder 5))
(add5 10)                  ; -> 15

;; --- Map Function ---
(define (map f lst)
  (if (null? lst)
      '()
      (cons (f (car lst)) (map f (cdr lst)))))
(map add5 '(1 2 3))        ; -> (6 7 8)

;; --- FizzBuzz ---
(define (fizzbuzz n)
  (if (= (modulo n 15) 0)
      "FizzBuzz"
      (if (= (modulo n 3) 0)
          "Fizz"
          (if (= (modulo n 5) 0)
              "Buzz"
              n))))
(fizzbuzz 15)               ; -> "FizzBuzz"

;; --- List Processing ---
(define (sum lst)
  (if (null? lst)
      0
      (+ (car lst) (sum (cdr lst)))))
(sum '(1 2 3 4 5))         ; -> 15

;; --- Quote Shorthand ---
(if (> 5 3) 'yes 'no)       ; -> yes
(car '(1 2 3))            ; -> 1

;; --- Conditional ---
(and 'a 'b)                ; -> b
(or 'a 'b)                 ; -> a
```

---

## Creating a Program File

Save any of these examples to a file (e.g., `demo.lisp`) and run:

```bash
python minilisp.py demo.lisp
```

Example `demo.lisp`:
```lisp
(define (fact n)
  (if (<= n 1)
      1
      (* n (fact (- n 1)))))

(fact 10)
```

Run it:
```bash
$ python minilisp.py demo.lisp
3628800
```

---

## Files Included

- **`EXAMPLES.md`** - This file, with all the examples documented
- **`demo.lisp`** - A runnable demo file that tests most features

Run the demo:
```bash
python minilisp.py demo.lisp
```

---

## License

These examples are provided as-is for educational and testing purposes. Feel free to use, modify, and distribute them.
