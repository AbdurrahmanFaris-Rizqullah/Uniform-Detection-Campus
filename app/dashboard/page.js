'use client';

import Sidebar from '../components/layouts/Sidebar';
import styles from './dashboard.module.css';

export default function DashboardPage() {
  return (
    <div className={styles.container}>
      <Sidebar />
      <main className={styles.main}>
        <header className={styles.header}>
          {/* Header content */}
        </header>
        
        <div className={styles.content}>
          <div className={styles.stats}>
            {/* Stats cards */}
          </div>
          
          <div className={styles.charts}>
            {/* Charts section */}
          </div>
          
          <div className={styles.table}>
            {/* Data table */}
          </div>
        </div>
      </main>
    </div>
  );
}   