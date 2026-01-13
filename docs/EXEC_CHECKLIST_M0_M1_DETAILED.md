# EXECUTABLE CHECKLIST — M0 + M1 (DETAILED)

Generated: 2026-01-13T07:48:50

This document is the authoritative execution runbook.
Follow steps in order. STOP if any Definition of Done fails.

---

## M0 — Repo Discipline (Support Phase)

- Verify repo structure
- Enforce git hygiene (.gitignore, .gitattributes)
- Lock CI expectations

**DoD:** Repo is stable and reproducible.

---

## M1 — Cockpit Foundation

### M1.1 App Location Check
- writers-dashboard-app/package.json exists
- No nested writers-dashboard-app/writers-dashboard-app/

**STOP-THE-LINE:** Fix structure if nested.

### M1.2 Run App
cd writers-dashboard-app
npm install
npm run dev

**DoD:** Vite dev server runs and page loads.

### M1.3 Cockpit Layout
- Left nav
- Center editor
- Right inspector

**DoD:** Three panels render consistently.

### M1.4 Contracts
- spec/contracts/ProjectManifest.json
- spec/contracts/PlanNode.json
- spec/contracts/ValidationIssue.json
- spec/contracts/OverrideRequest.json

**DoD:** Schemas exist and are committed.

### M1.5 Persistence
- localStorage for node selection
- localStorage for notes
- localStorage for overrides

**DoD:** Refresh restores state.

### M1.6 Validation UI (Stub)
- Mock issues rendered
- Clicking issue focuses node

**DoD:** Interaction works.

### M1.7 Notes Editor
- Textarea per node
- Auto-save enabled

**DoD:** Notes persist after refresh.

### M1.8 Fixtures + Smoke Test
- fixtures/toy_project/manifest.json
- fixtures/toy_project/nodes.json
- npm test passes

**DoD:** Smoke test green.

---

EXIT M1 ONLY WHEN ALL ABOVE CONDITIONS ARE MET.
