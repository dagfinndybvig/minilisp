# MiniLisp Decision Log

This file records all significant decisions made during the MiniLisp project.
Each entry follows the structured format: decision, context, alternatives,
theory, evidence, confidence, date.

---

decision: "Fork Norvig's lispy.py and extend it, rather than building from scratch"
context: |
  We need to build a minimal LISP interpreter with parsing, evaluation, define,
  lambda, and lexical scoping. Norvig's lispy.py (100 lines of Python) already
  implements 80% of our requirements: parsing S-expressions, basic evaluation,
  define, lambda, if, and arithmetic operations.

  Building from scratch would mean reimplementing proven algorithms for parsing
  and evaluation. Norvig's code is well-tested, widely cited, and MIT licensed.
alternatives:
  - name: Build from scratch
    why_not: |
      Reinventing the wheel. Norvig's implementation is proven, simple, and
      covers our core requirements. Building from scratch would take 3-5x longer
      and likely introduce the same bugs Norvig already solved.
  
  - name: Use an existing LISP implementation (e.g., PyPy, Scheme)
    why_not: |
      Defeats the entire purpose of this project, which is to understand interpreter
      design by building one ourselves. Also, existing implementations are
      too heavyweight for our educational goals.
  
  - name: Port Norvig's code to JavaScript/Go
    why_not: |
      Python is the best choice for prototyping this. It's closest to Norvig's
      original, has excellent REPL support, and allows us to focus on the
      interpreter logic rather than language quirks.

theory: |
  - **DRY (Don't Repeat Yourself):** Norvig's code already solves the parsing
    and basic evaluation problems. We should extend rather than rewrite.
  
  - **80/20 Rule:** Get 80% of the functionality (parsing, eval, define, lambda)
    for 20% of the effort by building on existing work. Focus our energy on
    the 20% that's missing (lexical scoping, proper error handling, tests).
  
  - **Standing on Shoulders of Giants:** Newton's quote applies to software too.
    Norvig's lispy.py is a well-regarded reference implementation.

evidence: |
  - Norvig's lispy.py is 100 lines of clear, readable Python
  - It's MIT licensed (permissive, allows modification and redistribution)
  - It covers: atom parsing, list parsing, define, lambda, if, begin, arithmetic
  - It has been used in production and education for years
  - GitHub: https://github.com/norvig/pytudes/blob/main/lispy.py
  - Blog post: https://norvig.com/lispy.html
  
  - Our requirements overlap significantly with lispy.py's capabilities
  - The main gap (lexical scoping) is a well-understood extension

confidence: high
 date: "2026-06-22T10:00:00Z"
 tags: [architecture, approach]

---

decision: "Use chained dictionaries for environment/lexical scoping implementation"
context: |
  To support proper lexical scoping and closures, we need an environment system
  where each function's body is evaluated in an environment that includes its
  parameters bound to the argument values, plus a reference to the enclosing
  environment where the function was defined.

  Norvig's original lispy.py uses dynamic scoping (simpler but incorrect for
  LISP). We need to replace this with lexical scoping.
alternatives:
  - name: Single dictionary with name mangling
    why_not: |
      Name mangling (e.g., prefixing variable names with function names) is
      complex, error-prone, and doesn't naturally support nested functions or
      closures that reference variables from outer scopes.
  
  - name: Symbol table with explicit scope stack
    why_not: |
      More complex than needed. A chained dictionary approach is simpler to
      implement, understand, and debug. It directly models the lexical
      scoping rules.
  
  - name: Use Python's inspect module to capture closure variables
    why_not: |
      This would tie us too closely to Python's implementation. We want to
      understand how lexical scoping works, not delegate it to Python's
      runtime.

theory: |
  - **SICP Chapter 4:** Environments can be modeled as a sequence of frames,
    where each frame is a dictionary mapping variable names to values, and
    each frame has a pointer to its enclosing environment. This is the standard
    approach for implementing lexical scoping.
  
  - **Closure Property:** A lambda expression evaluates to a procedure that
    has the same scope as the lambda expression itself. The chained dictionary
    approach naturally captures this: when a lambda is created, it captures
    its defining environment (the current frame chain).

