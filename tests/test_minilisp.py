"""
MiniLisp Test Suite

Comprehensive tests for the MiniLisp interpreter.
Run with: python -m pytest tests/test_minilisp.py -v
"""

import pytest
from minilisp import tokenize, parse, Env, eval as lisp_eval, pprint


# =============================================================================
# PARSER TESTS
# =============================================================================

class TestTokenize:
    """Tests for the tokenize() function."""
    
    def test_atom_integer(self):
        assert tokenize("123") == ["123"]
    
    def test_atom_float(self):
        assert tokenize("3.14") == ["3.14"]
    
    def test_atom_symbol(self):
        assert tokenize("hello") == ["hello"]
    
    def test_atom_with_hyphen(self):
        assert tokenize("make-adder") == ["make-adder"]
    
    def test_empty_list(self):
        assert tokenize("()") == ["(", ")"]
    
    def test_simple_list(self):
        assert tokenize("(+ 1 2)") == ["(", "+", "1", "2", ")"]
    
    def test_nested_list(self):
        tokens = tokenize("(+ 1 (* 2 3))")
        assert tokens == ["(", "+", "1", "(", "*", "2", "3", ")", ")"]
    
    def test_multiple_expressions(self):
        tokens = tokenize("(+ 1 2)(- 3 4)")
        assert tokens == ["(", "+", "1", "2", ")", "(", "-", "3", "4", ")"]
    
    def test_whitespace_handling(self):
        # Various whitespace should all work
        assert tokenize(" (+ 1 2) ") == ["(", "+", "1", "2", ")"]
        assert tokenize("(+  1   2)") == ["(", "+", "1", "2", ")"]
        assert tokenize("  ( + 1 2 )  ") == ["(", "+", "1", "2", ")"]
    
    def test_comment_handling(self):
        # Lisp-style comments (semicolon to end of line) should be stripped
        assert tokenize("(+ 1 2) ; this is a comment") == ["(", "+", "1", "2", ")"]
        assert tokenize("; comment before\n(+ 1 2)") == ["(", "+", "1", "2", ")"]
        assert tokenize("(+ ; inline comment\n1 2)") == ["(", "+", "1", "2", ")"]
        assert tokenize("(+ 1 ; comment\n 2)") == ["(", "+", "1", "2", ")"]


class TestParse:
    """Tests for the parse() function."""
    
    def test_parse_atom(self):
        tokens = tokenize("123")
        assert parse(tokens) == 123
    
    def test_parse_symbol(self):
        tokens = tokenize("hello")
        assert parse(tokens) == "hello"
    
    def test_parse_empty_list(self):
        tokens = tokenize("()")
        assert parse(tokens) == []
    
    def test_parse_simple_list(self):
        tokens = tokenize("(+ 1 2)")
        assert parse(tokens) == ["+", 1, 2]
    
    def test_parse_nested_list(self):
        tokens = tokenize("(+ 1 (* 2 3))")
        assert parse(tokens) == ["+", 1, ["*", 2, 3]]
    
    def test_parse_deeply_nested(self):
        tokens = tokenize("(a (b (c (d))))")
        assert parse(tokens) == ["a", ["b", ["c", ["d"]]]]
    
    def test_parse_multiple_top_level(self):
        # Parse should handle one expression at a time
        tokens = tokenize("(+ 1 2) (- 3 4)")
        first = parse(tokens)
        assert first == ["+", 1, 2]
        assert tokens == ["(", "-", "3", "4", ")"]


# =============================================================================
# ENVIRONMENT TESTS
# =============================================================================

class TestEnv:
    """Tests for the Env (environment) class."""
    
    def test_simple_lookup(self):
        env = Env(["x", "y"], [1, 2])
        assert env["x"] == 1
        assert env["y"] == 2
    
    def test_outer_env_lookup(self):
        outer = Env(["x"], [1])
        inner = Env(["y"], [2], outer)
        assert inner["x"] == 1  # Should find in outer
        assert inner["y"] == 2  # Should find in inner
    
    def test_shadowing(self):
        outer = Env(["x"], [1])
        inner = Env(["x"], [2], outer)
        assert inner["x"] == 2  # Inner shadows outer
        assert outer["x"] == 1  # Outer unchanged
    
    def test_find_method(self):
        outer = Env(["x"], [1])
        inner = Env(["y"], [2], outer)
        
        # find should return the env where variable is defined
        assert inner.find("y") is inner
        assert inner.find("x") is outer
    
    def test_find_missing(self):
        env = Env(["x"], [1])
        with pytest.raises(NameError):
            env.find("y")


