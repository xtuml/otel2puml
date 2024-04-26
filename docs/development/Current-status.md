# Current Status
Currently the number of end to end tests stands at 60 with 46 passing and 14 failing (77% coverage). An overview breakdown of the tests is presented below.

|                            filepath                            | $$\textcolor{#23d18b}{\tt{passed}}$$ | $$\textcolor{#f5f543}{\tt{xfailed}}$$ | SUBTOTAL |
| -------------------------------------------------------------- | --------------------------------: | --------------------------------: | -------: |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\_branch\_counts.py}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\_loops.py}}$$ |   $$\textcolor{#23d18b}{\tt{8}}$$ |   $$\textcolor{#f5f543}{\tt{4}}$$ | $$\textcolor{#f5f543}{\tt{12}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_bunched.py}}$$ |  $$\textcolor{#23d18b}{\tt{15}}$$ |   $$\textcolor{#f5f543}{\tt{5}}$$ | $$\textcolor{#f5f543}{\tt{20}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_kill.py}}$$ |   $$\textcolor{#23d18b}{\tt{2}}$$ |   $$\textcolor{#f5f543}{\tt{2}}$$ | $$\textcolor{#f5f543}{\tt{4}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_nested.py}}$$ |  $$\textcolor{#23d18b}{\tt{15}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{15}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_simple.py}}$$ |   $$\textcolor{#23d18b}{\tt{4}}$$ |   $$\textcolor{#f5f543}{\tt{3}}$$ | $$\textcolor{#f5f543}{\tt{7}}$$ |
| $$\textcolor{#f5f543}{\tt{TOTAL}}$$                            |  $$\textcolor{#23d18b}{\tt{46}}$$ |  $$\textcolor{#f5f543}{\tt{14}}$$ | $$\textcolor{#f5f543}{\tt{60}}$$ |
## Branch counts
Able to handle all branch count cases. The associated tests are 
|                   filepath                   |         function         | $$\textcolor{#23d18b}{\tt{passed}}$$ | SUBTOTAL |
| -------------------------------------------- | ------------------------ | --------------------------------: | -------: |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\_branch\_counts.py}}$$ | $$\textcolor{#23d18b}{\tt{test\_simple\_branch\_count}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\_branch\_counts.py}}$$ | $$\textcolor{#23d18b}{\tt{test\_double\_branch\_count}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{TOTAL}}$$          |                          |   $$\textcolor{#23d18b}{\tt{2}}$$ | $$\textcolor{#23d18b}{\tt{2}}$$ |                                      |                          |      2 |        2 |

## Loops
Able to handle all loop cases except break points which need updating. Failures:
* Cases with break points:
    * `tests/end-to-end-tests/test_loops.py::TestBreakPoints::test_loop_break_point`
    * `tests/end-to-end-tests/test_loops.py::TestBreakPoints::test_loop_two_break_points`
    * `tests/end-to-end-tests/test_loops.py::TestBreakPoints::test_loop_nested_break_point`
    * `tests/end-to-end-tests/test_loops.py::TestEdgeCases::test_loop_break_split_exit`

|               filepath               |                   function                   | $$\textcolor{#23d18b}{\tt{passed}}$$ | $$\textcolor{#f5f543}{\tt{xfailed}}$$ | SUBTOTAL |
| ------------------------------------ | -------------------------------------------- | --------------------------------: | --------------------------------: | -------: |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\_loops.py}}$$ | $$\textcolor{#23d18b}{\tt{test\_self\_loop}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\_loops.py}}$$ | $$\textcolor{#23d18b}{\tt{TestNestedLoops.test\_nested\_normal\_loop}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\_loops.py}}$$ | $$\textcolor{#23d18b}{\tt{TestNestedLoops.test\_nested\_self\_loop}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\_loops.py}}$$ | $$\textcolor{#23d18b}{\tt{TestNestedLogicBlocks.test\_nested\_and}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\_loops.py}}$$ | $$\textcolor{#23d18b}{\tt{TestNestedLogicBlocks.test\_nested\_or}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\_loops.py}}$$ | $$\textcolor{#23d18b}{\tt{TestNestedLogicBlocks.test\_nested\_xor}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\_loops.py}}$$ | $$\textcolor{#23d18b}{\tt{TestNestedLogicBlocks.test\_logic\_bunched}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\_loops.py}}$$ | $$\textcolor{#23d18b}{\tt{test\_nested\_branch\_counts}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\_loops.py}}$$ | $$\textcolor{#f5f543}{\tt{TestBreakPoints.test\_loop\_break\_point}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ |   $$\textcolor{#f5f543}{\tt{1}}$$ | $$\textcolor{#f5f543}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\_loops.py}}$$ | $$\textcolor{#f5f543}{\tt{TestBreakPoints.test\_loop\_two\_break\_points}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ |   $$\textcolor{#f5f543}{\tt{1}}$$ | $$\textcolor{#f5f543}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\_loops.py}}$$ | $$\textcolor{#f5f543}{\tt{TestBreakPoints.test\_loop\_nested\_break\_point}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ |   $$\textcolor{#f5f543}{\tt{1}}$$ | $$\textcolor{#f5f543}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/test\_loops.py}}$$ | $$\textcolor{#f5f543}{\tt{TestEdgeCases.test\_loop\_break\_split\_exit}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ |   $$\textcolor{#f5f543}{\tt{1}}$$ | $$\textcolor{#f5f543}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{TOTAL}}$$  |                                              |   $$\textcolor{#23d18b}{\tt{8}}$$ |   $$\textcolor{#f5f543}{\tt{4}}$$ | $$\textcolor{#f5f543}{\tt{12}}$$ |

## Constraints
### One level
Handles most simple constraints. Failures:
* multiple of the same event when coming off and AND constraint (`tests/end-to-end-tests/constraints/test_constraints_simple.TestConstraintAND.test_multiple_same_event_AND`)
* merge at correct event when coming off an AND or OR constraint
    * `tests/end-to-end-tests/constraints/test_constraints_simple.TestConstraintAND.test_merge_at_correct_event_AND`
    * `tests/end-to-end-tests/constraints/test_constraints_simple.TestConstraintOR.test_merge_at_correct_event_OR`

|                           filepath                            |                     function                      | $$\textcolor{#23d18b}{\tt{passed}}$$ | $$\textcolor{#f5f543}{\tt{xfailed}}$$ | SUBTOTAL |
| ------------------------------------------------------------- | ------------------------------------------------- | --------------------------------: | --------------------------------: | -------: |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_simple.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintAND.test\_simple\_AND}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_simple.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintOR.test\_simple\_OR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_simple.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintXOR.test\_simple\_XOR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_simple.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintXOR.test\_merge\_at\_correct\_event\_XOR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_simple.py}}$$ | $$\textcolor{#f5f543}{\tt{TestConstraintAND.test\_multiple\_same\_event\_AND}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ |   $$\textcolor{#f5f543}{\tt{1}}$$ | $$\textcolor{#f5f543}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_simple.py}}$$ | $$\textcolor{#f5f543}{\tt{TestConstraintAND.test\_merge\_at\_correct\_event\_AND}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ |   $$\textcolor{#f5f543}{\tt{1}}$$ | $$\textcolor{#f5f543}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_simple.py}}$$ | $$\textcolor{#f5f543}{\tt{TestConstraintOR.test\_merge\_at\_correct\_event\_OR}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ |   $$\textcolor{#f5f543}{\tt{1}}$$ | $$\textcolor{#f5f543}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{TOTAL}}$$                           |                                                   |   $$\textcolor{#23d18b}{\tt{4}}$$ |   $$\textcolor{#f5f543}{\tt{3}}$$ | $$\textcolor{#f5f543}{\tt{7}}$$ |
### Nested
Handles nesting of all structures within logic blocks. No failures

|                           filepath                            |                   function                    | $$\textcolor{#23d18b}{\tt{passed}}$$ | SUBTOTAL |
| ------------------------------------------------------------- | --------------------------------------------- | --------------------------------: | -------: |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedAND.test\_AND\_AND}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedAND.test\_AND\_OR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedAND.test\_AND\_XOR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedAND.test\_AND\_branch\_count}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedAND.test\_AND\_loop}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedOR.test\_OR\_AND}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedOR.test\_OR\_OR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedOR.test\_OR\_XOR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedOR.test\_OR\_branch\_count}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedOR.test\_OR\_loop}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedXOR.test\_XOR\_AND}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedXOR.test\_XOR\_OR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedXOR.test\_XOR\_XOR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedXOR.test\_XOR\_branch\_count}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_nested.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintNestedXOR.test\_XOR\_loop}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{TOTAL}}$$                           |                                               |  $$\textcolor{#23d18b}{\tt{15}}$$ | $$\textcolor{#23d18b}{\tt{15}}$$ |
### Bunched
Can handle all bunched constraints except for those with the same operator. Failures:
* cases with bunched logic of the same type cases:
    * `tests/end-to-end-tests/constraints/test_constraints_bunched.TestConstraintBunchedAND.test_bunched_AND_AND`
    * `tests/end-to-end-tests/constraints/test_constraints_bunched.TestConstraintBunchedOR.test_bunched_OR_OR`
    * `tests/end-to-end-tests/constraints/test_constraints_bunched.TestConstraintBunchedXOR.test_bunched_XOR_XOR`
    * `tests/end-to-end-tests/constraints/test_constraints_bunched.TestBunchedHard.test_bunched_three_levels_AND`
    * `tests/end-to-end-tests/constraints/test_constraints_bunched.TestBunchedHard.test_bunched_three_levels_XOR`

|                            filepath                            |                      function                       | $$\textcolor{#23d18b}{\tt{passed}}$$ | $$\textcolor{#f5f543}{\tt{xfailed}}$$ | SUBTOTAL |
| -------------------------------------------------------------- | --------------------------------------------------- | --------------------------------: | --------------------------------: | -------: |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_bunched.py}}$$ | $$\textcolor{#f5f543}{\tt{TestConstraintBunchedAND.test\_bunched\_AND\_AND}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ |   $$\textcolor{#f5f543}{\tt{1}}$$ | $$\textcolor{#f5f543}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_bunched.py}}$$ | $$\textcolor{#f5f543}{\tt{TestConstraintBunchedOR.test\_bunched\_OR\_OR}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ |   $$\textcolor{#f5f543}{\tt{1}}$$ | $$\textcolor{#f5f543}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_bunched.py}}$$ | $$\textcolor{#f5f543}{\tt{TestConstraintBunchedXOR.test\_bunched\_XOR\_XOR}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ |   $$\textcolor{#f5f543}{\tt{1}}$$ | $$\textcolor{#f5f543}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_bunched.py}}$$ | $$\textcolor{#f5f543}{\tt{TestBunchedHard.test\_bunched\_three\_levels\_AND}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ |   $$\textcolor{#f5f543}{\tt{1}}$$ | $$\textcolor{#f5f543}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_bunched.py}}$$ | $$\textcolor{#f5f543}{\tt{TestBunchedHard.test\_bunched\_three\_levels\_XOR}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ |   $$\textcolor{#f5f543}{\tt{1}}$$ | $$\textcolor{#f5f543}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedAND.test\_bunched\_AND\_OR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedAND.test\_bunched\_AND\_XOR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedAND.test\_bunched\_merge\_AND\_AND}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedAND.test\_bunched\_merge\_AND\_OR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedAND.test\_bunched\_merge\_AND\_XOR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedOR.test\_bunched\_OR\_AND}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedOR.test\_bunched\_OR\_XOR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedOR.test\_bunched\_merge\_OR\_AND}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedOR.test\_bunched\_merge\_OR\_OR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedOR.test\_bunched\_merge\_OR\_XOR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedXOR.test\_bunched\_XOR\_AND}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedXOR.test\_bunched\_XOR\_OR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedXOR.test\_bunched\_merge\_XOR\_AND}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedXOR.test\_bunched\_merge\_XOR\_OR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_bunched.py}}$$ | $$\textcolor{#23d18b}{\tt{TestConstraintBunchedXOR.test\_bunched\_merge\_XOR\_XOR}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{TOTAL}}$$                            |                                                     |  $$\textcolor{#23d18b}{\tt{15}}$$ |   $$\textcolor{#f5f543}{\tt{5}}$$ | $$\textcolor{#f5f543}{\tt{20}}$$ |

### Kill/Detach
Can handle about half of the kill/detach constraints. Failures:
* merge on parent without a known merge in the logic block where the kill occurs (`tests/end-to-end-tests/constraints/test_constraints_kill.test_kill_with_merge_on_parent`)
* within a loop and the logic ends up extending further than the loop end. (`tests/end-to-end-tests/constraints/test_constraints_kill.test_kill_in_loop`)

|                          filepath                           |            function            | $$\textcolor{#23d18b}{\tt{passed}}$$ | $$\textcolor{#f5f543}{\tt{xfailed}}$$ | SUBTOTAL |
| ----------------------------------------------------------- | ------------------------------ | --------------------------------: | --------------------------------: | -------: |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_kill.py}}$$ | $$\textcolor{#23d18b}{\tt{test\_kill\_with\_no\_merge}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#23d18b}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_kill.py}}$$ | $$\textcolor{#23d18b}{\tt{test\_kill\_with\_merge}}$$ |   $$\textcolor{#23d18b}{\tt{1}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ | $$\textcolor{#23d18b}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_kill.py}}$$ | $$\textcolor{#f5f543}{\tt{test\_kill\_with\_merge\_on\_parent}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ |   $$\textcolor{#f5f543}{\tt{1}}$$ | $$\textcolor{#f5f543}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{tests/end\text{-}to\text{-}end\text{-}tests/constraints/test\_constraints\_kill.py}}$$ | $$\textcolor{#f5f543}{\tt{test\_kill\_in\_loop}}$$ |   $$\textcolor{#666666}{\tt{0}}$$ |   $$\textcolor{#f5f543}{\tt{1}}$$ | $$\textcolor{#f5f543}{\tt{1}}$$ |
| $$\textcolor{#f5f543}{\tt{TOTAL}}$$                         |                                |   $$\textcolor{#23d18b}{\tt{2}}$$ |   $$\textcolor{#f5f543}{\tt{2}}$$ | $$\textcolor{#f5f543}{\tt{4}}$$ |
