# MiniLisp

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A minimal LISP interpreter with proper lexical scoping, built as an educational project to understand interpreter design fundamentals.

## Quick Start

Start the REPL:
```bash
python minilisp.py
```

Run a file:
```bash
python minilisp.py demo.lisp
```

## Features

### Core Language
- ✅ S-expression parsing
- ✅ Basic arithmetic (`+`, `-`, `*`, `/`, `modulo`)
- ✅ Comparisons (`>`, `<`, `>=`, `<=`, `=`, `!=`)
- ✅ Boolean logic (`and`, `or`, `not`)
- ✅ Function definition (`define`)
- ✅ Lambda expressions (`lambda`)
- ✅ Conditional evaluation (`if`, `cond`)
- ✅ Mutation (`set!`)
- ✅ Lexical scoping with closures
- ✅ Recursion support
- ✅ Local bindings (`let`, `let*`, `letrec`)
- ✅ Higher-order helpers (`apply`, `map`)
- ✅ List operations (`list`, `car`, `cdr`, `cons`, `append`, `length`, `null?`)
- ✅ Type predicates (`number?`, `symbol?`, `list?`, `function?`)
- ✅ Quoting (`quote`, `'x`, `'(1 2 3)`)
- ✅ Evaluation (`eval`)
- ✅ Pretty-printing (`pprint`)

### REPL Features
- ✅ Interactive read-eval-print loop
- ✅ Help command (`help` or `?`)
- ✅ Exit command (`exit` or `quit`)
- ✅ File execution support

### Code Quality
- ✅ 72 regression tests (100% passing)
- ✅ Lisp-style comments (`;` to end of line)
- ✅ Clear error messages
- ✅ Proper lexical scoping
- ✅ First-class functions

## Examples

```lisp
;; Basic arithmetic
(+ 1 2 3)              ; -> 6
(* 2 3 4)              ; -> 24

;; Function definition
(define (square x) (* x x))
(square 5)             ; -> 25

;; Lambda expressions
((lambda (x) (* x x)) 5)  ; -> 25

;; Conditional
(if (> 5 3) 'yes 'no)     ; -> yes

;; Closures (lexical scoping)
(define (make-adder n)
  (lambda (x) (+ x n)))
(define add5 (make-adder 5))
(add5 10)             ; -> 15

;; Pretty printing
(pprint '(+ 1 (* 2 3)))
; -> (
;     +
;     1
;     (* 2 3)
;   )
```

## Attribution

This project stands on the shoulders of giants:

### Theoretical Foundation
The implementation follows the same core ideas presented in **[Structure and Interpretation of Computer Programs (SICP)](https://mitpress.mit.edu/sites/default/files/sicp/full-text/book/book.html)** by Abelson, Sussman, and Sussman — especially the environment model for evaluation and the use of lexical scoping in Chapter 4.

### Technical Foundation
**MiniLisp** is inspired by [Peter Norvig's lispy.py](https://norvig.com/lispy.html), which itself is a compact implementation of the interpreter ideas taught in SICP. MiniLisp follows the same basic structure, but it adds a handful of extra forms and conveniences:

- ✅ Lexical environment chaining for closures and nested procedures
- ✅ A regression test suite covering arithmetic, closures, recursion, and newer forms
- ✅ Pretty-printing with traditional Lisp indentation
- ✅ Enhanced REPL with commands
- ✅ File execution support
- ✅ Lisp-style comment support
- ✅ Quote shorthand syntax
- ✅ Additional special forms such as `cond`, `set!`, `let*`, and `letrec`
- ✅ Extra helpers such as `apply` and `map`
- ✅ Extensive documentation

The original `lispy.py` is copyright © 2010-2022 Peter Norvig, licensed under the **MIT License**. MiniLisp maintains the same license.

### Development Methodology
This project was developed using **[Mycelium](https://github.com/haabe/mycelium)** — a theory-guided harness for AI-assisted product development created by **[haabe](https://github.com/haabe)**.

© 2026 Mycelium Contributors, licensed under the **MIT License**.

*Note: Mycelium was originally designed for Claude Code, but this project demonstrates its effectiveness with Mistral Vibe as well.*

Mycelium provided:
- Canvas-based knowledge management (`.claude/canvas/`)
- Diamond-based work tracking (`.claude/diamonds/`)
- Decision logging (`.claude/harness/decision-log.md`)
- Evidence-based development discipline

The development process is fully documented in the Mycelium files included in this repository. All canvas evidence, diamond progress, and decision logs are preserved for transparency.

## Documentation

- **[EXAMPLES.md](EXAMPLES.md)** — 50+ categorized examples covering all features
- **[demo.lisp](demo.lisp)** — Runnable demo file testing major features
- **[tests/test_minilisp.py](tests/test_minilisp.py)** — Regression test suite (72 tests)

## Installation

No installation required — just clone and run:

```bash
git clone https://github.com/dagfinndybvig/minilisp.git
cd minilisp
python minilisp.py
```

Requirements:
- Python 3.6+
- No external dependencies

## Running Tests

```bash
python -m pytest tests/test_minilisp.py -v
```

All 72 tests should pass.

## License

MIT License — see [LICENSE](LICENSE) for details.

Copyright © 2026 Dagfinn Døhl Dybvig

As mentioned above, this project includes code and other elements derived from Peter Norvig's lispy.py (MIT License) and the Mycelium framework by haabe (MIT License).

## Contributing

Contributions are welcome! This is an educational project, so:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Update documentation
5. Submit a pull request

## Files

| File | Purpose |
|------|---------|
| `minilisp.py` | Core interpreter |
| `demo.lisp` | Example program |
| `EXAMPLES.md` | Comprehensive examples |
| `tests/test_minilisp.py` | Test suite |
| `.claude/canvas/gist.yml` | Mycelium project canvas |
| `.claude/diamonds/active.yml` | Work tracking |
| `.claude/harness/decision-log.md` | Decision records |
| `CHANGES-2026-06-23.md` | Change log |

## See Also

- [Peter Norvig's lispy.py](https://norvig.com/lispy.html) — Original inspiration
- [Mycelium by haabe](https://github.com/haabe/mycelium) — Development methodology framework
- [Structure and Interpretation of Computer Programs](https://mitpress.mit.edu/sites/default/files/sicp/full-text/book/book.html) — Theoretical foundation (SICP Chapter 4)