# =============================================================================
# EVALUATOR TESTS - Basic Arithmetic
# =============================================================================

class TestEvalArithmetic:
    """Tests for arithmetic operations in the evaluator."""
    
    @pytest.fixture
    def global_env(self):
        """Create a global environment with built-ins."""
        env = Env()
        from minilisp import setup_globals
        setup_globals(env)
        return env
    
    def test_add_two_numbers(self, global_env):
        expr = ["+", 1, 2]
        assert lisp_eval(expr, global_env) == 3
    
    def test_add_multiple_numbers(self, global_env):
        expr = ["+", 1, 2, 3, 4]
        assert lisp_eval(expr, global_env) == 10
    
    def test_subtract(self, global_env):
        expr = ["-", 10, 3]
        assert lisp_eval(expr, global_env) == 7
    
    def test_multiply(self, global_env):
        expr = ["*", 3, 4]
        assert lisp_eval(expr, global_env) == 12
    
    def test_divide(self, global_env):
        expr = ["/", 10, 2]
        assert lisp_eval(expr, global_env) == 5.0
    
    def test_nested_arithmetic(self, global_env):
        expr = ["+", 1, ["*", 2, 3]]
        assert lisp_eval(expr, global_env) == 7
    
    def test_complex_nested(self, global_env):
        expr = ["*", ["+", 2, 3], ["-", 5, 1]]
        assert lisp_eval(expr, global_env) == 20


# =============================================================================
# EVALUATOR TESTS - Variables and Define
# =============================================================================

class TestEvalVariables:
    """Tests for variable binding and define."""
    
    @pytest.fixture
    def global_env(self):
        env = Env()
        from minilisp import setup_globals
        setup_globals(env)
        return env
    
    def test_variable_lookup(self, global_env):
        # First define a variable
        global_env["x"] = 10
        expr = "x"
        assert lisp_eval(expr, global_env) == 10
    
    def test_define_variable(self, global_env):
        # Note: define returns the value, but also binds it
        # In LISP: (define x 5) returns 5 and binds x to 5
        # But our implementation might just bind without returning
        # Let's test the binding effect
        expr = ["define", "x", 5]
        lisp_eval(expr, global_env)
        assert global_env["x"] == 5
    
    def test_define_function(self, global_env):
        # Define a function and call it
        # (define (square x) (* x x))
        expr = ["define", "square", ["lambda", ["x"], ["*", "x", "x"]]]
        lisp_eval(expr, global_env)
        
        # Now call it: (square 5)
        call_expr = ["square", 5]
        assert lisp_eval(call_expr, global_env) == 25


# =============================================================================
# EVALUATOR TESTS - Lambda and Lexical Scoping
# =============================================================================

class TestEvalLambda:
    """Tests for lambda expressions and lexical scoping."""
    
    @pytest.fixture
    def global_env(self):
        env = Env()
        from minilisp import setup_globals
        setup_globals(env)
        return env
    
    def test_simple_lambda(self, global_env):
        # ((lambda (x) (* x x)) 5)
        expr = [["lambda", ["x"], ["*", "x", "x"]], 5]
        assert lisp_eval(expr, global_env) == 25
    
    def test_lambda_with_multiple_args(self, global_env):
        # ((lambda (x y) (+ x y)) 3 4)
        expr = [["lambda", ["x", "y"], ["+", "x", "y"]], 3, 4]
        assert lisp_eval(expr, global_env) == 7
    
    def test_closure_captures_variable(self, global_env):
        # (define (make-adder n) (lambda (x) (+ x n)))
        # ((make-adder 5) 10) -> 15
        
        # Define make-adder
        define_expr = ["define", "make-adder", 
                      ["lambda", ["n"], 
                       ["lambda", ["x"], ["+", "x", "n"]]]]
        lisp_eval(define_expr, global_env)
        
        # Call make-adder with 5
        adder5_expr = ["make-adder", 5]
        adder5 = lisp_eval(adder5_expr, global_env)
        
        # Call the returned function with 10
        assert lisp_eval([adder5, 10], global_env) == 15
    
    def test_closure_multiple_instances(self, global_env):
        # (define (make-adder n) (lambda (x) (+ x n)))
        # (define adder5 (make-adder 5))
        # (define adder10 (make-adder 10))
        # ((adder5 10)) -> 15
        # ((adder10 10)) -> 20
        
        define_expr = ["define", "make-adder",
                      ["lambda", ["n"],
                       ["lambda", ["x"], ["+", "x", "n"]]]]
        lisp_eval(define_expr, global_env)
        
        adder5_expr = ["define", "adder5", ["make-adder", 5]]
        lisp_eval(adder5_expr, global_env)
        
        adder10_expr = ["define", "adder10", ["make-adder", 10]]
        lisp_eval(adder10_expr, global_env)
        
        assert lisp_eval(["adder5", 10], global_env) == 15
        assert lisp_eval(["adder10", 10], global_env) == 20
    
    def test_nested_lambda(self, global_env):
        # ((lambda (x) (lambda (y) (+ x y))) 3) -> function
        # Then call that function with 4 -> 7
        outer = [["lambda", ["x"], ["lambda", ["y"], ["+", "x", "y"]]], 3]
        inner_func = lisp_eval(outer, global_env)
        assert lisp_eval([inner_func, 4], global_env) == 7


