# End-to-end tests Constraints
End to end test cases for cases involving constraints.
## Contents
* [Simple](./constraints/simple.md)
    * [AND](./constraints/simple.md#and)
        * Basic
        * Multiple same events
        * Merge at correct event
    * [XOR](./constraints/simple.md#xor)
        * Basic
        * Merge at correct event
    * [OR](./constraints/simple.md#or)
        * Basic
        * Merge at correct event
* [Nested](./constraints/nested.md)
    * [AND](./constraints/nested.md#and)
        * AND
        * XOR
        * OR
        * Loop
        * Branch counts
    * [XOR](./constraints/nested.md#xor)
        * AND
        * XOR
        * OR
        * Loop
        * Branch counts
    * [OR](./constraints/nested.md#or)
        * AND
        * XOR
        * OR
        * Loop
        * Branch counts
* [Kill/detach](./constraints/kill_detach.md)
    * [No merge](./constraints/kill_detach.md#no-merge)
    * [With merge](./constraints/kill_detach.md#with-merge)
    * [Merge on parent](./constraints/kill_detach.md#merge-on-parent)
    * [In loops](./constraints/kill_detach.md#in-loops)
* [Bunched](./constraints/bunched.md)
    * [Bunched with AND as highest level](./constraints/bunched.md#and)
        * [Bunched with AND as next level](./constraints/bunched.md#and-and)
            * With event in between merge and branch
            * Without event in between merge and branch
        * [Bunched with XOR as next level](./constraints/bunched.md#and-xor)
            * With event in between merge and branch
            * Without event in between merge and branch
        * [Bunched with OR as next level](./constraints/bunched.md#and-or)
            * With event in between merge and branch
            * Without event in between merge and branch
    * [Bunched with XOR as highest level](./constraints/bunched.md#xor)
        * [Bunched with AND as next level](./constraints/bunched.md#xor-and)
            * With event in between merge and branch
            * Without event in between merge and branch
        * [Bunched with XOR as next level](./constraints/bunched.md#xor-xor)
            * With event in between merge and branch
            * Without event in between merge and branch
        * [Bunched with OR as next level](./constraints/bunched.md#xor-or)
            * With event in between merge and branch
            * Without event in between merge and branch
    * [Bunched with OR as highest level](./constraints/bunched.md#or)
        * [Bunched with AND as next level](./constraints/bunched.md#or-and)
            * With event in between merge and branch
            * Without event in between merge and branch
        * [Bunched with XOR as next level](./constraints/bunched.md#or-xor)
            * With event in between merge and branch
            * Without event in between merge and branch
        * [Bunched with OR as next level](./constraints/bunched.md#or-or)
            * With event in between merge and branch
            * Without event in between merge and branch
    * [Three levels of bunching of same logic type](./constraints/bunched.md#three-levels-of-bunching-of-same-logic-type)
        * [AND](./constraints/bunched.md#three-and)
        * [XOR](./constraints/bunched.md#three-xor)