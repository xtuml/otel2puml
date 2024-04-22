# End-to-End Tests

## Introduction
This document details an overview of the plan for the creation of End-to-End test PUML's that will cover a large variety of test cases that covers a good percentage of the functionality and possible cases that could be seen in real data. An overview of the categories and whatis being tested in those categories will be included in this document which will then be used to create the actual PUML's for testing.

## PUML test categories
The End to end tests will be categorised into the following
* loops
    * self loops
    * nested loops
    * nested logic blocks within loops
    * nested branch counts
    * break points
        * simple
        * nested
    * edge cases
* constraints
    * simple
        * AND
            * normal
            * multiple same events (plus edge cases)
        * XOR
        * OR
    * nested
        * AND
            * AND
            * XOR
            * OR
        * XOR
            * AND
            * XOR
            * OR
        * OR
            * AND
            * XOR
            * OR
        * loop
        * branch counts
    * bunched
        * AND
            * AND
            * XOR
            * OR
        * XOR
            * AND
            * XOR
            * OR
        * AND
            * AND
            * XOR
            * OR
        * Extremely nested
    * kill/detach cases
        * simple
        * no merge events
    * edge cases
* branch counts
    * simple
    * doubled up
    * edge cases