# =============================================================================
# EVALUATOR TESTS - Conditionals
# =============================================================================

class TestEvalConditionals:
    """Tests for if expressions and comparisons."""
    
    @pytest.fixture
    def global_env(self):
        env = Env()
        from minilisp import setup_globals
        setup_globals(env)
        return env
    
    def test_if_true(self, global_env):
        # (if (> 5 3) 'yes 'no)
        expr = ["if", [">", 5, 3], ["quote", "yes"], ["quote", "no"]]
        assert lisp_eval(expr, global_env) == "yes"
    
    def test_if_false(self, global_env):
        expr = ["if", [">", 3, 5], ["quote", "yes"], ["quote", "no"]]
        assert lisp_eval(expr, global_env) == "no"
    
    def test_greater_than(self, global_env):
        assert lisp_eval([">", 5, 3], global_env) == True
        assert lisp_eval([">", 3, 5], global_env) == False
    
    def test_less_than(self, global_env):
        assert lisp_eval(["<", 3, 5], global_env) == True
        assert lisp_eval(["<", 5, 3], global_env) == False
    
    def test_equal(self, global_env):
        assert lisp_eval(["=", 5, 5], global_env) == True
        assert lisp_eval(["=", 5, 3], global_env) == False


# =============================================================================
# EVALUATOR TESTS - Recursion
# =============================================================================

class TestEvalRecursion:
    """Tests for recursive function definitions."""
    
    @pytest.fixture
    def global_env(self):
        env = Env()
        from minilisp import setup_globals
        setup_globals(env)
        return env
    
    def test_factorial(self, global_env):
        # (define (fact n) (if (<= n 1) 1 (* n (fact (- n 1)))))
        define_expr = ["define", "fact",
                      ["lambda", ["n"],
                       ["if", ["<=", "n", 1], 1, ["*", "n", ["fact", ["-", "n", 1]]]]]]
        lisp_eval(define_expr, global_env)
        
        assert lisp_eval(["fact", 1], global_env) == 1
        assert lisp_eval(["fact", 2], global_env) == 2
        assert lisp_eval(["fact", 5], global_env) == 120
    
    def test_fibonacci(self, global_env):
        # (define (fib n) (if (<= n 1) n (+ (fib (- n 1)) (fib (- n 2)))))
        define_expr = ["define", "fib",
                      ["lambda", ["n"],
                       ["if", ["<=", "n", 1], "n",
                        ["+", ["fib", ["-", "n", 1]], ["fib", ["-", "n", 2]]]]]]
        lisp_eval(define_expr, global_env)
        
        assert lisp_eval(["fib", 0], global_env) == 0
        assert lisp_eval(["fib", 1], global_env) == 1
        assert lisp_eval(["fib", 2], global_env) == 1
        assert lisp_eval(["fib", 5], global_env) == 5
        assert lisp_eval(["fib", 10], global_env) == 55


