import { useMemo, useState } from "react";
import "./App.css";
import { Shell } from "./components/Layout/Shell";
import { LeftNav, type NavNode } from "./components/Nav/LeftNav";
import { CenterPane } from "./components/Center/CenterPane";
import { RightInspector, type ValidationIssue } from "./components/Inspector/RightInspector";

function App() {
  // Minimal “project nav” placeholder (we’ll load fixtures in M1.8)
  const nodes: NavNode[] = useMemo(
    () => [
      {
        id: "plan-hub",
        title: "Build Plan Hub",
        href: "../Build_plan/index.html",
      },
      {
        id: "master-reader",
        title: "Master Build Plan (Consolidated)",
        href: "../Build_plan/MASTER_BUILD_PLAN_CONSOLIDATED.html",
      },
      {
        id: "m0-overview",
        title: "M0 Overview",
        href: "../Build_plan/m0/overview.html",
      },
      {
        id: "m1-overview",
        title: "M1 Overview",
        href: "../Build_plan/m1/overview.html",
      },
    ],
    []
  );

  const [selectedNodeId, setSelectedNodeId] = useState<string>(nodes[0]?.id ?? "");
  const selectedNode = useMemo(
    () => nodes.find((n) => n.id === selectedNodeId) ?? null,
    [nodes, selectedNodeId]
  );

  // Minimal validation placeholder (we’ll compute real issues later)
  const issues: ValidationIssue[] = useMemo(() => {
    const out: ValidationIssue[] = [];
    if (!selectedNode) return out;
    if (!selectedNode.href) {
      out.push({
        id: "missing-href",
        severity: "error",
        message: "Selected node has no href.",
        nodeId: selectedNode.id,
      });
    }
    return out;
  }, [selectedNode]);

  return (
    <Shell
      left={
        <LeftNav
          nodes={nodes}
          selectedId={selectedNodeId}
          onSelect={setSelectedNodeId}
        />
      }
      center={<CenterPane node={selectedNode} />}
      right={
        <RightInspector
          selectedNode={selectedNode}
          issues={issues}
          onSelectNode={(nodeId) => setSelectedNodeId(nodeId)}
        />
      }
    />
  );
}

export default App;
