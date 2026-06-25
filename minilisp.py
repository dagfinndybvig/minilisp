#!/usr/bin/env python3
"""
MiniLisp - A minimal LISP interpreter

Based on Peter Norvig's lispy.py (https://norvig.com/lispy.html)
Extended with proper lexical scoping.

Usage:
    python minilisp.py          # Start REPL
    python minilisp.py file.lisp # Run a file
"""

from typing import List, Dict, Any, Union, Callable
import operator as op
import functools
import sys


# =============================================================================
# PARSER
# =============================================================================

def tokenize(expr: str) -> List[str]:
    """Convert a string into a list of tokens."""
    # Remove Lisp-style comments (everything from ; to end of line)
    no_comments = ''
    for line in expr.split('\n'):
        if ';' in line:
            no_comments += line.split(';')[0].rstrip() + '\n'
        else:
            no_comments += line + '\n'
    # Tokenize
    return no_comments.replace('(', ' ( ').replace(')', ' ) ').split()


def parse(tokens: List[str]) -> Any:
    """Parse a list of tokens into an AST (nested lists)."""
    if not tokens:
        raise SyntaxError("Unexpected end of input")
    
    token = tokens.pop(0)
    if token == '(':
        expr = []
        while tokens and tokens[0] != ')':
            expr.append(parse(tokens))
        if not tokens:
            raise SyntaxError("Unexpected end of input in list")
        tokens.pop(0)  # Remove the ')'
        return expr
    elif token == ')':
        raise SyntaxError("Unexpected ')'")
    elif token == "'":
        # Handle quote shorthand: 'x or '(...
        if not tokens:
            raise SyntaxError("Unexpected end of input after quote")
        next_token = tokens.pop(0)
        if next_token == '(':
            # ' followed by ( - quote a list
            # Put the ( back and parse the list
            tokens.insert(0, '(')
            expr = parse(tokens)  # Parse the list
            return ['quote', expr]
        else:
            # ' followed by atom - quote the atom
            return ['quote', atom(next_token)]
    else:
        return atom(token)


def atom(token: str) -> Any:
    """Convert a token to a Python value."""
    # Handle quote shorthand for tokens like 'yes (single token with quote prefix)
    if token.startswith("'"):
        return ['quote', token[1:]]
    
    if token == 'true' or token == '#t':
        return True
    elif token == 'false' or token == '#f':
        return False
    elif token == 'nil' or token == '()':
        return []
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return token  # Symbol


# =============================================================================
# ENVIRONMENT (Lexical Scoping)
# =============================================================================

class Env(dict):
    """
    An environment: a dict of {var: val} pairs, with an outer Env.
    Implements lexical scoping via chained dictionaries.
    """
    def __init__(self, parms=(), args=(), outer=None):
        self.update(zip(parms, args))
        self.outer = outer
    
    def find(self, var):
        """Find the environment where var is defined, walking the chain."""
        if var in self:
            return self
        elif self.outer is not None:
            return self.outer.find(var)
        else:
            raise NameError(f"Name '{var}' is not defined")
    
    def __getitem__(self, var):
        """Get variable value, walking the environment chain."""
        found_env = self.find(var)
        # Use dict's __getitem__ directly to avoid recursion
        return dict.__getitem__(found_env, var)


def eval_sequence(exprs, env: Env) -> Any:
    """Evaluate a sequence of expressions, returning the last result."""
    result = None
    for expr in exprs:
        result = eval(expr, env)
    return result


def parse_bindings(bindings: Any) -> List[List[Any]]:
    """Normalize a binding list into a list of [var, expr] pairs."""
    if isinstance(bindings, list) and bindings:
        if isinstance(bindings[0], list) and len(bindings[0]) >= 2 and not isinstance(bindings[0][0], list):
            return [binding for binding in bindings]
        if len(bindings) == 2 and not isinstance(bindings[0], list):
            return [bindings]
    raise SyntaxError("Invalid bindings")


# =============================================================================
# EVALUATOR
# =============================================================================

