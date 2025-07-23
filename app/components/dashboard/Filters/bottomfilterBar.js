'use client';

import { RiSearchLine } from 'react-icons/ri';
import styles from './bottomfilters.module.css';

export default function BottomFilterBar() {
  return (
    <div className={styles.filterBar}>
      <div className={styles.searchBar}>
        <RiSearchLine size={20} />
        <input type="text" placeholder="Search" />
      </div>
    </div>
  );
}