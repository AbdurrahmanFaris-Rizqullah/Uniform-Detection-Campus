'use client';

import { RiCalendarLine, RiDownloadLine } from 'react-icons/ri';
import styles from './topfilters.module.css';

export default function FilterBar() {
  return (
    <div className={styles.filterContainer}>
      <h1 className={styles.title}>Discipline Report</h1>
      <div className={styles.filterBar}>
        <div className={styles.leftSection}>
          <div className={styles.viewOptions}>
            <button className={styles.viewButton}>All</button>
            <button className={styles.viewButton}>Analytics only</button>
            <button className={styles.viewButton}>Table only</button>
          </div>
        </div>

        <div className={styles.rightSection}>
          <div className={styles.filters}>
            <select className={styles.filterSelect}>
              <option>July</option>
              {/* Add other months */}
            </select>
            
            <select className={styles.filterSelect}>
              <option>2025</option>
              {/* Add other years */}
            </select>

            <select className={styles.filterSelect}>
              <option>18</option>
              {/* Add other dates */}
            </select>
          </div>

          <button className={styles.downloadButton}>
            <RiDownloadLine size={18} />
            Download Data
          </button>
        </div>
      </div>
    </div>
  );
}