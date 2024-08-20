# Simple
Tests cases for most simple constraint cases
## AND
Tests for single AND constraint cases
### Basic
Tests a basic AND constraint

![](/end-to-end-pumls/constraints/simple/AND/simple_AND.svg)
### Multiple same events
Tests multiple of the same event coming from the same source (should provide a branch count)

#### Simple
![](/end-to-end-pumls/constraints/simple/AND/multiple_same_event_AND.svg)

prodcues this result using the tool

![](/end-to-end-pumls/constraints/simple/AND/multiple_same_event_AND_equiv.svg)

#### Extra branch merging in
![](/end-to-end-pumls/constraints/simple/AND/multiple_same_event_AND_with_extra_branch.svg)

produces this result using the tool

![](/end-to-end-pumls/constraints/simple/AND/multiple_same_event_AND_with_extra_branch_equiv.svg)

#### Loop following branch event
![](/end-to-end-pumls/constraints/simple/AND/multiple_same_event_AND_with_self_loop.svg)

produces this result using the tool

![](/end-to-end-pumls/constraints/simple/AND/multiple_same_event_AND_with_self_loop_equiv.svg)

### Merge at correct event
Tests that the merge event is the correct event

#### Simple
![](/end-to-end-pumls/constraints/simple/AND/merge_at_correct_event_AND.svg)

#### Kill branch included
![](/end-to-end-pumls/constraints/simple/AND/merge_at_correct_event_AND_with_kill.svg)

## XOR
Tests for single XOR constraint cases
### Basic
Tests a basic XOR constraint

![](/end-to-end-pumls/constraints/simple/XOR/simple_XOR.svg)

### Merge at correct event
Tests that the merge event is the correct event

![](/end-to-end-pumls/constraints/simple/XOR/merge_at_correct_event_XOR.svg)

### Merge from similar paths
Tests that two paths are able to merge even if they some of the path is shared by the other path

![](/end-to-end-pumls/constraints/simple/XOR/merge_from_similar_paths_XOR.svg)

## OR
Tests for single OR constraint cases
### Basic
Tests a basic OR constraint

![](/end-to-end-pumls/constraints/simple/OR/simple_OR.svg)

### Merge at correct event
Tests that the merge event is the correct event

![](/end-to-end-pumls/constraints/simple/OR/merge_at_correct_event_OR.svg)