def eval(expr, env: Env) -> Any:
    """
    Evaluate an expression in an environment.
    
    This is the core of the interpreter. It recursively evaluates
    expressions according to LISP semantics with lexical scoping.
    """
    # Self-evaluating forms: numbers, booleans
    if isinstance(expr, (int, float, bool)):
        return expr
    
    # Callable objects (functions as first-class values)
    elif callable(expr):
        return expr
    
    # Empty list
    elif expr == [] or expr is None:
        return expr
    
    # Variable reference (symbol)
    elif isinstance(expr, str):
        return env[expr]
    
    # List (special form or function call)
    elif isinstance(expr, list):
        if not expr:
            return expr
        
        op = expr[0]
        args = expr[1:]
        
        # Quote: (quote expr) -> return expr unevaluated
        if op == 'quote':
            if len(args) != 1:
                raise SyntaxError("quote takes exactly 1 argument")
            return args[0]
        
        # Define variable: (define var expr)
        elif op == 'define':
            if len(args) == 0:
                raise SyntaxError("define requires arguments")
            
            # Function definition: (define (f x y...) body...)
            if isinstance(args[0], list):
                func_def = args[0]
                if not func_def:
                    raise SyntaxError("Function definition requires a name")
                func_name = func_def[0]
                parms = func_def[1:]
                if len(args) == 1:
                    raise SyntaxError("Function definition requires a body")
                elif len(args) == 2:
                    body = args[1]
                else:
                    # Multiple body expressions: (define (f) expr1 expr2)
                    body = ['begin'] + args[1:]
                
                # Create lambda and bind it to func_name
                env[func_name] = make_lambda(parms, body, env)
                return None
            
            # Variable definition: (define x 42)
            elif len(args) == 2 and isinstance(args[0], str):
                var, val_expr = args
                env[var] = eval(val_expr, env)
                return None
            else:
                raise SyntaxError(f"Invalid define: {expr}")
        
        # Lambda: (lambda (parms...) body...)
        elif op == 'lambda':
            if len(args) == 0:
                raise SyntaxError("lambda requires parameters and body")
            
            parms_expr = args[0]
            if isinstance(parms_expr, list):
                parms = parms_expr
            elif isinstance(parms_expr, str):
                parms = [parms_expr]
            else:
                raise SyntaxError("lambda parameters must be a list")
            
            if len(args) == 1:
                body = None
            elif len(args) == 2:
                body = args[1]
            else:
                body = ['begin'] + args[1:]
            
            return make_lambda(parms, body, env)
        
        # Begin: (begin expr1 expr2 ...) -> evaluate all, return last
        elif op == 'begin':
            if not args:
                return None
            return eval_sequence(args, env)
        
        # If: (if test conseq [alt])
        elif op == 'if':
            if len(args) < 2 or len(args) > 3:
                raise SyntaxError("if requires 2 or 3 arguments")
            test, conseq = args[0], args[1]
            alt = args[2] if len(args) == 3 else None
            return eval(conseq if eval(test, env) else alt, env)

        # Cond: (cond (test expr1 expr2 ...) (else expr1 expr2 ...))
        elif op == 'cond':
            if not args:
                return None
            for clause in args:
                if not isinstance(clause, list) or not clause:
                    raise SyntaxError("cond clauses must be non-empty lists")
                if isinstance(clause[0], str) and clause[0].lower() == 'else':
                    if len(clause) < 2:
                        raise SyntaxError("else clause requires a body")
                    return eval_sequence(clause[1:], env)
                if eval(clause[0], env):
                    if len(clause) == 1:
                        return None
                    return eval_sequence(clause[1:], env)
            return None
        
        # Set!: (set! var expr)
        elif op == 'set!':
            if len(args) != 2 or not isinstance(args[0], str):
                raise SyntaxError("set! requires a variable name and an expression")
            var, val_expr = args
            target_env = env.find(var)
            target_env[var] = eval(val_expr, env)
            return None
        
        # And: (and expr1 expr2 ...) -> evaluate left to right, return first false or last
        elif op == 'and':
            if not args:
                return True
            result = True
            for arg in args:
                result = eval(arg, env)
                if not result:
                    return result
            return result
        
        # Or: (or expr1 expr2 ...) -> evaluate left to right, return first true or last
        elif op == 'or':
            if not args:
                return False
            result = False
            for arg in args:
                result = eval(arg, env)
                if result:
                    return result
            return result
        
        # Let: (let ((var expr) ...) body...)
        elif op == 'let':
            if len(args) == 0:
                raise SyntaxError("let requires bindings and body")
            
            binding_list = parse_bindings(args[0])
            body = args[1:] if len(args) > 1 else []
            
            if not body:
                raise SyntaxError("let requires a body")
            
            let_env = Env([], [], env)
            for binding in binding_list:
                if isinstance(binding, list) and len(binding) >= 2:
                    var, val_expr = binding[0], binding[1]
                    let_env[var] = eval(val_expr, env)
                else:
                    raise SyntaxError(f"Invalid binding: {binding}")
            
            return eval_sequence(body, let_env)

        # Let*: (let* ((var expr) ...) body...)
        elif op == 'let*':
            if len(args) == 0:
                raise SyntaxError("let* requires bindings and body")
            
            binding_list = parse_bindings(args[0])
            body = args[1:] if len(args) > 1 else []
            
            if not body:
                raise SyntaxError("let* requires a body")
            
            let_env = Env([], [], env)
            for binding in binding_list:
                if isinstance(binding, list) and len(binding) >= 2:
                    var, val_expr = binding[0], binding[1]
                    let_env[var] = eval(val_expr, let_env)
                else:
                    raise SyntaxError(f"Invalid binding: {binding}")
            
            return eval_sequence(body, let_env)

        # Letrec: (letrec ((var expr) ...) body...)
        elif op == 'letrec':
            if len(args) == 0:
                raise SyntaxError("letrec requires bindings and body")
            
            binding_list = parse_bindings(args[0])
            body = args[1:] if len(args) > 1 else []
            
            if not body:
                raise SyntaxError("letrec requires a body")
            
            let_env = Env([], [], env)
            for binding in binding_list:
                if isinstance(binding, list) and len(binding) >= 2:
                    var, _ = binding[0], binding[1]
                    let_env[var] = None
                else:
                    raise SyntaxError(f"Invalid binding: {binding}")
            for binding in binding_list:
                if isinstance(binding, list) and len(binding) >= 2:
                    var, val_expr = binding[0], binding[1]
                    let_env[var] = eval(val_expr, let_env)
                else:
                    raise SyntaxError(f"Invalid binding: {binding}")
            
            return eval_sequence(body, let_env)
        
        # List: (list expr1 expr2 ...) -> create a list
        elif op == 'list':
            return [eval(arg, env) for arg in args]
        
        # Cons: (cons expr list) -> add element to front of list
        elif op == 'cons':
            if len(args) != 2:
                raise SyntaxError("cons requires exactly 2 arguments")
            return [eval(args[0], env)] + eval(args[1], env)
        
        # Car: (car list) -> first element
        elif op == 'car':
            if len(args) != 1:
                raise SyntaxError("car requires exactly 1 argument")
            lst = eval(args[0], env)
            if not isinstance(lst, list) or not lst:
                raise TypeError("car requires a non-empty list")
            return lst[0]
        
        # Cdr: (cdr list) -> all but first element
        elif op == 'cdr':
            if len(args) != 1:
                raise SyntaxError("cdr requires exactly 1 argument")
            lst = eval(args[0], env)
            if not isinstance(lst, list):
                raise TypeError("cdr requires a list")
            return lst[1:]
        
        # Eval: (eval expr) -> evaluate expr in current environment
        elif op == 'eval':
            if len(args) != 1:
                raise SyntaxError("eval requires exactly 1 argument")
            return eval(eval(args[0], env), env)
        
        # Function call: evaluate op, then apply to evaluated args
        else:
            func = eval(op, env)
            evaluated_args = [eval(arg, env) for arg in args]
            return apply_func(func, evaluated_args, env)
    
    else:
        raise TypeError(f"Cannot evaluate: {expr}")


