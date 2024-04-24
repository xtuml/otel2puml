# Bunched
Tests for bunched constraints - that is the case where a the start of a constraint block is immediately proceeded by the start of another constraint block.

## AND
Tests for bunched constraint cases with AND as the first constraint block
### AND-AND
Test for a bunched AND constraint with another AND constraint
#### Event in between merge and branch
Test for a bunched AND constraint with another AND constraint where an event occurs between the merge and the branch

![](/end-to-end-pumls/constraints/bunched/AND/bunched_ANDFork_ANDFork.svg)
#### No event in between merge and branch
Test for a bunched AND constraint with another AND constraint where no event occurs between the merge and the 

![](/end-to-end-pumls/constraints/bunched/AND/bunched_merge_ANDFork_ANDFork.svg)
### AND-XOR
Test for a bunched AND constraint with another XOR constraint
#### Event in between merge and branch
Test for a bunched AND constraint with another XOR constraint where an event occurs between the merge and the branch

![](/end-to-end-pumls/constraints/bunched/AND/bunched_ANDFork_XORFork.svg)
#### No event in between merge and branch
Test for a bunched AND constraint with another XOR constraint where no event occurs between the merge and the branch

![](/end-to-end-pumls/constraints/bunched/AND/bunched_merge_ANDFork_XORFork.svg)
### AND-OR
Test for a bunched AND constraint with another OR constraint
#### Event in between merge and branch
Test for a bunched AND constraint with another OR constraint where an event occurs between the merge and the branch

![](/end-to-end-pumls/constraints/bunched/AND/bunched_ANDFork_ORFork.svg)
#### No event in between merge and branch
Test for a bunched AND constraint with another OR constraint where no event occurs between the merge and the branch

![](/end-to-end-pumls/constraints/bunched/AND/bunched_merge_ANDFork_ORFork.svg)

## XOR
Tests for bunched constraint cases with XOR as the first constraint block
### XOR-AND
Test for a bunched XOR constraint with another AND constraint
#### Event in between merge and branch
Test for a bunched XOR constraint with another AND constraint where an event occurs between the merge and the branch

![](/end-to-end-pumls/constraints/bunched/XOR/bunched_XORFork_ANDFork.svg)
#### No event in between merge and branch
Test for a bunched XOR constraint with another AND constraint where no event occurs between the merge and the branch

![](/end-to-end-pumls/constraints/bunched/XOR/bunched_merge_XORFork_ANDFork.svg)
### XOR-XOR
Test for a bunched XOR constraint with another XOR constraint
#### Event in between merge and branch
Test for a bunched XOR constraint with another XOR constraint where an event occurs between the merge and the branch

![](/end-to-end-pumls/constraints/bunched/XOR/bunched_XORFork_XORFork.svg)
#### No event in between merge and branch
Test for a bunched XOR constraint with another XOR constraint where no event occurs between the merge and the branch

![](/end-to-end-pumls/constraints/bunched/XOR/bunched_merge_XORFork_XORFork.svg)
### XOR-OR
Test for a bunched XOR constraint with another OR constraint
#### Event in between merge and branch
Test for a bunched XOR constraint with another OR constraint where an event occurs between the merge and the branch

![](/end-to-end-pumls/constraints/bunched/XOR/bunched_XORFork_ORFork.svg)
#### No event in between merge and branch
Test for a bunched XOR constraint with another OR constraint where no event occurs between the merge and the branch

![](/end-to-end-pumls/constraints/bunched/XOR/bunched_merge_XORFork_ORFork.svg)

## OR
Tests for bunched constraint cases with OR as the first constraint block
### OR-AND
Test for a bunched OR constraint with another AND constraint
#### Event in between merge and branch
Test for a bunched OR constraint with another AND constraint where an event occurs between the merge and the branch

![](/end-to-end-pumls/constraints/bunched/OR/bunched_ORFork_ANDFork.svg)
#### No event in between merge and branch
Test for a bunched OR constraint with another AND constraint where no event occurs between the merge and the branch

![](/end-to-end-pumls/constraints/bunched/OR/bunched_merge_ORFork_ANDFork.svg)
### OR-XOR
Test for a bunched OR constraint with another XOR constraint
#### Event in between merge and branch
Test for a bunched OR constraint with another XOR constraint where an event occurs between the merge and the branch

![](/end-to-end-pumls/constraints/bunched/OR/bunched_ORFork_XORFork.svg)
#### No event in between merge and branch
Test for a bunched OR constraint with another XOR constraint where no event occurs between the merge and the branch

![](/end-to-end-pumls/constraints/bunched/OR/bunched_merge_ORFork_XORFork.svg)
### OR-OR
Test for a bunched OR constraint with another OR constraint
#### Event in between merge and branch
Test for a bunched OR constraint with another OR constraint where an event occurs between the merge and the branch

![](/end-to-end-pumls/constraints/bunched/OR/bunched_ORFork_ORFork.svg)
#### No event in between merge and branch
Test for a bunched OR constraint with another OR constraint where no event occurs between the merge and the branch

![](/end-to-end-pumls/constraints/bunched/OR/bunched_merge_ORFork_ORFork.svg)
## Three levels of bunching of same logic type
Tests for bunched constraint cases with three levels of the same logic type
### Three-AND
Test for a bunched constraint with three levels of AND constraints

![](/end-to-end-pumls/constraints/bunched/bunched_3_levels_same_AND.svg)
### Three-XOR
Test for a bunched constraint with three levels of XOR constraints

![](/end-to-end-pumls/constraints/bunched/bunched_3_levels_same_XOR.svg)