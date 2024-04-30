
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
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\text{\_}branch\text{\_}counts.py}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\text{\_}loops.py}}$$ |   $$\textcolor{#23d18b}{\tt{8}}$$ |   $$\textcolor{#f5f543}{\tt{4}}$$ | $$\textcolor{#f5f543}{\tt{12}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}bunched.py}}$$ |  $$\textcolor{#23d18b}{\tt{20}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{20}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}kill.py}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ |   $$\textcolor{#f5f543}{\tt{2}}$$ | $$\textcolor{#f5f543}{\tt{4}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}nested.py}}$$ |  $$\textcolor{#23d18b}{\tt{15}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{15}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}simple.py}}$$ |   $$\textcolor{#23d18b}{\tt{4}}$$ |   $$\textcolor{#f5f543}{\tt{3}}$$ | $$\textcolor{#f5f543}{\tt{7}}$$ |
| $$\textcolor{#f5f543}{\tt{TOTAL}}$$                            |  $$\textcolor{#23d18b}{\tt{51}}$$ |   $$\textcolor{#f5f543}{\tt{9}}$$ | $$\textcolor{#f5f543}{\tt{60}}$$ |


## Branch counts

Currently the number of branch tests stands at 2, with 2 passing and 0 failing (100.00% coverage).

|                   filepath                   |         function         | $$\textcolor{#23d18b}{\tt{passed}}$$ | SUBTOTAL |
| -------------------------------------------- | ------------------------ | --------------------------------: | -------: |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\text{\_}branch\text{\_}counts.py}}$$ | $$\textcolor{#23d18b}{\tt{test\text{\_}simple\text{\_}branch\text{\_}count}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\text{\_}branch\text{\_}counts.py}}$$ | $$\textcolor{#23d18b}{\tt{test\text{\_}double\text{\_}branch\text{\_}count}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
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
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\text{\_}loops.py}}$$ | $$\textcolor{#23d18b}{\tt{test\text{\_}self\text{\_}loop}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\text{\_}loops.py}}$$ | $$\textcolor{#23d18b}{\tt{TestNestedLoops.test\text{\_}nested\text{\_}normal\text{\_}loop}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\text{\_}loops.py}}$$ | $$\textcolor{#23d18b}{\tt{TestNestedLoops.test\text{\_}nested\text{\_}self\text{\_}loop}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\text{\_}loops.py}}$$ | $$\textcolor{#23d18b}{\tt{TestNestedLogicBlocks.test\text{\_}nested\text{\_}and}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\text{\_}loops.py}}$$ | $$\textcolor{#23d18b}{\tt{TestNestedLogicBlocks.test\text{\_}nested\text{\_}or}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\text{\_}loops.py}}$$ | $$\textcolor{#23d18b}{\tt{TestNestedLogicBlocks.test\text{\_}nested\text{\_}xor}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\text{\_}loops.py}}$$ | $$\textcolor{#23d18b}{\tt{TestNestedLogicBlocks.test\text{\_}logic\text{\_}bunched}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\text{\_}loops.py}}$$ | $$\textcolor{#23d18b}{\tt{test\text{\_}nested\text{\_}branch\text{\_}counts}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\text{\_}loops.py}}$$ | $$\textcolor{#f5f543}{\tt{TestBreakPoints.test\text{\_}loop\text{\_}break\text{\_}point}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ |   $$\textcolor{#f5f543}{\tt{1}}$$ | $$\textcolor{#f5f543}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\text{\_}loops.py}}$$ | $$\textcolor{#f5f543}{\tt{TestBreakPoints.test\text{\_}loop\text{\_}two\text{\_}break\text{\_}points}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ |   $$\textcolor{#f5f543}{\tt{1}}$$ | $$\textcolor{#f5f543}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\text{\_}loops.py}}$$ | $$\textcolor{#f5f543}{\tt{TestBreakPoints.test\text{\_}loop\text{\_}nested\text{\_}break\text{\_}point}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ |   $$\textcolor{#f5f543}{\tt{1}}$$ | $$\textcolor{#f5f543}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\text{\_}loops.py}}$$ | $$\textcolor{#f5f543}{\tt{TestEdgeCases.test\text{\_}loop\text{\_}break\text{\_}split\text{\_}exit}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ |   $$\textcolor{#f5f543}{\tt{1}}$$ | $$\textcolor{#f5f543}{\tt{1}}$$ |
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
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}simple.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintAND.test\text{\_}simple\text{\_}AND}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}simple.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintOR.test\text{\_}simple\text{\_}OR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}simple.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintXOR.test\text{\_}simple\text{\_}XOR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}simple.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintXOR.test\text{\_}merge\text{\_}at\text{\_}correct\text{\_}event\text{\_}XOR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}simple.py}}$$ | $$\textcolor{#f5f543}{\tt{TestConstraintAND.test\text{\_}multiple\text{\_}same\text{\_}event\text{\_}AND}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ |   $$\textcolor{#f5f543}{\tt{1}}$$ | $$\textcolor{#f5f543}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}simple.py}}$$ | $$\textcolor{#f5f543}{\tt{TestConstraintAND.test\text{\_}merge\text{\_}at\text{\_}correct\text{\_}event\text{\_}AND}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ |   $$\textcolor{#f5f543}{\tt{1}}$$ | $$\textcolor{#f5f543}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}simple.py}}$$ | $$\textcolor{#f5f543}{\tt{TestConstraintOR.test\text{\_}merge\text{\_}at\text{\_}correct\text{\_}event\text{\_}OR}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ |   $$\textcolor{#f5f543}{\tt{1}}$$ | $$\textcolor{#f5f543}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{TOTAL}}$$                           |                                                   |   $$\textcolor{#23d18b}{\tt{4}}$$ |   $$\textcolor{#f5f543}{\tt{3}}$$ | $$\textcolor{#f5f543}{\tt{7}}$$ |


### Nested

Currently the number of nested tests stands at 15, with 15 passing and 0 failing (100.00% coverage).

|                           filepath                            |                   function                    | $$\textcolor{#23d18b}{\tt{passed}}$$ | SUBTOTAL |
| ------------------------------------------------------------- | --------------------------------------------- | --------------------------------: | -------: |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedAND.test\text{\_}AND\text{\_}AND}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedAND.test\text{\_}AND\text{\_}OR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedAND.test\text{\_}AND\text{\_}XOR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedAND.test\text{\_}AND\text{\_}branch\text{\_}count}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedAND.test\text{\_}AND\text{\_}loop}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedOR.test\text{\_}OR\text{\_}AND}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedOR.test\text{\_}OR\text{\_}OR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedOR.test\text{\_}OR\text{\_}XOR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedOR.test\text{\_}OR\text{\_}branch\text{\_}count}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedOR.test\text{\_}OR\text{\_}loop}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedXOR.test\text{\_}XOR\text{\_}AND}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedXOR.test\text{\_}XOR\text{\_}OR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedXOR.test\text{\_}XOR\text{\_}XOR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedXOR.test\text{\_}XOR\text{\_}branch\text{\_}count}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedXOR.test\text{\_}XOR\text{\_}loop}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{TOTAL}}$$                           |                                               |  $$\textcolor{#23d18b}{\tt{15}}$$ | $$\textcolor{#23d18b}{\tt{15}}$$ |


### Bunched

Currently the number of bunched tests stands at 20, with 20 passing and 0 failing (100.00% coverage).

|                            filepath                            |                      function                       | $$\textcolor{#23d18b}{\tt{passed}}$$ | SUBTOTAL |
| -------------------------------------------------------------- | --------------------------------------------------- | --------------------------------: | -------: |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedAND.test\text{\_}bunched\text{\_}AND\text{\_}AND}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedAND.test\text{\_}bunched\text{\_}AND\text{\_}OR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedAND.test\text{\_}bunched\text{\_}AND\text{\_}XOR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedAND.test\text{\_}bunched\text{\_}merge\text{\_}AND\text{\_}AND}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedAND.test\text{\_}bunched\text{\_}merge\text{\_}AND\text{\_}OR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedAND.test\text{\_}bunched\text{\_}merge\text{\_}AND\text{\_}XOR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedOR.test\text{\_}bunched\text{\_}OR\text{\_}AND}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedOR.test\text{\_}bunched\text{\_}OR\text{\_}OR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedOR.test\text{\_}bunched\text{\_}OR\text{\_}XOR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedOR.test\text{\_}bunched\text{\_}merge\text{\_}OR\text{\_}AND}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedOR.test\text{\_}bunched\text{\_}merge\text{\_}OR\text{\_}OR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedOR.test\text{\_}bunched\text{\_}merge\text{\_}OR\text{\_}XOR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedXOR.test\text{\_}bunched\text{\_}XOR\text{\_}AND}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedXOR.test\text{\_}bunched\text{\_}XOR\text{\_}OR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedXOR.test\text{\_}bunched\text{\_}XOR\text{\_}XOR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedXOR.test\text{\_}bunched\text{\_}merge\text{\_}XOR\text{\_}AND}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedXOR.test\text{\_}bunched\text{\_}merge\text{\_}XOR\text{\_}OR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedXOR.test\text{\_}bunched\text{\_}merge\text{\_}XOR\text{\_}XOR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestBunchedHard.test\text{\_}bunched\text{\_}three\text{\_}levels\text{\_}AND}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestBunchedHard.test\text{\_}bunched\text{\_}three\text{\_}levels\text{\_}XOR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{TOTAL}}$$                            |                                                     |  $$\textcolor{#23d18b}{\tt{20}}$$ | $$\textcolor{#23d18b}{\tt{20}}$$ |


### Kill/Detach

Currently the number of kill tests stands at 4, with 2 passing and 2 failing (50.00% coverage).

xfailed:
* `tests/end-to-end-tests/constraints/test_constraints_kill.py::test_kill_with_merge_on_parent`
* `tests/end-to-end-tests/constraints/test_constraints_kill.py::test_kill_in_loop`

|                          filepath                           |            function            | $$\textcolor{#23d18b}{\tt{passed}}$$ | $$\textcolor{#f5f543}{\tt{xfailed}}$$ | SUBTOTAL |
| ----------------------------------------------------------- | ------------------------------ | --------------------------------: | --------------------------------: | -------: |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}kill.py}}$$ | $$\textcolor{#23d18b}{\tt{test\text{\_}kill\text{\_}with\text{\_}no\text{\_}merge}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}kill.py}}$$ | $$\textcolor{#23d18b}{\tt{test\text{\_}kill\text{\_}with\text{\_}merge}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}kill.py}}$$ | $$\textcolor{#f5f543}{\tt{test\text{\_}kill\text{\_}with\text{\_}merge\text{\_}on\text{\_}parent}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ |   $$\textcolor{#f5f543}{\tt{1}}$$ | $$\textcolor{#f5f543}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\text{\_}constraints\text{\_}kill.py}}$$ | $$\textcolor{#f5f543}{\tt{test\text{\_}kill\text{\_}in\text{\_}loop}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ |   $$\textcolor{#f5f543}{\tt{1}}$$ | $$\textcolor{#f5f543}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{TOTAL}}$$                         |                                |   $$\textcolor{#23d18b}{\tt{2}}$$ |   $$\textcolor{#f5f543}{\tt{2}}$$ | $$\textcolor{#f5f543}{\tt{4}}$$ |