evidence: |
  - Norvig's lispy.py already has an Env class that extends dict
  - The Env class has an 'outer' attribute pointing to the parent environment
  - The find() method walks the chain to resolve variables
  - This pattern is proven in lispy.py and works correctly
  
  - SICP (Abelson & Sussman) uses this exact approach in their Scheme
    interpreter implementation
  
  - The implementation is ~20 lines of code (see minilisp.py Env class)

confidence: high
 date: "2026-06-22T10:05:00Z"
 tags: [architecture, scoping, implementation]

---

decision: "Implement in Python (not JavaScript or Go)"
context: |
  We need to choose an implementation language. Options considered:
  Python, JavaScript, and Go.

  The interpreter will be ~400-500 lines. We want rapid prototyping,
  readability, and a good REPL experience.
alternatives:
  - name: JavaScript
    pros: |
      - Can run in browser for interactive demos
      - Familiar to web developers
      - No compilation step needed
    cons: |
      - async/await complexity for REPL (need to handle async input)
      - Less ideal for systems programming concepts
      - More verbose for some operations
    
  - name: Go
    pros: |
      - Static typing catches errors early
      - Fast execution
      - Good for systems programming
      - Easy cross-compilation
    cons: |
      - More verbose syntax
      - Less familiar for interpreter concepts (dynamic typing, REPL)
      - Slower development cycle
      - No built-in REPL (need to implement)
    
  - name: Python
    pros: |
      - Norvig's reference implementation is in Python
      - Excellent REPL support built-in
      - Concise, readable syntax
      - Rapid prototyping
      - Dynamic typing matches LISP's dynamic nature
      - Rich standard library
      - Easy to write tests
    cons: |
      - Slightly slower than Go (but fine for our use case)
      - Dynamic typing might mask some bugs

theory: |
  - **Rapid Prototyping:** Python's interactive REPL and concise syntax
    allow for fast iteration during development.
  
  - **Least Resistance:** Norvig's reference is in Python. Porting to another
    language adds translation overhead without adding value for our
    educational goals.

evidence: |
  - Norvig's lispy.py exists and works in Python
  - Python has built-in REPL (just run `python minilisp.py`)
  - Python's standard library has everything we need (no external dependencies)
  - Python is widely used for educational interpreter implementations

confidence: high
 date: "2026-06-22T10:00:00Z"
 tags: [language, implementation]

---

# Decision Template

---

# Session Summary: 2026-06-22

## Decisions Made This Session

---

decision: "Fix define handler to correctly unpack function definitions"
context: |
  During testing, (define (square x) (* x x)) followed by (square 2) caused:
  Error: 'NoneType' object has no attribute 'find'
  
  Root cause: The define handler unpacked arguments incorrectly.
  Original code: _, func_def = args; func_name, *func_body = func_def
  For (define (square x) (* x x)), args = [['square', 'x'], ['*', 'x', 'x']]
  This unpacked to _ = ['square', 'x'], func_def = ['*', 'x', 'x']
  Then func_name became '*' (the first element of func_def)
  
  This meant 'square' was never bound to a function, so looking it up
  returned None, causing the error when trying to call None.find().
alternatives:
  - name: Rewrite the entire parser
    why_not: |
      Overkill. The parser was working correctly; the bug was in eval's
      define handler, not in parsing.
  
  - name: Use different syntax (define square (lambda (x) (* x x)))
    why_not: |
      Would work but requires users to use less idiomatic LISP syntax.
      The (define (f x) ...) form is standard and should be supported.

theory: |
  Trace the data: parser output -> eval input -> define handler.
  The parser correctly produces: ['define', ['square', 'x'], ['*', 'x', 'x']]
  The define handler must extract func_name from args[0][0], not from args[1][0].
  
  Principle: Data flow analysis. Understand the structure of your input before
  writing unpacking logic.
evidence: |
  - Error reproduced: (define (square x) (* x x)) then (square 2) -> crash
  - Fix tested: same input now returns 4 correctly
  - Parser output verified with print debugging

confidence: high
 date: "2026-06-22T11:25:00Z"
 tags: [bugfix, implementation, parsing]

