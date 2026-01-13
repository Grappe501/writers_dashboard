# EXEC CHECKLIST — M1.6/1.7 COMBINED (Fixtures + Notes)

## Goal
Deliver Notes + Fixtures in one pass, touching core UI files once.

## Pass Criteria
- App boots with no white screen
- Selecting a node updates Center + Inspector
- Notes textarea appears for selected node
- Notes auto-save to localStorage and persist on refresh
- Validation still runs and Inspector shows totals
- Fixture files exist at:
  - fixtures/manifests/pilot.manifest.json
  - fixtures/expected/pilot.validation.expected.json

## Manual Checks
1. Start dev server:
   - cd writers-dashboard-app
   - npm run dev
2. Click a node in left nav.
3. Type in Notes box.
4. Refresh page — note persists.
5. Confirm Inspector totals still render.

## Deferred (Do Not Run Yet)
- Automated tests
- CI gating
- Snapshot assertions
