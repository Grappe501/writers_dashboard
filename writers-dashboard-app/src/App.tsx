import { useMemo, useState } from "react";
import "./App.css";
import { Shell } from "./components/Layout/Shell";
import { LeftNav } from "./components/Nav/LeftNav";
import { CenterPane } from "./components/Center/CenterPane";
import { RightInspector } from "./components/Inspector/RightInspector";
import manifest from "./data/project.manifest.json";
import { validateManifest } from "./validation/validateManifest";
import { useNotes } from "./notes/useNotes";

console.log("COCKPIT_APP_TSX_ACTIVE");

export default function App() {
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);

  const issues = useMemo(() => {
    return validateManifest(manifest as any);
  }, []);

  const projectId = (manifest as any)?.projectId || "writers-dashboard-pilot";
  const notesApi = useNotes(projectId);

  return (
    <Shell
      left={<LeftNav manifest={manifest as any} onSelectNode={setSelectedNodeId} />}
      center={
        <CenterPane
          selectedNodeId={selectedNodeId}
          getNote={notesApi.get}
          setNote={notesApi.set}
          clearNote={notesApi.clear}
        />
      }
      right={<RightInspector selectedNodeId={selectedNodeId} issues={issues} />}
    />
  );
}