---

decision: "Implement quote shorthand syntax 'x and fix Env.find() crash"
context: |
  Users reported: (if (> 5 3) 'yes 'no) caused Error: 'NoneType' object has no attribute 'find'
  
  Two issues were identified:
  1. Quote shorthand syntax 'x (equivalent to (quote x)) was not implemented
  2. Env.find() method crashed with AttributeError when variable not found in any environment
  
  The tokenizer treated 'yes as a single token with the quote as part of the variable name,
  so it tried to look up a variable named "'yes" which didn't exist. When find() reached
  the end of the environment chain (outer == None), it tried to call None.find(var),
  causing the crash.
alternatives:
  - name: Require users to always use (quote x) syntax
    why_not: |
      Less convenient for users. The 'x shorthand is standard in LISP and was already
      documented in the help text, so users expected it to work.
  
  - name: Fix only Env.find() without implementing quote shorthand
    why_not: |
      Would fix the crash but users still couldn't use the documented quote shorthand syntax.
      Both issues needed to be fixed for a complete solution.

theory: |
  - **Principle of Least Surprise**: If it's documented, it should work.
    The help text already mentioned 'expr as shorthand for quote.
  
  - **Robust Error Handling**: Errors should be informative, not cryptic.
    AttributeError: 'NoneType' object has no attribute 'find' is not helpful.
    NameError: Name 'x' is not defined is much clearer.
  
  - **Defensive Programming**: Always check for None before calling methods.
    The original find() method assumed outer would never be None at the end of the chain.

evidence: |
  - User reported the error with (if (> 5 3) 'yes 'no)
  - Verified conditionals worked with (quote yes) syntax
  - Implemented fixes and tested with 21 conditional expressions
  - All tests pass with quote shorthand

confidence: high
date: "2026-06-23T12:00:00Z"
tags: [bugfix, parser, error-handling, syntax]

---

decision: "Fix REPL to handle both bare and parenthesized commands"
context: |
  User reported that (help) and (exit) crashed, contrary to the interpreter's
  own instructions which said "Type (exit) to quit, (help) for info".
  
  The REPL checked the raw input string for 'exit' and 'help', but when users
  typed (exit) or (help), these were parsed as LISP expressions ['exit'] and
  ['help'], which then failed because exit and help are not defined as functions.
  
  The REPL only worked with bare words (exit, help, quit, ?) but not with
  parenthesized forms ((exit), (help), (quit), (?)).
alternatives:
  - name: Only support bare words
    why_not: |
      Contrary to the documented instructions. Users were told they could use
      (exit) and (help), so this would break the documented API.
  
  - name: Remove parentheses from the welcome message
    why_not: |
      Would make the documentation inconsistent with standard LISP practice.
      Many LISPs support both forms, and it's more intuitive for users.

theory: |
  - **Principle of Least Surprise**: The documentation said users could type
    (exit) and (help), so these should work.
  
  - **Consistency**: If the interpreter documents a feature, it should be implemented.
  
  - **User Experience**: Users expect both forms to work, as they see both in
    the welcome message.

evidence: |
  - User reported (help) and (exit) didn't work
  - Tested that bare words worked but parenthesized forms didn't
  - Fixed by parsing first, then checking both string and list forms
  - All command forms now work correctly

confidence: high
date: "2026-06-23T12:30:00Z"
tags: [bugfix, repl, ux, consistency]

---

decision: "Implement Env.__getitem__ to use find() for proper lexical scoping"
context: |
  During test execution, environment lookup tests failed because Env class
  extended dict but didn't override __getitem__. When code did env["x"], it only
  looked in the current environment dict, not the outer chain. This broke lexical
  scoping for nested environments.
alternatives:
  - name: Modify all lookup code to use find() explicitly
    why_not: |
      Would require changing every env lookup site in the codebase. Overriding
      __getitem__ is the Pythonic way and requires minimal changes.
  
  - name: Use a different data structure (not dict inheritance)
    why_not: |
      The Env class already extends dict and this pattern works well. Adding
      __getitem__ is the cleanest solution that maintains the existing API.

