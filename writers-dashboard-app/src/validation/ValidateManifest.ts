export type Severity = "info" | "warn" | "error";

export type ValidationIssue = {
  id: string;
  severity: Severity;
  message: string;
  nodeId?: string;
  path?: string;
  ruleId?: string;
  source: "schema" | "link-check" | "business-rule" | "runtime";
};

export type PlanNode = {
  id: string;
  title: string;
  kind: "hub" | "module" | "day" | "doc" | "folder" | "link" | string;
  href?: string;
  children?: string[];
  parentId?: string;
};

export type Manifest = {
  rootNodeId: string;
  nodes: PlanNode[];
  validationProfile?: {
    requireHrefForKinds?: Array<"link" | "doc" | "hub" | "module" | "day">;
    stopTheLineOn?: Array<"warn" | "error">;
  };
};

const DEFAULT_REQUIRE_HREF_FOR: Array<"link" | "doc" | "hub" | "module" | "day"> = [
  "link",
  "doc",
  "hub",
  "module",
  "day",
];

function issue(
  id: string,
  severity: Severity,
  message: string,
  extra?: Partial<ValidationIssue>
): ValidationIssue {
  return {
    id,
    severity,
    message,
    source: "business-rule",
    ...extra,
  };
}

export function validateManifest(manifest: Manifest): ValidationIssue[] {
  const issues: ValidationIssue[] = [];

  // Basic shape
  if (!manifest || typeof manifest !== "object") {
    return [issue("manifest-missing", "error", "Manifest is missing or invalid.")];
  }

  if (!manifest.rootNodeId || typeof manifest.rootNodeId !== "string") {
    issues.push(issue("rootNodeId-missing", "error", "rootNodeId is missing or invalid.", { path: "/rootNodeId" }));
  }

  if (!Array.isArray(manifest.nodes)) {
    issues.push(issue("nodes-missing", "error", "nodes must be an array.", { path: "/nodes" }));
    return issues;
  }

  const nodes = manifest.nodes;
  const nodeMap = new Map<string, PlanNode>();
  const idCounts = new Map<string, number>();

  // Build nodeMap + detect duplicates
  for (let i = 0; i < nodes.length; i++) {
    const n = nodes[i];

    if (!n || typeof n !== "object") {
      issues.push(issue("node-invalid", "error", `Node at index ${i} is invalid.`, { path: `/nodes/${i}` }));
      continue;
    }

    if (!n.id || typeof n.id !== "string") {
      issues.push(issue("node-id-missing", "error", `Node at index ${i} is missing id.`, { path: `/nodes/${i}/id` }));
      continue;
    }

    idCounts.set(n.id, (idCounts.get(n.id) ?? 0) + 1);
    if (!nodeMap.has(n.id)) nodeMap.set(n.id, n);

    if (!n.title || typeof n.title !== "string") {
      issues.push(
        issue("node-title-missing", "warn", `Node '${n.id}' is missing title.`, {
          nodeId: n.id,
          path: `/nodes/${i}/title`,
        })
      );
    }

    if (!n.kind || typeof n.kind !== "string") {
      issues.push(
        issue("node-kind-missing", "warn", `Node '${n.id}' is missing kind.`, {
          nodeId: n.id,
          path: `/nodes/${i}/kind`,
        })
      );
    }
  }

  for (const [id, count] of idCounts.entries()) {
    if (count > 1) {
      issues.push(
        issue("node-id-duplicate", "error", `Duplicate node id detected: '${id}' appears ${count} times.`, {
          nodeId: id,
          ruleId: "unique-node-ids",
        })
      );
    }
  }

  // rootNodeId exists
  if (manifest.rootNodeId && !nodeMap.has(manifest.rootNodeId)) {
    issues.push(
      issue("rootNodeId-not-found", "error", `rootNodeId '${manifest.rootNodeId}' does not exist in nodes.`, {
        path: "/rootNodeId",
        ruleId: "root-node-exists",
      })
    );
  }

  // children refs exist + parent consistency hint
  for (const n of nodeMap.values()) {
    const children = Array.isArray(n.children) ? n.children : [];
    for (let idx = 0; idx < children.length; idx++) {
      const childId = children[idx];
      if (!nodeMap.has(childId)) {
        issues.push(
          issue("child-missing", "error", `Node '${n.id}' references missing child '${childId}'.`, {
            nodeId: n.id,
            path: `/nodes/${n.id}/children/${idx}`,
            ruleId: "children-must-exist",
          })
        );
        continue;
      }

      const child = nodeMap.get(childId)!;
      if (child.parentId && child.parentId !== n.id) {
        issues.push(
          issue(
            "parentId-mismatch",
            "warn",
            `Child '${childId}' lists parentId='${child.parentId}' but is under '${n.id}'.`,
            { nodeId: childId, ruleId: "parentId-consistency" }
          )
        );
      }
    }
  }

  // href rules
  const requireHrefFor =
    manifest.validationProfile?.requireHrefForKinds ?? DEFAULT_REQUIRE_HREF_FOR;

  for (const n of nodeMap.values()) {
    const kind = String(n.kind) as any;
    const hrefMissing = !n.href || typeof n.href !== "string" || n.href.trim().length === 0;

    if (requireHrefFor.includes(kind) && hrefMissing) {
      // In v1: link missing href is an error; others are warn (we’re still building readers/paths)
      const sev: Severity = kind === "link" ? "error" : "warn";
      issues.push(
        issue("missing-href", sev, `Node '${n.id}' (${n.kind}) is missing href.`, {
          nodeId: n.id,
          ruleId: "href-required-for-kind",
        })
      );
    }
  }

  // Orphan / reachability (warn)
  if (manifest.rootNodeId && nodeMap.has(manifest.rootNodeId)) {
    const reachable = new Set<string>();
    const stack: string[] = [manifest.rootNodeId];

    while (stack.length) {
      const cur = stack.pop()!;
      if (reachable.has(cur)) continue;
      reachable.add(cur);

      const node = nodeMap.get(cur);
      const children = node && Array.isArray(node.children) ? node.children : [];
      for (const c of children) stack.push(c);
    }

    for (const n of nodeMap.values()) {
      if (!reachable.has(n.id)) {
        issues.push(
          issue("orphan-node", "warn", `Node '${n.id}' is not reachable from root '${manifest.rootNodeId}'.`, {
            nodeId: n.id,
            ruleId: "reachability-from-root",
          })
        );
      }
    }
  }

  return issues;
}