def make_lambda(parms, body, env):
    """Create a lambda function that captures its defining environment."""
    def lamb(*args):
        if len(args) != len(parms):
            raise TypeError(f"Expected {len(parms)} arguments, got {len(args)}")
        # Create new environment with parameters bound to arguments
        new_env = Env(parms, args, env)
        return eval(body, new_env)
    return lamb


def apply_func(func, args: List, env: Env) -> Any:
    """Apply a function to arguments."""
    if callable(func):
        # Python function or lambda
        try:
            return func(*args)
        except TypeError as e:
            # Wrong number of arguments
            raise TypeError(f"Wrong number of arguments: {e}")
    elif isinstance(func, list):
        # Could be a special form we didn't handle
        raise TypeError(f"Cannot apply: {func}")
    else:
        raise TypeError(f"Not a function: {func}")


# =============================================================================
# PRETTY PRINTER
# =============================================================================

def pprint(expr, indent: int = 0, indent_size: int = 2) -> str:
    """
    Pretty-print a Lisp expression in classical Lisp format with indentation.
    
    Args:
        expr: The expression to print (atom, list, or other value)
        indent: Current indentation level (spaces)
        indent_size: Number of spaces per indentation level
    
    Returns:
        String representation in Lisp format
    
    Traditional Lisp pretty-printing rules:
    - Atoms print as-is
    - Empty list prints as ()
    - Lists print with parentheses
    - Nested lists are indented to show structure
    """
    # Handle nil/empty list
    if expr == [] or expr is None:
        return "()"
    
    # Handle booleans - use Lisp symbols
    if isinstance(expr, bool):
        return "#t" if expr else "#f"
    
    # Handle atoms (numbers, strings, symbols)
    if isinstance(expr, (int, float, str)):
        return str(expr)
    
    # Handle callables (functions)
    if callable(expr):
        return "<function>"
    
    # Handle lists
    if isinstance(expr, list):
        if not expr:
            return "()"
        
        # Check if all elements are simple (non-list)
        all_simple = all(not isinstance(item, list) for item in expr)
        
        # If all elements are simple and the list is short, print inline
        if all_simple and len(expr) <= 5:
            elements = " ".join(pprint(item, 0, indent_size) for item in expr)
            return f"({elements})"
        
        # Otherwise, use multi-line format with indentation
        new_indent = indent + indent_size
        space_prefix = " " * new_indent
        
        # Check if any element is a non-empty list (needs multi-line)
        has_nested = any(isinstance(item, list) and item for item in expr)
        
        if has_nested:
            # Traditional Lisp pretty-print: all elements on separate lines
            # with consistent indentation
            lines = []
            for item in expr:
                item_str = pprint(item, new_indent, indent_size)
                lines.append(space_prefix + item_str)
            inner = "\n".join(lines)
            indent_str = " " * indent
            return f"(\n{inner}\n{indent_str})"
        else:
            # Inline format for simple lists
            elements = " ".join(pprint(item, 0, indent_size) for item in expr)
            return f"({elements})"
    
    # Fallback for any other type
    return str(expr)


