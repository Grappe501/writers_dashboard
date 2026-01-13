import { useEffect, useMemo, useState } from "react";
import { loadNotes, saveNotes, type NotesByNodeId } from "./notesStore";

export function useNotes(projectId: string) {
  const [notes, setNotes] = useState<NotesByNodeId>(() => loadNotes(projectId));

  // persist on change
  useEffect(() => {
    saveNotes(projectId, notes);
  }, [projectId, notes]);

  const api = useMemo(() => {
    return {
      notes,
      get(nodeId: string | null) {
        if (!nodeId) return "";
        return notes[nodeId] ?? "";
      },
      set(nodeId: string | null, value: string) {
        if (!nodeId) return;
        setNotes((prev) => ({ ...prev, [nodeId]: value }));
      },
      clear(nodeId: string | null) {
        if (!nodeId) return;
        setNotes((prev) => {
          const next = { ...prev };
          delete next[nodeId];
          return next;
        });
      },
    };
  }, [notes]);

  return api;
}
