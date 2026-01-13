export type NotesByNodeId = Record<string, string>;

function key(projectId: string) {
  return `writers_dashboard.notes.${projectId}`;
}

export function loadNotes(projectId: string): NotesByNodeId {
  try {
    const raw = localStorage.getItem(key(projectId));
    if (!raw) return {};
    const parsed = JSON.parse(raw);
    if (!parsed || typeof parsed !== "object") return {};
    return parsed as NotesByNodeId;
  } catch {
    return {};
  }
}

export function saveNotes(projectId: string, notes: NotesByNodeId) {
  try {
    localStorage.setItem(key(projectId), JSON.stringify(notes));
  } catch {
    // no-op (storage might be blocked)
  }
}
