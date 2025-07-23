'use client';

import { RiCalendarLine, RiDownloadLine, RiSearchLine } from 'react-icons/ri';
import styles from './bottomfilters.module.css';

export default function BottomFilterBar() {
  return (
    <div className={styles.filterBar}>
      <div className={styles.leftSection}>
        <div className={styles.searchBar}>
          <RiSearchLine size={20} />
          <input type="text" placeholder="Search" />
        </div>
      </div>

      <div className={styles.rightSection}>
        <div className={styles.filters}>
          <select className={styles.filterSelect}>
            <option>All</option>
            <option>Campus 2</option>
          </select>
          
          <select className={styles.filterSelect}>
            <option>Non-Uniform</option>
            <option>Uniform</option>
          </select>

          <button className={styles.dateButton}>
            <RiCalendarLine size={18} />
            <span>14 Jul 2025</span>
          </button>
        </div>

        <button className={styles.exportButton}>
          <RiDownloadLine size={18} />
          Export Data
        </button>
      </div>
    </div>
  );
}