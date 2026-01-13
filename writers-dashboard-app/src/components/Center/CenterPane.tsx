import styles from "./CenterPane.module.css";

type Props = {
  selectedNodeId: string | null;
  getNote: (nodeId: string | null) => string;
  setNote: (nodeId: string | null, value: string) => void;
  clearNote: (nodeId: string | null) => void;
};

export function CenterPane({ selectedNodeId, getNote, setNote, clearNote }: Props) {
  const hasSelection = typeof selectedNodeId === "string" && selectedNodeId.length > 0;

  const noteValue = getNote(selectedNodeId);

  // For M1.x, we can derive href from the runtime manifest by reading a data attribute we’ll add later,
  // but for now we keep it simple: show a reader panel once selection exists.
  // (Real node lookup will be introduced cleanly in the next step.)
  const hrefGuess = hasSelection ? `/readers/build_plan/${selectedNodeId}.html` : "";

  const canIframe = hasSelection && hrefGuess.startsWith("/readers/");

  return (
    <main className={styles.centerPane}>
      <div className={styles.header}>
        <h2>{hasSelection ? selectedNodeId : "No selection"}</h2>
        <div className={styles.muted}>
          {hasSelection ? "Selected plan node" : "Select a node in the left nav."}
        </div>
      </div>

      {hasSelection ? (
        <div className={styles.card}>
          <div className={styles.cardTitle}>Reader</div>

          <div className={styles.muted}>
            Target: <code>{hrefGuess}</code>
          </div>

          <div style={{ display: "flex", gap: 12, marginTop: 10, alignItems: "center" }}>
            <a href={hrefGuess} target="_blank" rel="noreferrer" className={styles.link}>
              Open reader in new tab
            </a>
            <span className={styles.muted}>·</span>
            <span className={styles.muted}>{canIframe ? "Preview below" : "No preview available"}</span>
          </div>

          {canIframe ? (
            <div style={{ marginTop: 12, border: "1px solid rgba(0,0,0,0.08)", borderRadius: 8, overflow: "hidden" }}>
              <iframe
                title="Reader"
                src={hrefGuess}
                style={{ width: "100%", height: 360, border: "0" }}
              />
            </div>
          ) : null}
        </div>
      ) : null}

      <div className={styles.card}>
        <div className={styles.cardTitle}>Notes</div>

        {!hasSelection ? (
          <div className={styles.empty}>Choose a plan node to view/edit notes.</div>
        ) : (
          <>
            <textarea
              value={noteValue}
              onChange={(e) => setNote(selectedNodeId, e.target.value)}
              placeholder="Write notes for this node… (auto-saves)"
              style={{
                width: "100%",
                minHeight: 220,
                resize: "vertical",
                padding: 10,
                fontSize: 14,
                lineHeight: 1.4
              }}
            />

            <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
              <button onClick={() => clearNote(selectedNodeId)}>Clear</button>
              <div className={styles.muted} style={{ alignSelf: "center" }}>
                Saved locally (per projectId).
              </div>
            </div>
          </>
        )}
      </div>
    </main>
  );
}
