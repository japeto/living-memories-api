# chore: add pre-commit and commit-msg hooks

## Summary
Add trackable git hooks via the `pre-commit` framework so all developers share
identical lint, format, and commit-message validation automatically on every commit.

## Scope
Hook configuration, custom validator scripts, skill updates, and README setup step.
No business logic changes.

## Git Strategy
- Work branch: `chore/add-git-hooks` (from develop)
- Target: `develop`

## Files to Create / Modify

| File | Action | Description |
|------|--------|-------------|
| `.pre-commit-config.yaml` | Create | Framework config: ruff, debug check, env guard, commit-msg validator |
| `.githooks/validate_commit_msg.py` | Create | Validates Conventional Commits format + Co-authored-by trailers |
| `.githooks/check_debug_statements.py` | Create | Rejects print/breakpoint/pdb in app/ |
| `requirements-dev.txt` | Modify | Add `pre-commit` |
| `README.md` | Modify | Add `pre-commit install` to Getting Started |
| `.claude/skills/lm-git/SKILL.md` | Modify | D2: install command. D3: never --no-verify |
| `.claude/skills/lm-developer/SKILL.md` | Modify | D3: hooks must pass before handoff |
| `.claude/skills/lm-architect/SKILL.md` | Modify | Acceptance criteria template: add hooks item |

## Acceptance Criteria
- [ ] `pre-commit run --all-files` → zero violations
- [ ] Commit with invalid message format is rejected by commit-msg hook
- [ ] Commit with missing Co-authored-by trailer is rejected
- [ ] Commit with `print("x")` in `app/` is rejected by pre-commit hook
- [ ] Commit attempting to add `.env` file is rejected
- [ ] Valid commit (correct message + trailers + clean code) passes all hooks
- [ ] `pre-commit install --hook-type pre-commit --hook-type commit-msg` installs cleanly
