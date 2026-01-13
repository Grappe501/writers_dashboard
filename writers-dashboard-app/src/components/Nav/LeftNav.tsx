import styles from "./LeftNav.module.css";

type PlanNode = {
  id: string;
  title: string;
  children?: string[];
};

type Manifest = {
  rootNodeId: string;
  nodes: PlanNode[];
};

type Props = {
  manifest: Manifest;
  onSelectNode: (id: string) => void;
};

export function LeftNav({ manifest, onSelectNode }: Props) {
  const nodeMap = new Map(manifest.nodes.map((n) => [n.id, n]));

  const handleSelect = (id: string) => {
    console.log("[LeftNav] select:", id);
    onSelectNode(id);
  };

  const renderNode = (id: string, depth = 0) => {
    const node = nodeMap.get(id);
    if (!node) return null;

    return (
      <div key={id} className={styles.node} style={{ paddingLeft: depth * 12 }}>
        <button
          type="button"
          className={styles.nodeButton}
          onClick={() => handleSelect(node.id)}
        >
          <div className={styles.nodeTitle}>{node.title}</div>
          <div className={styles.nodeId}>{node.id}</div>
        </button>

        {node.children?.map((childId) => renderNode(childId, depth + 1))}
      </div>
    );
  };

  return <nav className={styles.leftNav}>{renderNode(manifest.rootNodeId)}</nav>;
}
