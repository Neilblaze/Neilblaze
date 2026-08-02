---
name: cleanup-code
description: Run linters, automatically fix code issues, and validate fixes through iterative cycles until all checks pass or maximum iterations are reached.
---

Workflow:

1. **Find Linting Commands**: Figure out what commands you should run to lint. It is probably described in the project's CLAUDE.md or README.md.
2. **Initial Assessment**: Run the linters. Note the ones that fail or have warnings.
3. **Iterative Lint-Fix Cycle**: 
    - **Choose linter**: Choose a linter from the list of failed or warning linters.
    - **Fix**: Automatically fix issues.
    - **Validate**: Ensure fixes are valid.
4. **Repeat**: Repeat the process until all checks pass or maximum iterations are reached.
5. **Report Results**: Report which linters are failing, and which one were you fixing. Note if the current linter is fixed or needs further attention.

Maximum iterations: 5.
Never use ignores to fix linting errors. If you cannot fix an issue, report in step 5 instead. 
Assume the current linter configurations are correct.
