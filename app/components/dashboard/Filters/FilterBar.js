'use client';

import { useState } from 'react';
import { RiDownloadLine, RiFilePdfLine, RiFileExcelLine, RiFileTextLine } from 'react-icons/ri';
import styles from './topfilters.module.css';

export default function FilterBar({ viewMode, onViewModeChange }) {
  const [showExportModal, setShowExportModal] = useState(false);
  const [exportFilters, setExportFilters] = useState({
    period: 'today',
    dateRange: {
      start: '',
      end: ''
    },
    locations: [],
    status: 'all'
  });

  const handleExport = (format) => {
    // Implementasi export berdasarkan format dan filter
    console.log('Exporting in format:', format, 'with filters:', exportFilters);
    setShowExportModal(false);
  };

  return (
    <div className={styles.filterContainer}>
      <h1 className={styles.title}>Discipline Report</h1>
      <div className={styles.filterBar}>
        <div className={styles.leftSection}>
          <div className={styles.viewOptions}>
            <button 
              className={`${styles.viewButton} ${viewMode === 'all' ? styles.active : ''}`}
              onClick={() => onViewModeChange('all')}
            >
              All
            </button>
            <button 
              className={`${styles.viewButton} ${viewMode === 'analytics' ? styles.active : ''}`}
              onClick={() => onViewModeChange('analytics')}
            >
              Analytics only
            </button>
            <button 
              className={`${styles.viewButton} ${viewMode === 'table' ? styles.active : ''}`}
              onClick={() => onViewModeChange('table')}
            >
              Table only
            </button>
          </div>
        </div>

        <div className={styles.rightSection}>
          <div className={styles.filters}>
            <select className={styles.filterSelect}>
              <option>July</option>
            </select>
            
            <select className={styles.filterSelect}>
              <option>2025</option>
            </select>

            <select className={styles.filterSelect}>
              <option>18</option>
            </select>
          </div>

          <button 
            className={styles.exportButton} 
            onClick={() => setShowExportModal(true)}
          >
            <RiDownloadLine size={18} />
            Export Report
          </button>
        </div>
      </div>

      {showExportModal && (
        <div className={styles.modalOverlay}>
          <div className={styles.exportModal}>
            <h3>Export Report</h3>
            
            <div className={styles.filterGroup}>
              <label>Period</label>
              <select 
                value={exportFilters.period}
                onChange={(e) => setExportFilters({...exportFilters, period: e.target.value})}
              >
                <option value="today">Today</option>
                <option value="week">This Week</option>
                <option value="month">This Month</option>
                <option value="custom">Custom Range</option>
              </select>

              {exportFilters.period === 'custom' && (
                <div className={styles.dateRangeInputs}>
                  <input 
                    type="date" 
                    value={exportFilters.dateRange.start}
                    onChange={(e) => setExportFilters({
                      ...exportFilters, 
                      dateRange: {...exportFilters.dateRange, start: e.target.value}
                    })}
                  />
                  <input 
                    type="date"
                    value={exportFilters.dateRange.end}
                    onChange={(e) => setExportFilters({
                      ...exportFilters, 
                      dateRange: {...exportFilters.dateRange, end: e.target.value}
                    })}
                  />
                </div>
              )}
            </div>

            <div className={styles.filterGroup}>
              <label>Location</label>
              <select 
                multiple
                value={exportFilters.locations}
                onChange={(e) => setExportFilters({
                  ...exportFilters, 
                  locations: Array.from(e.target.selectedOptions, option => option.value)
                })}
              >
                <option value="all">All Locations</option>
                <option value="campus1">Campus 1</option>
                <option value="campus2">Campus 2</option>
              </select>
            </div>

            <div className={styles.filterGroup}>
              <label>Status</label>
              <select
                value={exportFilters.status}
                onChange={(e) => setExportFilters({...exportFilters, status: e.target.value})}
              >
                <option value="all">All Status</option>
                <option value="uniform">Uniform</option>
                <option value="non-uniform">Non-Uniform</option>
              </select>
            </div>

            <div className={styles.formatButtons}>
              <button onClick={() => handleExport('pdf')} className={styles.formatButton}>
                <RiFilePdfLine size={20} />
                PDF Report
              </button>
              <button onClick={() => handleExport('excel')} className={styles.formatButton}>
                <RiFileExcelLine size={20} />
                Excel Data
              </button>
              <button onClick={() => handleExport('csv')} className={styles.formatButton}>
                <RiFileTextLine size={20} />
                CSV Data
              </button>
            </div>

            <div className={styles.modalActions}>
              <button 
                className={styles.cancelButton}
                onClick={() => setShowExportModal(false)}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}