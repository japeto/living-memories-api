# config: Create GitHub PR Templates

## Summary
Add GitHub Pull Request templates for standard tasks (features/bugfixes/chores) and deployments/releases to standardize the code review and release process.

## Scope
- Create multiple PR templates using the `.github/PULL_REQUEST_TEMPLATE/` directory.
- Create a template for standard tasks (feature, fix, chore).
- Create a template for release/deployment PRs.
- Out of scope: Issue templates, CI/CD pipeline changes.

## Files to Create / Modify
| File | Action | Description |
|------|--------|-------------|
| `.github/PULL_REQUEST_TEMPLATE/task.md` | Create | PR template for features, bugfixes, and chores. Contains sections for Description, Type of change, and Checklist. |
| `.github/PULL_REQUEST_TEMPLATE/release.md` | Create | PR template for deployments and releases. Contains sections for Release Notes, Version, Deployment Steps, and Rollback Plan. |

## Business Logic / Change Description
1. **Directory Creation**: Create a `.github/PULL_REQUEST_TEMPLATE` directory in the repository root to support multiple PR templates.
2. **Task PR Template (`task.md`)**:
   - Add sections for:
     - **Description:** What does this PR do?
     - **Related Issue(s):** E.g., `Closes #XXX`
     - **Type of Change:** Checkboxes for feat, fix, docs, chore, etc.
     - **Checklist:** Standard checks (linting passed, tests added/passed, no circular imports, etc., reflecting our strict `pre-commit` and FastAPI context standards).
3. **Release PR Template (`release.md`)**:
   - Add sections for:
     - **Release Version:** Target version for this deployment.
     - **Changelog / Release Notes:** High-level summary of what's included.
     - **Deployment Checklist:** E.g., Environment variables needed, DB migrations required.
     - **Rollback Plan:** Steps to take if the deployment fails.

## Acceptance Criteria
- [ ] `.github/PULL_REQUEST_TEMPLATE/task.md` exists and contains standard development checklists.
- [ ] `.github/PULL_REQUEST_TEMPLATE/release.md` exists and contains deployment/release specific sections.
- [ ] Markdown formatting is correct and renders properly on GitHub.

## Open Questions / Risk Alerts
- Does the project use specific issue trackers (e.g., Jira, Linear) whose ticket formatting should be included in the PR template?
- Are there specific deployment environments (Staging, Prod) that should have separate checklists in the release template?
