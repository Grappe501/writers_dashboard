import styles from "./RightInspector.module.css";

type Severity = "info" | "warn" | "error";

type ValidationIssue = {
  id: string;
  severity: Severity;
  message: string;
  nodeId?: string;
  ruleId?: string;
};

type Props = {
  selectedNodeId: string | null;
  issues: ValidationIssue[];
};

export function RightInspector({ selectedNodeId, issues }: Props) {
  const hasSelection = typeof selectedNodeId === "string" && selectedNodeId.length > 0;

  const totals = {
    info: issues.filter((i) => i.severity === "info").length,
    warn: issues.filter((i) => i.severity === "warn").length,
    error: issues.filter((i) => i.severity === "error").length,
  };

  const scopedIssues = hasSelection
    ? issues.filter((i) => i.nodeId === selectedNodeId)
    : issues;

  const stopTheLine = totals.error > 0;

  return (
    <aside className={styles.rightInspector}>
      <div className={styles.header}>
        <h3>Inspector</h3>
        <div className={styles.subheader}>Selection + Validation</div>
      </div>

      <div className={styles.card}>
        <div className={styles.cardTitle}>Selected</div>
        {hasSelection ? (
          <div className={styles.selected}>
            <div className={styles.selectedTitle}>{selectedNodeId}</div>
            <div className={styles.muted}>id</div>
          </div>
        ) : (
          <div className={styles.empty}>No node selected.</div>
        )}
      </div>

      <div className={styles.card}>
        <div className={styles.cardTitle}>Validation</div>

        <div className={styles.muted}>
          Totals — info: {totals.info} · warn: {totals.warn} · error: {totals.error}
        </div>

        {stopTheLine ? (
          <div className={styles.muted} style={{ marginTop: 8 }}>
            STOP-THE-LINE: errors present.
          </div>
        ) : (
          <div className={styles.muted} style={{ marginTop: 8 }}>
            No stop-the-line errors detected.
          </div>
        )}

        <div className={styles.muted} style={{ marginTop: 8 }}>
          Showing: {hasSelection ? "issues for selected node" : "all issues"}
        </div>

        {scopedIssues.length === 0 ? (
          <div className={styles.muted} style={{ marginTop: 8 }}>
            No issues.
          </div>
        ) : (
          <ul style={{ marginTop: 8, paddingLeft: 18 }}>
            {scopedIssues.slice(0, 12).map((i, idx) => (
              <li key={`${i.id}-${idx}`}>
                <strong>{i.severity.toUpperCase()}</strong>: {i.message}
              </li>
            ))}
          </ul>
        )}

        {scopedIssues.length > 12 ? (
          <div className={styles.muted}>…and {scopedIssues.length - 12} more</div>
        ) : null}
      </div>

      <div className={styles.card}>
        <div className={styles.cardTitle}>Next</div>
        <div className={styles.muted}>
          M1.5 wiring complete → next is M1.6 fixtures / M1.7 notes (per roadmap)
        </div>
      </div>
    </aside>
  );
}
