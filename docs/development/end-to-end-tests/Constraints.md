# End-to-end tests Constraints
End to end test cases for cases involving constraints.
## Contents
* [Simple](/docs/development/end-to-end-tests/Constraints/Simple)
    * [AND](/docs/development/end-to-end-tests/Constraints/Simple#and)
        * Basic
        * Multiple same events
        * Merge at correct event
    * [XOR](/docs/development/end-to-end-tests/Constraints/Simple#xor)
        * Basic
        * Merge at correct event
    * [OR](/docs/development/end-to-end-tests/Constraints/Simple#or)
        * Basic
        * Merge at correct event
* [Nested](/docs/development/end-to-end-tests/Constraints/Nested)
    * [AND](/docs/development/end-to-end-tests/Constraints/Nested#and)
        * AND
        * XOR
        * OR
        * Loop
        * Branch counts
    * [XOR](/docs/development/end-to-end-tests/Constraints/Nested#xor)
        * AND
        * XOR
        * OR
        * Loop
        * Branch counts
    * [OR](/docs/development/end-to-end-tests/Constraints/Nested#or)
        * AND
        * XOR
        * OR
        * Loop
        * Branch counts
* [Kill/detach](/docs/development/end-to-end-tests/Constraints/Kill_detach)
    * [No merge](/docs/development/end-to-end-tests/Constraints/Kill_detach#no-merge)
    * [With merge](/docs/development/end-to-end-tests/Constraints/Kill_detach#with-merge)
    * [Merge on parent](/docs/development/end-to-end-tests/Constraints/Kill_detach#merge-on-parent)
    * [In loops](/docs/development/end-to-end-tests/Constraints/Kill_detach#in-loops)
* [Bunched](/docs/development/end-to-end-tests/Constraints/Bunched)
    * [Bunched with AND as highest level](/docs/development/end-to-end-tests/Constraints/Bunched#and)
        * [Bunched with AND as next level](/docs/development/end-to-end-tests/Constraints/Bunched#and-and)
            * With event in between merge and branch
            * Without event in between merge and branch
        * [Bunched with XOR as next level](/docs/development/end-to-end-tests/Constraints/Bunched#and-xor)
            * With event in between merge and branch
            * Without event in between merge and branch
        * [Bunched with OR as next level](/docs/development/end-to-end-tests/Constraints/Bunched#and-or)
            * With event in between merge and branch
            * Without event in between merge and branch
    * [Bunched with XOR as highest level](/docs/development/end-to-end-tests/Constraints/Bunched#xor)
        * [Bunched with AND as next level](/docs/development/end-to-end-tests/Constraints/Bunched#xor-and)
            * With event in between merge and branch
            * Without event in between merge and branch
        * [Bunched with XOR as next level](/docs/development/end-to-end-tests/Constraints/Bunched#xor-xor)
            * With event in between merge and branch
            * Without event in between merge and branch
        * [Bunched with OR as next level](/docs/development/end-to-end-tests/Constraints/Bunched#xor-or)
            * With event in between merge and branch
            * Without event in between merge and branch
    * [Bunched with OR as highest level](/docs/development/end-to-end-tests/Constraints/Bunched#or)
        * [Bunched with AND as next level](/docs/development/end-to-end-tests/Constraints/Bunched#or-and)
            * With event in between merge and branch
            * Without event in between merge and branch
        * [Bunched with XOR as next level](/docs/development/end-to-end-tests/Constraints/Bunched#or-xor)
            * With event in between merge and branch
            * Without event in between merge and branch
        * [Bunched with OR as next level](/docs/development/end-to-end-tests/Constraints/Bunched#or-or)
            * With event in between merge and branch
            * Without event in between merge and branch
    * [Three levels of bunching of same logic type](/docs/development/end-to-end-tests/Constraints/Bunched#three-levels-of-bunching-of-same-logic-type)
        * [AND](/docs/development/end-to-end-tests/Constraints/Bunched#three-and)
        * [XOR](/docs/development/end-to-end-tests/Constraints/Bunched#three-xor)