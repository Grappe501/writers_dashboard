# Executable Checklist — M0 + M1 (Writers Dashboard)

Generated: 2026-01-12T14:44:20

This checklist is the **authoritative execution runbook** for beginning implementation.
Follow in order. **STOP means do not proceed.**

---

## M0 — Repo Constitution & Discipline

- [ ] Verify Python, Git, Node, NPM installed
- [ ] Lock repo folder structure (`Build_plan`, `src`, `tools`, `fixtures`, `spec`, `docs`, `reports`)
- [ ] Add `.gitattributes` to enforce LF
- [ ] Update `.gitignore` to exclude archive/reports noise
- [ ] Create `docs/CHANGELOG_PLAN.md`
- [ ] Create `docs/testing_strategy.md`
- [ ] Create `.github/workflows/ci.yml`

**M0 EXIT GATE:** Repo stable, hygiene enforced, CI stub exists

---

## M1 — Cockpit Foundation

- [ ] Scaffold app (Vite + React + TS recommended)
- [ ] App boots locally (`npm run dev`)
- [ ] 3-panel cockpit layout renders
- [ ] Define contracts in `spec/contracts/`
- [ ] Local autosave via localStorage
- [ ] Validation panel renders stub issues
- [ ] Override workflow logs requests
- [ ] Notes editor persists content
- [ ] Fixture loads and smoke test passes

**M1 EXIT GATE:** App runs, cockpit exists, persistence + validation work

---

GO if all above boxes are checked.
