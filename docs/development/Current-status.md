
# Current Status
Below we present the current status of the end-to-end tests.
The tests are divided into the following categories:
* [Branch counts](#branch-counts)
* [Loops](#loops)
* [Constraints](#constraints)
    * [One level](#one-level)
    * [Nested](#nested)
    * [Bunched](#bunched)
    * [Kill Detach](#kill-detach)

Currently the number of end-to-end tests stands at 70, with 69 passing and 1 failing (98.57% coverage).

|                            filepath                            | $$\textcolor{#23d18b}{\tt{passed}}$$ | $$\textcolor{#f5f543}{\tt{xfailed}}$$ | SUBTOTAL |
| -------------------------------------------------------------- | --------------------------------: | --------------------------------: | -------: |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\\_branch\\_counts.py}}$$ |   $$\textcolor{#23d18b}{\tt{8}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{8}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\\_loops.py}}$$ |  $$\textcolor{#23d18b}{\tt{30}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{30}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_bunched.py}}$$ |  $$\textcolor{#23d18b}{\tt{42}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{42}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_kill.py}}$$ |   $$\textcolor{#23d18b}{\tt{6}}$$ |   $$\textcolor{#f5f543}{\tt{2}}$$ | $$\textcolor{#f5f543}{\tt{8}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_nested.py}}$$ |  $$\textcolor{#23d18b}{\tt{30}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{30}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_simple.py}}$$ |  $$\textcolor{#23d18b}{\tt{22}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{22}}$$ |
| $$\textcolor{#f5f543}{\tt{TOTAL}}$$                            | $$\textcolor{#23d18b}{\tt{138}}$$ |   $$\textcolor{#f5f543}{\tt{2}}$$ | $$\textcolor{#f5f543}{\tt{140}}$$ |


## Branch counts

Currently the number of branch tests stands at 4, with 4 passing and 0 failing (100.00% coverage).

|                   filepath                   |           function           | $$\textcolor{#23d18b}{\tt{passed}}$$ | SUBTOTAL |
| -------------------------------------------- | ---------------------------- | --------------------------------: | -------: |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\\_branch\\_counts.py}}$$ | $$\textcolor{#23d18b}{\tt{test\\_simple\\_branch\\_count}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\\_branch\\_counts.py}}$$ | $$\textcolor{#23d18b}{\tt{test\\_double\\_branch\\_count}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\\_branch\\_counts.py}}$$ | $$\textcolor{#23d18b}{\tt{test\\_branch\\_with\\_bunched\\_OR}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\\_branch\\_counts.py}}$$ | $$\textcolor{#23d18b}{\tt{test\\_branch\\_with\\_bunched\\_AND}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{TOTAL}}$$          |                              |   $$\textcolor{#23d18b}{\tt{8}}$$ | $$\textcolor{#23d18b}{\tt{8}}$$ |


## Loops

Currently the number of loops tests stands at 15, with 15 passing and 0 failing (100.00% coverage).

|               filepath               |                                  function                                  | $$\textcolor{#23d18b}{\tt{passed}}$$ | SUBTOTAL |
| ------------------------------------ | -------------------------------------------------------------------------- | --------------------------------: | -------: |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\\_loops.py}}$$ | $$\textcolor{#23d18b}{\tt{test\\_self\\_loop}}$$                           |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\\_loops.py}}$$ | $$\textcolor{#23d18b}{\tt{TestNestedLoops.test\\_nested\\_normal\\_loop}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\\_loops.py}}$$ | $$\textcolor{#23d18b}{\tt{TestNestedLoops.test\\_nested\\_self\\_loop}}$$  |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\\_loops.py}}$$ | $$\textcolor{#23d18b}{\tt{TestNestedLogicBlocks.test\\_nested\\_and}}$$    |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\\_loops.py}}$$ | $$\textcolor{#23d18b}{\tt{TestNestedLogicBlocks.test\\_nested\\_or}}$$     |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\\_loops.py}}$$ | $$\textcolor{#23d18b}{\tt{TestNestedLogicBlocks.test\\_nested\\_xor}}$$    |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\\_loops.py}}$$ | $$\textcolor{#23d18b}{\tt{TestNestedLogicBlocks.test\\_logic\\_bunched}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\\_loops.py}}$$ | $$\textcolor{#23d18b}{\tt{TestNestedBranchCounts.test\\_nested\\_branch\\_counts}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\\_loops.py}}$$ | $$\textcolor{#23d18b}{\tt{TestNestedBranchCounts.test\\_loop\\_nested\\_branch\\_counts\\_event\\_at\\_end\\_of\\_loop}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\\_loops.py}}$$ | $$\textcolor{#23d18b}{\tt{TestBreakPoints.test\\_loop\\_break\\_point}}$$  |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\\_loops.py}}$$ | $$\textcolor{#23d18b}{\tt{TestBreakPoints.test\\_loop\\_two\\_break\\_points}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\\_loops.py}}$$ | $$\textcolor{#23d18b}{\tt{TestBreakPoints.test\\_loop\\_nested\\_break\\_point}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\\_loops.py}}$$ | $$\textcolor{#23d18b}{\tt{TestEdgeCases.test\\_loop\\_break\\_split\\_exit}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\\_loops.py}}$$ | $$\textcolor{#23d18b}{\tt{TestEdgeCases.test\\_paths\\_should\\_kill\\_in\\_loop}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\\_loops.py}}$$ | $$\textcolor{#23d18b}{\tt{TestEdgeCases.test\\_two\\_different\\_loops\\_follow\\_same\\_event}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{TOTAL}}$$  |                                                                            |  $$\textcolor{#23d18b}{\tt{30}}$$ | $$\textcolor{#23d18b}{\tt{30}}$$ |


## Constraints
### One level

Currently the number of simple tests stands at 11, with 11 passing and 0 failing (100.00% coverage).

|                           filepath                            |                             function                             | $$\textcolor{#23d18b}{\tt{passed}}$$ | SUBTOTAL |
| ------------------------------------------------------------- | ---------------------------------------------------------------- | --------------------------------: | -------: |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_simple.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintAND.test\\_simple\\_AND}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_simple.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintAND.test\\_multiple\\_same\\_event\\_AND}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_simple.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintAND.test\\_multiple\\_same\\_event\\_AND\\_with\\_extra\\_branch}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_simple.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintAND.test\\_multiple\\_same\\_event\\_AND\\_with\\_self\\_loop}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_simple.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintAND.test\\_merge\\_at\\_correct\\_event\\_AND}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_simple.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintAND.test\\_merge\\_at\\_correct\\_event\\_AND\\_with\\_kill}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_simple.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintOR.test\\_simple\\_OR}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_simple.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintOR.test\\_merge\\_at\\_correct\\_event\\_OR}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_simple.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintXOR.test\\_simple\\_XOR}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_simple.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintXOR.test\\_merge\\_at\\_correct\\_event\\_XOR}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_simple.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintXOR.test\\_merge\\_from\\_similar\\_paths}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{TOTAL}}$$                           |                                                                  |  $$\textcolor{#23d18b}{\tt{22}}$$ | $$\textcolor{#23d18b}{\tt{22}}$$ |


### Nested

Currently the number of nested tests stands at 15, with 15 passing and 0 failing (100.00% coverage).

|                           filepath                            |                   function                    | $$\textcolor{#23d18b}{\tt{passed}}$$ | SUBTOTAL |
| ------------------------------------------------------------- | --------------------------------------------- | --------------------------------: | -------: |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedAND.test\\_AND\\_AND}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedAND.test\\_AND\\_OR}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedAND.test\\_AND\\_XOR}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedAND.test\\_AND\\_branch\\_count}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedAND.test\\_AND\\_loop}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedOR.test\\_OR\\_AND}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedOR.test\\_OR\\_OR}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedOR.test\\_OR\\_XOR}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedOR.test\\_OR\\_branch\\_count}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedOR.test\\_OR\\_loop}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedXOR.test\\_XOR\\_AND}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedXOR.test\\_XOR\\_OR}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedXOR.test\\_XOR\\_XOR}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedXOR.test\\_XOR\\_branch\\_count}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedXOR.test\\_XOR\\_loop}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{TOTAL}}$$                           |                                               |  $$\textcolor{#23d18b}{\tt{30}}$$ | $$\textcolor{#23d18b}{\tt{30}}$$ |


### Bunched

Currently the number of bunched tests stands at 21, with 21 passing and 0 failing (100.00% coverage).

|                            filepath                            |                      function                       | $$\textcolor{#23d18b}{\tt{passed}}$$ | SUBTOTAL |
| -------------------------------------------------------------- | --------------------------------------------------- | --------------------------------: | -------: |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedAND.test\\_bunched\\_AND\\_AND}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedAND.test\\_bunched\\_AND\\_OR}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedAND.test\\_bunched\\_AND\\_XOR}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedAND.test\\_bunched\\_merge\\_AND\\_AND}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedAND.test\\_bunched\\_merge\\_AND\\_OR}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedAND.test\\_bunched\\_merge\\_AND\\_XOR}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedOR.test\\_bunched\\_OR\\_AND}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedOR.test\\_bunched\\_OR\\_OR}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedOR.test\\_bunched\\_OR\\_XOR}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedOR.test\\_bunched\\_merge\\_OR\\_AND}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedOR.test\\_bunched\\_merge\\_OR\\_OR}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedOR.test\\_bunched\\_merge\\_OR\\_XOR}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedXOR.test\\_bunched\\_XOR\\_AND}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedXOR.test\\_bunched\\_XOR\\_OR}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedXOR.test\\_bunched\\_XOR\\_XOR}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedXOR.test\\_bunched\\_merge\\_XOR\\_AND}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedXOR.test\\_bunched\\_merge\\_XOR\\_OR}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedXOR.test\\_bunched\\_merge\\_XOR\\_XOR}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestBunchedHard.test\\_bunched\\_three\\_levels\\_AND}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestBunchedHard.test\\_bunched\\_three\\_levels\\_XOR}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestBunchedHard.test\\_bunched\\_XOR\\_XOR\\_with\\_kill}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{TOTAL}}$$                            |                                                     |  $$\textcolor{#23d18b}{\tt{42}}$$ | $$\textcolor{#23d18b}{\tt{42}}$$ |


### Kill Detach

Currently the number of kill tests stands at 4, with 3 passing and 1 failing (75.00% coverage).

xfailed:
* `tests/end-to-end-tests/constraints/test_constraints_kill.py::test_kill_with_merge_on_parent`

|                          filepath                           |            function            | $$\textcolor{#23d18b}{\tt{passed}}$$ | $$\textcolor{#f5f543}{\tt{xfailed}}$$ | SUBTOTAL |
| ----------------------------------------------------------- | ------------------------------ | --------------------------------: | --------------------------------: | -------: |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_kill.py}}$$ | $$\textcolor{#23d18b}{\tt{test\\_kill\\_with\\_no\\_merge}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_kill.py}}$$ | $$\textcolor{#23d18b}{\tt{test\\_kill\\_with\\_merge}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_kill.py}}$$ | $$\textcolor{#23d18b}{\tt{test\\_kill\\_in\\_loop}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\\_constraints\\_kill.py}}$$ | $$\textcolor{#f5f543}{\tt{test\\_kill\\_with\\_merge\\_on\\_parent}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ |   $$\textcolor{#f5f543}{\tt{2}}$$ | $$\textcolor{#f5f543}{\tt{2}}$$ |
| $$\textcolor{#f5f543}{\tt{TOTAL}}$$                         |                                |   $$\textcolor{#23d18b}{\tt{6}}$$ |   $$\textcolor{#f5f543}{\tt{2}}$$ | $$\textcolor{#f5f543}{\tt{8}}$$ |



