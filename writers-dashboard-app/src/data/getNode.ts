type PlanNode = {
    id: string;
    title: string;
    kind: string;
    href?: string;
  };
  
  type Manifest = {
    nodes: PlanNode[];
  };
  
  export function getNodeById(manifest: Manifest, id: string | null) {
    if (!id) return null;
    return manifest.nodes.find((n) => n.id === id) ?? null;
  }
  