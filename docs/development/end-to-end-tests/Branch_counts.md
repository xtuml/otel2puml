# End-to-end tests branch counts
End to end test cases for cases involving branch counts.
## Contents
* [Simple single branch count](./Branch_counts.md#simple-single-branch-count)
* [Double branch count](./Branch_counts.md#double-branch-count)

## Cases
### Simple single branch count
Tests a simple branch count as below

![](/end-to-end-pumls/branch_counts/simple_branch_count.svg)
### Double branch count
Tests a double branch count

![](/end-to-end-pumls/branch_counts/double_branch_count.svg)

### Branch counts bunched with operators
Tests a branch count with OR and AND operators directly following the branch count

#### OR operator

The following diagram shows a branch count with an OR operator directly following it

![](/end-to-end-pumls/branch_counts/branch_with_bunched_OR.svg)

however due to ambiguity in the diagram the reverse engineered diagram is as follows

![](/end-to-end-pumls/branch_counts/branch_with_bunched_OR_equiv.svg)

#### AND operator
The AND operator should be preserved as is in the diagram
![](/end-to-end-pumls/branch_counts/branch_with_bunched_AND.svg)