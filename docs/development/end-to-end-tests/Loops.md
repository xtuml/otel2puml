# End-to-end tests loops
End to end test cases for cases involving loops.
## Contents
* [Self Loops](/docs/development/end-to-end-tests/Loops.md#self-loops)
* [Nested Loops](/docs/development/end-to-end-tests/Loops.md#nested-loops)
  * Nested Normal Loops
  * Nested Self Loops
* [Nested Logic Blocks](/docs/development/end-to-end-tests/Loops.md#nested-logic-blocks)
  * Nested AND logic
  * Nested OR logic
  * Nested XOR logic
  * Nested bunched logic
* [Break Points](/docs/development/end-to-end-tests/Loops.md#break-points)
  * Normal break in loop
  * Two breaks in loop
  * Break point in nested loop
* [Nested Branch Counts](/docs/development/end-to-end-tests/Loops.md#nested-branch-counts)
* [Edge Cases](/docs/development/end-to-end-tests/Loops.md#edge-cases)
  * Loop with break with logic directly after loop
  * Paths should kill in loop

## Cases
### Self Loops
Tests a self loop as below

![](/end-to-end-pumls/loops/self_loop.svg)
### Nested Loops
Tests for nested loops
#### Nested Normal Loop
Tests a nested normal loop as below

![](/end-to-end-pumls/loops/nested_loops/nested_normal_loops.svg)
#### Nested Self Loop
Tests a nested self loop

![](/end-to-end-pumls/loops/nested_loops/nested_self_loop.svg)
### Nested Logic Blocks
Tests logic blocks nested within loops
#### Nested AND Block
Tests an AND logic block nested within a loop

![](/end-to-end-pumls/loops/nested_logic_blocks/loop_nested_AND.svg)
#### Nested OR Block
Tests an OR logic block nested within a loop

![](/end-to-end-pumls/loops/nested_logic_blocks/loop_nested_OR.svg)
#### Nested XOR Block
Tests an XOR logic block nested within a loop

![](/end-to-end-pumls/loops/nested_logic_blocks/loop_nested_XOR.svg)
#### Nested Bunched Logic Block
Tests a logic blcok that starts and ends a loop to test logic starts/ends bunched against the beginning/end of a loop block

![](/end-to-end-pumls/loops/nested_logic_blocks/loop_nested_logic_bunched.svg)
### Break Points
Tests cases where loops have break points.
#### Normal Break In Loop
Tests a simple break point case in a loop

![](/end-to-end-pumls/loops/break_points/loop_break_point.svg)
#### Two Break Points In Loop
Tests a case where two break points exist in a loop

![](/end-to-end-pumls/loops/break_points/loop_with_2_breaks.svg)
#### Break Point In Nested Loop
Tests a case where a break point is within a nested loop[]

![](/end-to-end-pumls/loops/break_points/loop_nested_break_point.svg)
### Nested Branch Counts
Tests a case where a branch count is nested in a loop, starts the loop and then its children loop back to it again

![](/end-to-end-pumls/loops/nested_branch_counts/loop_nested_branch_counts.svg)
### Edge Cases
Tests any further edge cases that are considered to be less common
#### Loop with break with logic directly after loop 
Tests a case in which there is a loop with a break in it with the start of a logic block directly after the end of the loop so that the loop exits to more than one event.

![](/end-to-end-pumls/loops/edge_cases/loop_break_split_exit.svg)

#### Paths should kill in loop
Tests a case where paths in a logic block should be kill paths in a loop due to starting after the loop ends.

![](/end-to-end-pumls/loops/edge_cases/paths_should_kill_in_loop.svg)