# End-to-end tests Constraints
End to end test cases for cases involving constraints.
## Contents
* [Simple](./Constraints/Simple)
    * [AND](./Constraints/Simple#and)
        * Basic
        * Multiple same events
        * Merge at correct event
    * [XOR](./Constraints/Simple#xor)
        * Basic
        * Merge at correct event
    * [OR](./Constraints/Simple#or)
        * Basic
        * Merge at correct event
* [Nested](./Constraints/Nested)
    * [AND](./Constraints/Nested#and)
        * AND
        * XOR
        * OR
        * Loop
        * Branch counts
    * [XOR](./Constraints/Nested#xor)
        * AND
        * XOR
        * OR
        * Loop
        * Branch counts
    * [OR](./Constraints/Nested#or)
        * AND
        * XOR
        * OR
        * Loop
        * Branch counts
* [Kill/detach](./Constraints/Kill_detach)
    * [No merge](./Constraints/Kill_detach#no-merge)
    * [With merge](./Constraints/Kill_detach#with-merge)
    * [Merge on parent](./Constraints/Kill_detach#merge-on-parent)
    * [In loops](./Constraints/Kill_detach#in-loops)
* [Bunched](./Constraints/Bunched)
    * [Bunched with AND as highest level](./Constraints/Bunched#and)
        * [Bunched with AND as next level](./Constraints/Bunched#and-and)
            * With event in between merge and branch
            * Without event in between merge and branch
        * [Bunched with XOR as next level](./Constraints/Bunched#and-xor)
            * With event in between merge and branch
            * Without event in between merge and branch
        * [Bunched with OR as next level](./Constraints/Bunched#and-or)
            * With event in between merge and branch
            * Without event in between merge and branch
    * [Bunched with XOR as highest level](./Constraints/Bunched#xor)
        * [Bunched with AND as next level](./Constraints/Bunched#xor-and)
            * With event in between merge and branch
            * Without event in between merge and branch
        * [Bunched with XOR as next level](./Constraints/Bunched#xor-xor)
            * With event in between merge and branch
            * Without event in between merge and branch
        * [Bunched with OR as next level](./Constraints/Bunched#xor-or)
            * With event in between merge and branch
            * Without event in between merge and branch
    * [Bunched with OR as highest level](./Constraints/Bunched#or)
        * [Bunched with AND as next level](./Constraints/Bunched#or-and)
            * With event in between merge and branch
            * Without event in between merge and branch
        * [Bunched with XOR as next level](./Constraints/Bunched#or-xor)
            * With event in between merge and branch
            * Without event in between merge and branch
        * [Bunched with OR as next level](./Constraints/Bunched#or-or)
            * With event in between merge and branch
            * Without event in between merge and branch
    * [Three levels of bunching of same logic type](./Constraints/Bunched#three-levels-of-bunching-of-same-logic-type)
        * [AND](./Constraints/Bunched#three-and)
        * [XOR](./Constraints/Bunched#three-xor)