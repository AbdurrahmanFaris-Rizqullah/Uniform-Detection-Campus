'use client';

import { useState } from 'react';
import { RiNotification3Line, RiSettings4Line } from 'react-icons/ri';
import styles from './header.module.css';

export default function Header() {
  return (
    <header className={styles.header}>
      <div className={styles.left}>
        <h1>Discipline Report</h1>
      </div>

      <div className={styles.right}>
        <button className={styles.iconButton}>
          <RiNotification3Line size={20} />
          <span className={styles.badge}>1</span>
        </button>
        
        <button className={styles.iconButton}>
          <RiSettings4Line size={20} />
        </button>
      </div>
    </header>
  );
}