;; =============================================
;; MiniLisp Demo Program
;; Run with: python minilisp.py demo.lisp
;; =============================================

;; Basic arithmetic
(+ 2 3)
(* 4 5)

;; Define and use a function
(define (square x) (* x x))
(square 5)

;; Factorial with recursion
(define (fact n)
  (if (<= n 1)
      1
      (* n (fact (- n 1)))))
(fact 5)
(fact 10)

;; Closures (make-adder pattern)
(define (make-adder n)
  (lambda (x)
    (+ x n)))

(define add5 (make-adder 5))
(define add10 (make-adder 10))

(add5 20)
(add10 30)

;; Map function
(define (map f lst)
  (if (null? lst)
      '()
      (cons (f (car lst)) (map f (cdr lst)))))

(map add5 '(1 2 3))

;; Sum a list
(define (sum lst)
  (if (null? lst)
      0
      (+ (car lst) (sum (cdr lst)))))

(sum '(1 2 3 4 5))

;; FizzBuzz (using quoted symbols instead of strings)
(define (fizzbuzz n)
  (if (= (modulo n 15) 0)
      'FizzBuzz
      (if (= (modulo n 3) 0)
          'Fizz
          (if (= (modulo n 5) 0)
              'Buzz
              n))))

(fizzbuzz 3)
(fizzbuzz 5)
(fizzbuzz 15)
(fizzbuzz 7)

;; Quote shorthand examples
(if (> 5 3) 'yes 'no)
(car '(1 2 3))

;; Conditional examples
(and 'a 'b)
(or 'a 'b)

;; List processing
(car '(1 2 3))
(cdr '(1 2 3))
(cons 0 '(1 2 3))
(append '(1 2) '(3 4))
(length '(1 2 3))
(null? '())

;; Pretty printing examples
(pprint '(1 2 3))
(pprint '(+ 1 (* 2 3)))
(pprint '(define (square x) (* x x)))
