## 15. Error Handling Contract

Current repo behavior is fail-closed by doctrine.
The implemented contract layer treats missing truth, collapsed states,
and invalid boundary assumptions as hard failures, not recoverable guesses.

### 15.1 Current Fail-Closed Conditions

| Condition | Current contract posture |
| --- | --- |
| Ambiguous system role | Reject broadening repo authority |
| Missing challenge or verification for reviewability | `not_reviewable` |
| Proposal/operator state collapse | Forbidden by separate enums |
| Missing documentation build inputs | Build and context scripts exit non-zero |
| Unknown preset or section in context bundle | Script exits non-zero |

### 15.2 Current Error Surface

| Surface | Current handling |
| --- | --- |
| Python contract violations | Test-detected invariant failure |
| Bash documentation scripts | Non-zero exit with stderr message |
| Runtime API errors | Not applicable because no API exists |
