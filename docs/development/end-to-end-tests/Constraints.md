# End-to-end tests Constraints
End to end test cases for cases involving constraints.
## Contents
* [Simple](./constraints/simple)
    * [AND](./constraints/simple#and)
        * Basic
        * Multiple same events
        * Merge at correct event
    * [XOR](./constraints/simple#xor)
        * Basic
        * Merge at correct event
    * [OR](./constraints/simple#or)
        * Basic
        * Merge at correct event
* [Nested](./constraints/nested)
    * [AND](./constraints/nested#and)
        * AND
        * XOR
        * OR
        * Loop
        * Branch counts
    * [XOR](./constraints/nested#xor)
        * AND
        * XOR
        * OR
        * Loop
        * Branch counts
    * [OR](./constraints/nested#or)
        * AND
        * XOR
        * OR
        * Loop
        * Branch counts
* [Kill/detach](./constraints/kill_detach)
    * [No merge](./constraints/kill_detach#no-merge)
    * [With merge](./constraints/kill_detach#with-merge)
    * [Merge on parent](./constraints/kill_detach#merge-on-parent)
    * [In loops](./constraints/kill_detach#in-loops)
* [Bunched](./constraints/bunched)
    * [Bunched with AND as highest level](./constraints/bunched#and)
        * [Bunched with AND as next level](./constraints/bunched#and-and)
            * With event in between merge and branch
            * Without event in between merge and branch
        * [Bunched with XOR as next level](./constraints/bunched#and-xor)
            * With event in between merge and branch
            * Without event in between merge and branch
        * [Bunched with OR as next level](./constraints/bunched#and-or)
            * With event in between merge and branch
            * Without event in between merge and branch
    * [Bunched with XOR as highest level](./constraints/bunched#xor)
        * [Bunched with AND as next level](./constraints/bunched#xor-and)
            * With event in between merge and branch
            * Without event in between merge and branch
        * [Bunched with XOR as next level](./constraints/bunched#xor-xor)
            * With event in between merge and branch
            * Without event in between merge and branch
        * [Bunched with OR as next level](./constraints/bunched#xor-or)
            * With event in between merge and branch
            * Without event in between merge and branch
    * [Bunched with OR as highest level](./constraints/bunched#or)
        * [Bunched with AND as next level](./constraints/bunched#or-and)
            * With event in between merge and branch
            * Without event in between merge and branch
        * [Bunched with XOR as next level](./constraints/bunched#or-xor)
            * With event in between merge and branch
            * Without event in between merge and branch
        * [Bunched with OR as next level](./constraints/bunched#or-or)
            * With event in between merge and branch
            * Without event in between merge and branch
    * [Three levels of bunching of same logic type](./constraints/bunched#three-levels-of-bunching-of-same-logic-type)
        * [AND](./constraints/bunched#three-and)
        * [XOR](./constraints/bunched#three-xor)