# =============================================================================
# BUILT-IN FUNCTIONS
# =============================================================================

def setup_globals(env: Env):
    """Add built-in functions to the global environment."""
    env.update({
        # Arithmetic
        '+': lambda *args: sum(args),
        '-': lambda *args: -args[0] if len(args) == 1 else functools.reduce(op.sub, args[1:], args[0]),
        '*': lambda *args: 1 if not args else functools.reduce(op.mul, args, 1),
        '/': lambda *args: 1 / args[0] if len(args) == 1 else functools.reduce(op.truediv, args[1:], args[0]),
        'modulo': lambda a, b: a % b,
        
        # Comparisons
        '>': op.gt,
        '<': op.lt,
        '>=': op.ge,
        '<=': op.le,
        '=': op.eq,
        '!=': op.ne,
        
        # Boolean
        'not': op.not_,
        
        # List operations
        'list': lambda *args: list(args),
        'append': lambda a, b: a + b,
        'length': len,
        'null?': lambda x: x == [],
        'apply': lambda proc, args: proc(*args),
        'map': lambda proc, seq: [proc(item) for item in seq],
        
        # Type checking
        'number?': lambda x: isinstance(x, (int, float)),
        'symbol?': lambda x: isinstance(x, str),
        'list?': lambda x: isinstance(x, list),
        'function?': callable,
        
        # Pretty printing
        'pprint': pprint,
    })


