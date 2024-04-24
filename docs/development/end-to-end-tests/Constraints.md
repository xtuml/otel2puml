# End-to-end tests Constraints
End to end test cases for cases involving constraints.
## Contents
* [Simple](./Constraints/Simple.md)
    * [AND](./Constraints/Simple.md#and)
        * Basic
        * Multiple same events
        * Merge at correct event
    * [XOR](./Constraints/Simple.md#xor)
        * Basic
        * Merge at correct event
    * [OR](./Constraints/Simple.md#or)
        * Basic
        * Merge at correct event
* [Nested](./Constraints/Nested.md)
    * [AND](./Constraints/Nested.md#and)
        * AND
        * XOR
        * OR
        * Loop
        * Branch counts
    * [XOR](./Constraints/Nested.md#xor)
        * AND
        * XOR
        * OR
        * Loop
        * Branch counts
    * [OR](./Constraints/Nested.md#or)
        * AND
        * XOR
        * OR
        * Loop
        * Branch counts
* [Kill/detach](./Constraints/Kill_detach.md)
    * [No merge](./Constraints/Kill_detach.md#no-merge)
    * [With merge](./Constraints/Kill_detach.md#with-merge)
    * [Merge on parent](./Constraints/Kill_detach.md#merge-on-parent)
    * [In loops](./Constraints/Kill_detach.md#in-loops)
* [Bunched](./Constraints/Bunched.md)
    * [Bunched with AND as highest level](./Constraints/Bunched.md#and)
        * [Bunched with AND as next level](./Constraints/Bunched.md#and-and)
            * With event in between merge and branch
            * Without event in between merge and branch
        * [Bunched with XOR as next level](./Constraints/Bunched.md#and-xor)
            * With event in between merge and branch
            * Without event in between merge and branch
        * [Bunched with OR as next level](./Constraints/Bunched.md#and-or)
            * With event in between merge and branch
            * Without event in between merge and branch
    * [Bunched with XOR as highest level](./Constraints/Bunched.md#xor)
        * [Bunched with AND as next level](./Constraints/Bunched.md#xor-and)
            * With event in between merge and branch
            * Without event in between merge and branch
        * [Bunched with XOR as next level](./Constraints/Bunched.md#xor-xor)
            * With event in between merge and branch
            * Without event in between merge and branch
        * [Bunched with OR as next level](./Constraints/Bunched.md#xor-or)
            * With event in between merge and branch
            * Without event in between merge and branch
    * [Bunched with OR as highest level](./Constraints/Bunched.md#or)
        * [Bunched with AND as next level](./Constraints/Bunched.md#or-and)
            * With event in between merge and branch
            * Without event in between merge and branch
        * [Bunched with XOR as next level](./Constraints/Bunched.md#or-xor)
            * With event in between merge and branch
            * Without event in between merge and branch
        * [Bunched with OR as next level](./Constraints/Bunched.md#or-or)
            * With event in between merge and branch
            * Without event in between merge and branch
    * [Three levels of bunching of same logic type](./Constraints/Bunched.md#three-levels-of-bunching-of-same-logic-type)
        * [AND](./Constraints/Bunched.md#three-and)
        * [XOR](./Constraints/Bunched.md#three-xor)