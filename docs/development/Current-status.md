
# Current Status
Below we present the current status of the end-to-end tests.
The tests are divided into the following categories:
* [Branch counts](#branch-counts)
* [Loops](#loops)
* [Constraints](#constraints)
    * [One level](#one-level)
    * [Nested](#nested)
    * [Bunched](#bunched)
    * [Kill/Detach](#kill-detach)

Currently the number of end-to-end tests stands at 60, with 51 passing and 9 failing (85.00% coverage).

|                            filepath                            | $$\textcolor{#23d18b}{\tt{passed}}$$ | $$\textcolor{#f5f543}{\tt{xfailed}}$$ | SUBTOTAL |
| -------------------------------------------------------------- | --------------------------------: | --------------------------------: | -------: |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test{\_}branch{\_}counts.py}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test{\_}loops.py}}$$ |   $$\textcolor{#23d18b}{\tt{8}}$$ |   $$\textcolor{#f5f543}{\tt{4}}$$ | $$\textcolor{#f5f543}{\tt{12}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}bunched.py}}$$ |  $$\textcolor{#23d18b}{\tt{20}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{20}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}kill.py}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ |   $$\textcolor{#f5f543}{\tt{2}}$$ | $$\textcolor{#f5f543}{\tt{4}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}nested.py}}$$ |  $$\textcolor{#23d18b}{\tt{15}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{15}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}simple.py}}$$ |   $$\textcolor{#23d18b}{\tt{4}}$$ |   $$\textcolor{#f5f543}{\tt{3}}$$ | $$\textcolor{#f5f543}{\tt{7}}$$ |
| $$\textcolor{#f5f543}{\tt{TOTAL}}$$                            |  $$\textcolor{#23d18b}{\tt{51}}$$ |   $$\textcolor{#f5f543}{\tt{9}}$$ | $$\textcolor{#f5f543}{\tt{60}}$$ |


## Branch counts

Currently the number of branch tests stands at 2, with 2 passing and 0 failing (100.00% coverage).

|                   filepath                   |         function         | $$\textcolor{#23d18b}{\tt{passed}}$$ | SUBTOTAL |
| -------------------------------------------- | ------------------------ | --------------------------------: | -------: |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test{\_}branch{\_}counts.py}}$$ | $$\textcolor{#23d18b}{\tt{test{\_}simple{\_}branch{\_}count}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test{\_}branch{\_}counts.py}}$$ | $$\textcolor{#23d18b}{\tt{test{\_}double{\_}branch{\_}count}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{TOTAL}}$$          |                          |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |


## Loops

Currently the number of loops tests stands at 12, with 8 passing and 4 failing (66.67% coverage).

xfailed:
* `tests/end-to-end-tests/test_loops.py::TestBreakPoints.test_loop_break_point`
* `tests/end-to-end-tests/test_loops.py::TestBreakPoints.test_loop_two_break_points`
* `tests/end-to-end-tests/test_loops.py::TestBreakPoints.test_loop_nested_break_point`
* `tests/end-to-end-tests/test_loops.py::TestEdgeCases.test_loop_break_split_exit`

|               filepath               |                   function                   | $$\textcolor{#23d18b}{\tt{passed}}$$ | $$\textcolor{#f5f543}{\tt{xfailed}}$$ | SUBTOTAL |
| ------------------------------------ | -------------------------------------------- | --------------------------------: | --------------------------------: | -------: |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test{\_}loops.py}}$$ | $$\textcolor{#23d18b}{\tt{test{\_}self{\_}loop}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test{\_}loops.py}}$$ | $$\textcolor{#23d18b}{\tt{TestNestedLoops.test{\_}nested{\_}normal{\_}loop}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test{\_}loops.py}}$$ | $$\textcolor{#23d18b}{\tt{TestNestedLoops.test{\_}nested{\_}self{\_}loop}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test{\_}loops.py}}$$ | $$\textcolor{#23d18b}{\tt{TestNestedLogicBlocks.test{\_}nested{\_}and}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test{\_}loops.py}}$$ | $$\textcolor{#23d18b}{\tt{TestNestedLogicBlocks.test{\_}nested{\_}or}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test{\_}loops.py}}$$ | $$\textcolor{#23d18b}{\tt{TestNestedLogicBlocks.test{\_}nested{\_}xor}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test{\_}loops.py}}$$ | $$\textcolor{#23d18b}{\tt{TestNestedLogicBlocks.test{\_}logic{\_}bunched}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test{\_}loops.py}}$$ | $$\textcolor{#23d18b}{\tt{test{\_}nested{\_}branch{\_}counts}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test{\_}loops.py}}$$ | $$\textcolor{#f5f543}{\tt{TestBreakPoints.test{\_}loop{\_}break{\_}point}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ |   $$\textcolor{#f5f543}{\tt{1}}$$ | $$\textcolor{#f5f543}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test{\_}loops.py}}$$ | $$\textcolor{#f5f543}{\tt{TestBreakPoints.test{\_}loop{\_}two{\_}break{\_}points}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ |   $$\textcolor{#f5f543}{\tt{1}}$$ | $$\textcolor{#f5f543}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test{\_}loops.py}}$$ | $$\textcolor{#f5f543}{\tt{TestBreakPoints.test{\_}loop{\_}nested{\_}break{\_}point}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ |   $$\textcolor{#f5f543}{\tt{1}}$$ | $$\textcolor{#f5f543}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test{\_}loops.py}}$$ | $$\textcolor{#f5f543}{\tt{TestEdgeCases.test{\_}loop{\_}break{\_}split{\_}exit}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ |   $$\textcolor{#f5f543}{\tt{1}}$$ | $$\textcolor{#f5f543}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{TOTAL}}$$  |                                              |   $$\textcolor{#23d18b}{\tt{8}}$$ |   $$\textcolor{#f5f543}{\tt{4}}$$ | $$\textcolor{#f5f543}{\tt{12}}$$ |


## Constraints
### One level

Currently the number of simple tests stands at 7, with 4 passing and 3 failing (57.14% coverage).

xfailed:
* `tests/end-to-end-tests/constraints/test_constraints_simple.py::TestConstraintAND.test_multiple_same_event_AND`
* `tests/end-to-end-tests/constraints/test_constraints_simple.py::TestConstraintAND.test_merge_at_correct_event_AND`
* `tests/end-to-end-tests/constraints/test_constraints_simple.py::TestConstraintOR.test_merge_at_correct_event_OR`

|                           filepath                            |                     function                      | $$\textcolor{#23d18b}{\tt{passed}}$$ | $$\textcolor{#f5f543}{\tt{xfailed}}$$ | SUBTOTAL |
| ------------------------------------------------------------- | ------------------------------------------------- | --------------------------------: | --------------------------------: | -------: |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}simple.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintAND.test{\_}simple{\_}AND}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}simple.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintOR.test{\_}simple{\_}OR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}simple.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintXOR.test{\_}simple{\_}XOR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}simple.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintXOR.test{\_}merge{\_}at{\_}correct{\_}event{\_}XOR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}simple.py}}$$ | $$\textcolor{#f5f543}{\tt{TestConstraintAND.test{\_}multiple{\_}same{\_}event{\_}AND}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ |   $$\textcolor{#f5f543}{\tt{1}}$$ | $$\textcolor{#f5f543}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}simple.py}}$$ | $$\textcolor{#f5f543}{\tt{TestConstraintAND.test{\_}merge{\_}at{\_}correct{\_}event{\_}AND}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ |   $$\textcolor{#f5f543}{\tt{1}}$$ | $$\textcolor{#f5f543}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}simple.py}}$$ | $$\textcolor{#f5f543}{\tt{TestConstraintOR.test{\_}merge{\_}at{\_}correct{\_}event{\_}OR}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ |   $$\textcolor{#f5f543}{\tt{1}}$$ | $$\textcolor{#f5f543}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{TOTAL}}$$                           |                                                   |   $$\textcolor{#23d18b}{\tt{4}}$$ |   $$\textcolor{#f5f543}{\tt{3}}$$ | $$\textcolor{#f5f543}{\tt{7}}$$ |


### Nested

Currently the number of nested tests stands at 15, with 15 passing and 0 failing (100.00% coverage).

|                           filepath                            |                   function                    | $$\textcolor{#23d18b}{\tt{passed}}$$ | SUBTOTAL |
| ------------------------------------------------------------- | --------------------------------------------- | --------------------------------: | -------: |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedAND.test{\_}AND{\_}AND}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedAND.test{\_}AND{\_}OR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedAND.test{\_}AND{\_}XOR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedAND.test{\_}AND{\_}branch{\_}count}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedAND.test{\_}AND{\_}loop}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedOR.test{\_}OR{\_}AND}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedOR.test{\_}OR{\_}OR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedOR.test{\_}OR{\_}XOR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedOR.test{\_}OR{\_}branch{\_}count}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedOR.test{\_}OR{\_}loop}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedXOR.test{\_}XOR{\_}AND}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedXOR.test{\_}XOR{\_}OR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedXOR.test{\_}XOR{\_}XOR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedXOR.test{\_}XOR{\_}branch{\_}count}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedXOR.test{\_}XOR{\_}loop}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{TOTAL}}$$                           |                                               |  $$\textcolor{#23d18b}{\tt{15}}$$ | $$\textcolor{#23d18b}{\tt{15}}$$ |


### Bunched

Currently the number of bunched tests stands at 20, with 20 passing and 0 failing (100.00% coverage).

|                            filepath                            |                      function                       | $$\textcolor{#23d18b}{\tt{passed}}$$ | SUBTOTAL |
| -------------------------------------------------------------- | --------------------------------------------------- | --------------------------------: | -------: |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedAND.test{\_}bunched{\_}AND{\_}AND}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedAND.test{\_}bunched{\_}AND{\_}OR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedAND.test{\_}bunched{\_}AND{\_}XOR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedAND.test{\_}bunched{\_}merge{\_}AND{\_}AND}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedAND.test{\_}bunched{\_}merge{\_}AND{\_}OR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedAND.test{\_}bunched{\_}merge{\_}AND{\_}XOR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedOR.test{\_}bunched{\_}OR{\_}AND}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedOR.test{\_}bunched{\_}OR{\_}OR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedOR.test{\_}bunched{\_}OR{\_}XOR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedOR.test{\_}bunched{\_}merge{\_}OR{\_}AND}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedOR.test{\_}bunched{\_}merge{\_}OR{\_}OR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedOR.test{\_}bunched{\_}merge{\_}OR{\_}XOR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedXOR.test{\_}bunched{\_}XOR{\_}AND}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedXOR.test{\_}bunched{\_}XOR{\_}OR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedXOR.test{\_}bunched{\_}XOR{\_}XOR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedXOR.test{\_}bunched{\_}merge{\_}XOR{\_}AND}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedXOR.test{\_}bunched{\_}merge{\_}XOR{\_}OR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedXOR.test{\_}bunched{\_}merge{\_}XOR{\_}XOR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestBunchedHard.test{\_}bunched{\_}three{\_}levels{\_}AND}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestBunchedHard.test{\_}bunched{\_}three{\_}levels{\_}XOR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{TOTAL}}$$                            |                                                     |  $$\textcolor{#23d18b}{\tt{20}}$$ | $$\textcolor{#23d18b}{\tt{20}}$$ |


### Kill/Detach

Currently the number of kill tests stands at 4, with 2 passing and 2 failing (50.00% coverage).

xfailed:
* `tests/end-to-end-tests/constraints/test_constraints_kill.py::test_kill_with_merge_on_parent`
* `tests/end-to-end-tests/constraints/test_constraints_kill.py::test_kill_in_loop`

|                          filepath                           |            function            | $$\textcolor{#23d18b}{\tt{passed}}$$ | $$\textcolor{#f5f543}{\tt{xfailed}}$$ | SUBTOTAL |
| ----------------------------------------------------------- | ------------------------------ | --------------------------------: | --------------------------------: | -------: |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}kill.py}}$$ | $$\textcolor{#23d18b}{\tt{test{\_}kill{\_}with{\_}no{\_}merge}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}kill.py}}$$ | $$\textcolor{#23d18b}{\tt{test{\_}kill{\_}with{\_}merge}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}kill.py}}$$ | $$\textcolor{#f5f543}{\tt{test{\_}kill{\_}with{\_}merge{\_}on{\_}parent}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ |   $$\textcolor{#f5f543}{\tt{1}}$$ | $$\textcolor{#f5f543}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test{\_}constraints{\_}kill.py}}$$ | $$\textcolor{#f5f543}{\tt{test{\_}kill{\_}in{\_}loop}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ |   $$\textcolor{#f5f543}{\tt{1}}$$ | $$\textcolor{#f5f543}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{TOTAL}}$$                         |                                |   $$\textcolor{#23d18b}{\tt{2}}$$ |   $$\textcolor{#f5f543}{\tt{2}}$$ | $$\textcolor{#f5f543}{\tt{4}}$$ |



