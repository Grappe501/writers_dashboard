import type { ReactNode } from "react";
import styles from "./Shell.module.css";

export function Shell(props: { left: ReactNode; center: ReactNode; right: ReactNode }) {
  return (
    <div className={styles.shell}>
      <aside className={styles.left}>{props.left}</aside>
      <main className={styles.center}>{props.center}</main>
      <aside className={styles.right}>{props.right}</aside>
    </div>
  );
}