# =============================================================================
# REPL
# =============================================================================

def repl(prompt: str = 'minilisp> '):
    """Read-Eval-Print Loop."""
    global_env = Env()
    setup_globals(global_env)
    
    print("MiniLisp v0.1 - Type exit or (exit) to quit, help or (help) for info")
    
    while True:
        try:
            line = input(prompt)
            
            if not line:
                continue
            
            # Tokenize and parse first to handle both (exit) and exit
            tokens = tokenize(line)
            ast = parse(tokens)
            
            # Check for special commands - handle both bare words and (command) forms
            if isinstance(ast, str):
                if ast.lower() in ('exit', 'quit'):
                    print("Goodbye!")
                    break
                elif ast.lower() in ('help', '?'):
                    print_help()
                    continue
            elif isinstance(ast, list) and len(ast) == 1:
                if ast[0].lower() in ('exit', 'quit'):
                    print("Goodbye!")
                    break
                elif ast[0].lower() in ('help', '?'):
                    print_help()
                    continue
            
            # Evaluate
            result = eval(ast, global_env)
            
            # Print result (if not None)
            if result is not None:
                print(result)
                
        except KeyboardInterrupt:
            print("\nUse (exit) to quit")
        except EOFError:
            print("\nGoodbye!")
            break
        except SyntaxError as e:
            print(f"Syntax error: {e}")
        except TypeError as e:
            print(f"Type error: {e}")
        except NameError as e:
            print(f"Name error: {e}")
        except Exception as e:
            print(f"Error: {e}")


def print_help():
    """Print help message."""
    print("""
MiniLisp - A minimal LISP interpreter

Supported forms:
  Atoms:        42, 3.14, 'hello, true, false, nil
  Lists:        (expr1 expr2 ...)
  Define:       (define var expr)       - define variable
               (define (f x) body)     - define function
  Lambda:       (lambda (x) body)       - anonymous function
  If:           (if test conseq [alt])
  Cond:         (cond (test expr ...) (else expr ...))
  Set!:         (set! var expr)         - mutate an existing binding
  Begin:        (begin expr1 expr2 ...) - evaluate all, return last
  Let:          (let ((x 1) (y 2)) body) - local bindings
  Let*:         (let* ((x 1) (y x)) body) - sequential local bindings
  Letrec:       (letrec ((f (lambda (n) ...))) body) - recursive bindings
  And/Or:       (and expr ...)          - logical and/or
  List ops:     (list 1 2 3)             - create list
               (car list)               - first element
               (cdr list)               - rest of list
               (cons x list)            - add to front
  Pretty print:  (pprint expr)             - pretty print with indentation
  Arithmetic:   (+ 1 2 3)                - add
               (- a b)                  - subtract
               (* a b)                  - multiply
               (/ a b)                  - divide
  Comparisons:  (> a b), (< a b), etc.
  Eval:         (eval expr)              - evaluate expression
  Quote:       (quote expr)             - return expr unevaluated
               'expr                       - shorthand for quote

Examples:
  (+ 1 2 3)                     -> 6
  (define (square x) (* x x))    -> defines square
  (square 5)                    -> 25
  ((lambda (x) (* x x)) 5)       -> 25
  (if (> 5 3) 'yes 'no)          -> yes
  (let ((x 5)) (* x x))           -> 25

Type (exit) to quit.
    """)


# =============================================================================
# FILE EXECUTION
# =============================================================================

def run_file(filename: str):
    """Load and execute a .lisp file."""
    global_env = Env()
    setup_globals(global_env)
    
    with open(filename, 'r') as f:
        code = f.read()
    
    # Tokenize and parse the entire file
    tokens = tokenize(code)
    
    # Evaluate each top-level expression
    while tokens:
        ast = parse(tokens)
        result = eval(ast, global_env)
        if result is not None:
            print(result)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Run a file
        run_file(sys.argv[1])
    else:
        # Start REPL
        repl()