class TestEvalExtendedForms:
    """Tests for additional language forms added to MiniLisp."""

    @pytest.fixture
    def global_env(self):
        env = Env()
        from minilisp import setup_globals
        setup_globals(env)
        return env

    def test_cond(self, global_env):
        expr = ["cond", [[">", 1, 2], 1], [[">", 2, 1], 2], ["else", 3]]
        assert lisp_eval(expr, global_env) == 2

    def test_set_bang_updates_existing_binding(self, global_env):
        global_env["x"] = 1
        assert lisp_eval(["set!", "x", 2], global_env) is None
        assert global_env["x"] == 2

    def test_let_star_allows_sequential_bindings(self, global_env):
        expr = ["let*", [["x", 1], ["y", ["+", "x", 1]]], "y"]
        assert lisp_eval(expr, global_env) == 2

    def test_let_is_simultaneous(self, global_env):
        expr = ["let", [["x", 1], ["y", ["+", "x", 1]]], "y"]
        with pytest.raises(NameError):
            lisp_eval(expr, global_env)

    def test_letrec_supports_recursive_function(self, global_env):
        expr = [
            "letrec",
            [
                ["fact", ["lambda", ["n"], ["if", ["<=", "n", 1], 1, ["*", "n", ["fact", ["-", "n", 1]]]]]]
            ],
            ["fact", 5]
        ]
        assert lisp_eval(expr, global_env) == 120

    def test_variadic_subtract_and_divide(self, global_env):
        assert lisp_eval(["-", 10, 3, 2], global_env) == 5
        assert lisp_eval(["/", 24, 2, 2], global_env) == 6.0

    def test_apply_and_map_builtins(self, global_env):
        assert lisp_eval(["apply", "+", ["quote", [1, 2, 3]]], global_env) == 6
        assert lisp_eval(["map", ["lambda", ["x"], ["*", "x", "x"]], ["quote", [1, 2, 3]]], global_env) == [1, 4, 9]


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestIntegration:
    """Integration tests that combine multiple features."""
    
    @pytest.fixture
    def global_env(self):
        env = Env()
        from minilisp import setup_globals
        setup_globals(env)
        return env
    
    def test_full_session(self, global_env):
        """Simulate a full REPL session."""
        # Define square
        lisp_eval(["define", "square", ["lambda", ["x"], ["*", "x", "x"]]], global_env)
        
        # Define cube
        lisp_eval(["define", "cube", ["lambda", ["x"], ["*", "x", "x", "x"]]], global_env)
        
        # Call square
        assert lisp_eval(["square", 4], global_env) == 16
        
        # Call cube
        assert lisp_eval(["cube", 3], global_env) == 27
        
        # Nested calls
        assert lisp_eval(["square", ["cube", 2]], global_env) == 64
    
    def test_higher_order_function(self, global_env):
        """Test passing functions as arguments."""
        # Define a function that takes another function
        # (define (twice f x) (f (f x)))
        define_expr = ["define", "twice",
                      ["lambda", ["f", "x"], ["f", ["f", "x"]]]]
        lisp_eval(define_expr, global_env)
        
        # (twice square 5) where square is defined as (lambda (x) (* x x))
        square = ["lambda", ["x"], ["*", "x", "x"]]
        assert lisp_eval(["twice", square, 5], global_env) == 625
    
    def test_make_adder_factory(self, global_env):
        """Test a function that returns a function."""
        # (define (make-adder n) (lambda (x) (+ x n)))
        define_expr = ["define", "make-adder",
                      ["lambda", ["n"], ["lambda", ["x"], ["+", "x", "n"]]]]
        lisp_eval(define_expr, global_env)
        
        # Create adder5
        adder5 = lisp_eval(["make-adder", 5], global_env)
        
        # Use it
        assert lisp_eval([adder5, 10], global_env) == 15
        assert lisp_eval([adder5, 0], global_env) == 5
        assert lisp_eval([adder5, -5], global_env) == 0


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================

class TestErrorHandling:
    """Tests for error handling."""
    
    @pytest.fixture
    def global_env(self):
        env = Env()
        from minilisp import setup_globals
        setup_globals(env)
        return env
    
    def test_undefined_variable(self, global_env):
        with pytest.raises(NameError):
            lisp_eval("undefined-var", global_env)
    
    def test_wrong_number_of_args(self, global_env):
        # Define a function that takes 1 arg, call with 2
        define_expr = ["define", "one-arg", ["lambda", ["x"], "x"]]
        lisp_eval(define_expr, global_env)
        
        with pytest.raises(TypeError):
            lisp_eval(["one-arg", 1, 2], global_env)
    
    def test_invalid_syntax(self, global_env):
        # Unmatched parenthesis
        with pytest.raises(SyntaxError):
            tokens = ["(", "+", "1", "2"]  # Missing closing paren
            ast = parse(tokens)


# =============================================================================
# PERFORMANCE TESTS
# =============================================================================