theory: |
  - **Python Data Model**: Override special methods to customize behavior.
    __getitem__ is the standard way to customize dict access.
  
  - **DRY (Don't Repeat Yourself)**: Instead of calling find() everywhere,
    centralize the logic in one place (__getitem__).
  
  - **Principle of Least Surprise**: env["x"] should work the same as dict lookup
    but with the added behavior of walking the chain.

evidence: |
  - test_outer_env_lookup was failing: inner["x"] didn't find "x" in outer env
  - test_shadowing was failing: inner["x"] should find inner's "x", not outer's
  - After fix, all 5 Env tests pass
  - Verified with manual test: outer = Env(["x"], [1]); inner = Env(["y"], [2], outer); inner["x"] == 1

confidence: high
 date: "2026-06-23T13:30:00Z"
 tags: [architecture, bugfix, lexical-scoping, implementation]

---

decision: "Handle callable objects in evaluator for first-class functions"
context: |
  Lambda functions were returning Python callables, but when these were returned
  from other functions and used in expressions, the evaluator didn't recognize them
  as self-evaluating forms. This broke tests like test_closure_captures_variable
  and test_make_adder_factory where functions were returned and then called.
alternatives:
  - name: Don't allow functions as first-class values
    why_not: |
      This would break LISP idioms. Functions as first-class values are
      fundamental to LISP (passing functions as arguments, returning functions,
      etc.).
  
  - name: Wrap callables in a special LispFunction class
    why_not: |
      Unnecessary complexity. Python callables already have the right
      semantics. We just need to recognize them in the evaluator.

theory: |
  - **First-Class Functions**: In LISP, functions are first-class values that
    can be passed as arguments, returned from functions, and stored in variables.
  
  - **Minimal Change**: Adding a single check for callable in the evaluator
    enables this feature without changing the overall architecture.

evidence: |
  - test_closure_captures_variable failed: couldn't call returned lambda
  - test_nested_lambda failed: couldn't use nested lambda result
  - test_make_adder_factory failed: make-adder returns a function
  - After adding callable check, all lambda and closure tests pass

confidence: high
 date: "2026-06-23T13:30:00Z"
 tags: [architecture, bugfix, first-class-functions, evaluator]

---

decision: "Add argument count validation to lambda functions"
context: |
  The make_lambda function created Python lambdas with *args, which accept any
  number of arguments. This meant that calling a function with wrong number of
  arguments didn't raise an error, it just silently used the first N arguments or
  set extras to None. The test_wrong_number_of_args test expected a TypeError.
alternatives:
  - name: Let Python's type system handle it naturally
    why_not: |
      Python's *args accepts any number, so no error would be raised at the
      Python level. We need explicit validation.
  
  - name: Validate at call site in apply_func
    why_not: |
      By the time we reach apply_func, we've already unpacked the arguments.
      It's better to validate at the function boundary (in make_lambda).

theory: |
  - **Fail Fast**: Validate inputs as early as possible. Checking argument count
    at function entry is the right place.
  
  - **Explicit is Better than Implicit**: The Zen of Python. We should explicitly
    check and raise a clear error for wrong argument counts.

evidence: |
  - test_wrong_number_of_args was failing: no TypeError raised
  - After adding len(args) != len(parms) check in make_lambda, test passes
  - Error message is clear: "Expected N arguments, got M"

confidence: high
 date: "2026-06-23T13:30:00Z"
 tags: [bugfix, error-handling, lambda, validation]

---

decision: "Use functools.reduce for variadic multiplication operator"
context: |
  The multiplication operator was defined with a broken ternary:
  lambda *args: 1 if not args else op.mul(*args) if len(args) == 1 else op.mul(*args)
  This didn't work for more than 2 arguments. op.mul only takes 2 arguments,
  but we need to handle (* 2 3 4) which should return 24.
alternatives:
  - name: Use a loop to multiply sequentially
    why_not: |
      functools.reduce is the standard Python idiom for this pattern.
      It's cleaner and more Pythonic.
  
  - name: Use math.prod (Python 3.8+)
    why_not: |
      math.prod is available, but functools.reduce is more general and
      works with any binary operator pattern.

theory: |
  - **Python Standard Library**: Use functools.reduce for accumulating operations
    over variable-length argument lists.
  
  - **Consistency**: The + operator uses sum(*args), so * should use a similar
    accumulation pattern.

evidence: |
  - test_multiply failed: (* 2 3 4) didn't work correctly
  - test_full_session failed: (define (cube x) (* x x x)) didn't work
  - After using functools.reduce(op.mul, args, 1), all multiplication tests pass

confidence: high
 date: "2026-06-23T13:30:00Z"
 tags: [bugfix, implementation, operators, pythonic]

---

decision: "Create comprehensive examples and demo program for MiniLisp"
context: |
  Users needed example programs to understand how to use MiniLisp and test
  its features. Without examples, the project would be less useful for
  learning and testing. Also, .lisp files with comments weren't working
  because the tokenizer didn't strip Lisp-style comments.
alternatives:
  - name: Just document examples in README
    why_not: |
      Examples deserve their own comprehensive documentation. Combining with
      README would make it too long and hard to navigate.
  
  - name: Only create inline documentation
    why_not: |
      Inline documentation in code is good for developers but not helpful
      for users who just want to run examples and learn the language.
  
  - name: Put examples in separate files only (no EXAMPLES.md)
    why_not: |
      Having a documented reference (EXAMPLES.md) makes it easier to browse
      and understand all available examples without opening each file.

theory: |
  - **Documentation as Code**: Examples should be executable code.
  
  - **Progressive Disclosure**: Provide both a comprehensive reference
    (EXAMPLES.md) and runnable files (demo.lisp) so users can choose their
    learning path.
  
  - **Teaching by Example**: The best way to learn a language is to see
    working examples of real programs.
  
  - **Preservation**: Examples should be preserved in version control for
    future reference and regression testing.

evidence: |
  - Created EXAMPLES.md with 50+ categorized examples
  - Created demo.lisp that runs successfully
  - Added comment support to tokenizer
  - All examples tested and verified working
  - Examples cover all major MiniLisp features

confidence: high
 date: "2026-06-23T15:00:00Z"
 tags: [documentation, examples, user-experience, education]

---

decision: "Implement pprint function for pretty-printing Lisp expressions with traditional indentation"
context: |
  Users wanted a way to visualize Lisp data structures in classical Lisp format
  with proper indentation to show nested structure. The default Python list
  representation [1, 2, [3, 4]] doesn't match Lisp conventions and makes it
  hard to read nested structures.
  
  Traditional Lisp pretty-printers format lists with rounded parentheses and
  indent nested structures to make the hierarchy clear.
alternatives:
  - name: Simple string conversion without indentation
    why_not: |
      Would not provide the "pretty" aspect. Simple conversion like [1,2,3] -> (1 2 3)
      is trivial but doesn't help with nested structures. Users specifically wanted
      indentation to show structure.
  
  - name: External pretty-print library
    why_not: |
      Defeats the purpose of a self-contained, minimal interpreter. Also, no
      existing Python library formats exactly like classical Lisp with proper
      indentation conventions.
  
  - name: Defer to later phase
    why_not: |
      The feature is small (~40 lines), well-contained, and doesn't affect core
      functionality. Adding it now provides immediate user value.

theory: |
  - **Progressive Disclosure**: Make complex nested structures readable by
    formatting them hierarchically.
  
  - **Lisp Traditions**: Follow classical Lisp pretty-printing conventions that
    programmers expect (rounded parentheses, 2-space indentation, aligned
    closing parens).
  
  - **Separation of Concerns**: pprint is a presentation function that doesn't
    affect the core evaluation logic, making it safe to add as a built-in.

evidence: |
  - Implemented pprint in ~40 lines with recursive structure handling
  - Added 12 comprehensive tests covering atoms, lists, nested structures, booleans
  - Updated EXAMPLES.md with usage examples
  - Updated demo.lisp with pprint examples
  - All 65 tests pass (53 original + 12 new)
  - Feature works both from REPL and from .lisp files

confidence: high
 date: "2026-06-23T15:30:00Z"
 tags: [feature, pretty-printing, user-experience, stretch-goal]