class TestPerformance:
    """Performance tests to ensure interpreter is fast enough."""
    
    @pytest.fixture
    def global_env(self):
        env = Env()
        from minilisp import setup_globals
        setup_globals(env)
        return env
    
    def test_factorial_performance(self, global_env):
        """factorial(20) should complete in <100ms."""
        import time
        
        # Define factorial
        define_expr = ["define", "fact",
                      ["lambda", ["n"],
                       ["if", ["<=", "n", 1], 1, ["*", "n", ["fact", ["-", "n", 1]]]]]]
        lisp_eval(define_expr, global_env)
        
        # Time factorial(20)
        start = time.time()
        result = lisp_eval(["fact", 20], global_env)
        elapsed = time.time() - start
        
        assert result == 2432902008176640000
        assert elapsed < 0.1  # 100ms
    
    def test_deep_recursion(self, global_env):
        """Should handle 1000 levels of recursion without stack overflow."""
        import sys
        # Temporarily increase recursion limit
        old_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(10000)
        
        try:
            # Define a recursive function that counts down
            define_expr = ["define", "countdown",
                          ["lambda", ["n"],
                           ["if", ["<=", "n", 0], 0, ["countdown", ["-", "n", 1]]]]]
            lisp_eval(define_expr, global_env)
            
            # This should not cause a stack overflow
            result = lisp_eval(["countdown", 1000], global_env)
            assert result == 0
        finally:
            sys.setrecursionlimit(old_limit)


# =============================================================================
# REPL TESTS (Optional - if we implement REPL)
# =============================================================================

class TestREPL:
    """Tests for the REPL functionality."""
    
    def test_repl_basic(self):
        """Test that REPL can evaluate simple expressions."""
        # This would require mocking stdin/stdout
        # For now, skip or implement with subprocess
        pass


# =============================================================================
# PRETTY PRINT TESTS
# =============================================================================

class TestPPrint:
    """Tests for the pprint (pretty-print) function."""
    
    @pytest.fixture
    def global_env(self):
        """Create a global environment with built-ins for pprint tests."""
        env = Env()
        from minilisp import setup_globals
        setup_globals(env)
        return env
    
    def test_pprint_atom_integer(self):
        """Test pretty-printing an integer."""
        assert pprint(42) == "42"
    
    def test_pprint_atom_float(self):
        """Test pretty-printing a float."""
        assert pprint(3.14) == "3.14"
    
    def test_pprint_atom_symbol(self):
        """Test pretty-printing a symbol."""
        assert pprint("hello") == "hello"
    
    def test_pprint_atom_boolean_true(self):
        """Test pretty-printing true as #t."""
        assert pprint(True) == "#t"
    
    def test_pprint_atom_boolean_false(self):
        """Test pretty-printing false as #f."""
        assert pprint(False) == "#f"
    
    def test_pprint_empty_list(self):
        """Test pretty-printing empty list as ()."""
        assert pprint([]) == "()"
        assert pprint(None) == "()"
    
    def test_pprint_simple_list(self):
        """Test pretty-printing a simple list inline."""
        assert pprint([1, 2, 3]) == "(1 2 3)"
    
    def test_pprint_nested_list(self):
        """Test pretty-printing a nested list with indentation."""
        result = pprint(['+', 1, ['*', 2, 3]])
        # Should have multi-line format with indentation
        assert "(" in result
        assert ")" in result
        assert "*" in result
        assert "+" in result
        assert "1" in result
        # Check it's multi-line
        assert "\n" in result
    
    def test_pprint_deeply_nested(self):
        """Test pretty-printing deeply nested structures."""
        expr = ['define', ['square', 'x'], ['*', 'x', 'x']]
        result = pprint(expr)
        assert "define" in result
        assert "square" in result
        assert "*" in result
        assert "x" in result
    
    def test_pprint_lisp_form(self):
        """Test pretty-printing a Lisp-like form."""
        expr = ['lambda', ['x'], ['if', ['>', 'x', 0], 'x', ['-', 'x']]]
        result = pprint(expr)
        assert "lambda" in result
        assert "if" in result
        assert ">" in result
        assert "-" in result
    
    def test_pprint_through_evaluator(self, global_env):
        """Test that pprint works when called from Lisp code."""
        # (pprint '(+ 1 2))
        expr = ['pprint', ['quote', ['+', 1, 2]]]
        result = lisp_eval(expr, global_env)
        assert result == "(+ 1 2)"
    
    def test_pprint_nested_through_evaluator(self, global_env):
        """Test pprint with nested structures through evaluator."""
        expr = ['pprint', ['quote', ['+', 1, ['*', 2, 3]]]]
        result = lisp_eval(expr, global_env)
        # Result should be a multi-line string
        assert isinstance(result, str)
        assert "(" in result
        assert ")" in result
