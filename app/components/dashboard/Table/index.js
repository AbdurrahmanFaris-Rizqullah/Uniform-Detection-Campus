'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import { 
  RiMoreFill, 
  RiImage2Line, 
  RiCloseLine,
  RiArrowUpLine,
  RiArrowDownLine,
  RiLoader4Line 
} from 'react-icons/ri';
import styles from './table.module.css';

const ITEMS_PER_PAGE = 10;

export default function Table() {
  // States
  const [selectedImage, setSelectedImage] = useState(null);
  const [tableData, setTableData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' });
  const [filters, setFilters] = useState({
    location: '',
    status: '',
    date: '',
    actionTaken: ''
  });

  // Dummy data untuk contoh
  const dummyData = [
    {
      id: 1,
      screenshot: '/img/dashboard/cctv1.jpg',
      dateTime: 'Jul 15, 2025',
      location: 'Campus 2',
      status: 'Non-Uniform',
      name: 'Fazi Al Habib',
      actionTaken: 'Officer A',
      verifiedBy: '-',
      notes: '-',
    },
    // ... tambahkan data dummy lainnya
  ];

  // Effects
  useEffect(() => {
    // Simulasi loading data
    setLoading(true);
    setTimeout(() => {
      setTableData(dummyData);
      setTotalPages(Math.ceil(dummyData.length / ITEMS_PER_PAGE));
      setLoading(false);
    }, 1000);
  }, []);

  // Handlers
  const handleSort = (key) => {
    let direction = 'asc';
    if (sortConfig.key === key && sortConfig.direction === 'asc') {
      direction = 'desc';
    }
    setSortConfig({ key, direction });

    const sortedData = [...tableData].sort((a, b) => {
      if (a[key] < b[key]) return direction === 'asc' ? -1 : 1;
      if (a[key] > b[key]) return direction === 'asc' ? 1 : -1;
      return 0;
    });

    setTableData(sortedData);
  };

  const handleFilter = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    // Implementasi filter berdasarkan nilai baru
    const filteredData = dummyData.filter(item => {
      return Object.keys(filters).every(filterKey => {
        if (!filters[filterKey]) return true;
        return item[filterKey].toLowerCase().includes(filters[filterKey].toLowerCase());
      });
    });
    setTableData(filteredData);
    setCurrentPage(1);
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  // Render helpers
  const renderSortIcon = (key) => {
    if (sortConfig.key !== key) return null;
    return sortConfig.direction === 'asc' ? 
      <RiArrowUpLine className={styles.sortIcon} /> : 
      <RiArrowDownLine className={styles.sortIcon} />;
  };

  const renderPagination = () => {
    const pages = [];
    for (let i = 1; i <= totalPages; i++) {
      pages.push(
        <button
          key={i}
          className={`${styles.pageButton} ${currentPage === i ? styles.active : ''}`}
          onClick={() => handlePageChange(i)}
        >
          {i}
        </button>
      );
    }
    return pages;
  };

  if (loading) {
    return (
      <div className={styles.loadingState}>
        <RiLoader4Line className={styles.loadingIcon} />
        <p>Loading data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.errorState}>
        <p>Error: {error}</p>
        <button onClick={() => window.location.reload()}>Retry</button>
      </div>
    );
  }

  if (!tableData.length) {
    return (
      <div className={styles.emptyState}>
        <p>No data available</p>
      </div>
    );
  }

  return (
    <div className={styles.tableWrapper}>
      <div className={styles.filterSection}>
        <select 
          value={filters.location}
          onChange={(e) => handleFilter('location', e.target.value)}
          className={styles.filterSelect}
        >
          <option value="">All Locations</option>
          <option value="Campus 1">Campus 1</option>
          <option value="Campus 2">Campus 2</option>
        </select>

        <select
          value={filters.status}
          onChange={(e) => handleFilter('status', e.target.value)}
          className={styles.filterSelect}
        >
          <option value="">All Status</option>
          <option value="Uniform">Uniform</option>
          <option value="Non-Uniform">Non-Uniform</option>
        </select>

        <input
          type="date"
          value={filters.date}
          onChange={(e) => handleFilter('date', e.target.value)}
          className={styles.filterInput}
        />

        <select
          value={filters.actionTaken}
          onChange={(e) => handleFilter('actionTaken', e.target.value)}
          className={styles.filterSelect}
        >
          <option value="">All Officers</option>
          <option value="Officer A">Officer A</option>
          <option value="Officer B">Officer B</option>
        </select>
      </div>

      <div className={styles.tableContainer}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th className={styles.imageColumn}>CCTV Screenshot</th>
              <th onClick={() => handleSort('dateTime')} className={styles.sortable}>
                Date & Time {renderSortIcon('dateTime')}
              </th>
              <th onClick={() => handleSort('location')} className={styles.sortable}>
                Location {renderSortIcon('location')}
              </th>
              <th onClick={() => handleSort('status')} className={styles.sortable}>
                Status {renderSortIcon('status')}
              </th>
              <th onClick={() => handleSort('name')} className={styles.sortable}>
                Name {renderSortIcon('name')}
              </th>
              <th>Action Taken</th>
              <th>Verified By</th>
              <th>Notes</th>
              <th className={styles.actionColumn}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {tableData
              .slice((currentPage - 1) * ITEMS_PER_PAGE, currentPage * ITEMS_PER_PAGE)
              .map((row) => (
                <tr key={row.id}>
                  <td className={styles.imageCell}>
                    <div 
                      className={styles.imageWrapper}
                      onClick={() => setSelectedImage(row.screenshot)}
                      role="button"
                      tabIndex={0}
                      onKeyPress={(e) => e.key === 'Enter' && setSelectedImage(row.screenshot)}
                    >
                      <RiImage2Line size={20} />
                    </div>
                  </td>
                  <td>{row.dateTime}</td>
                  <td>{row.location}</td>
                  <td>
                    <span className={`${styles.status} ${row.status === 'Non-Uniform' ? styles.nonUniform : styles.uniform}`}>
                      {row.status}
                    </span>
                  </td>
                  <td>{row.name}</td>
                  <td>{row.actionTaken}</td>
                  <td>{row.verifiedBy}</td>
                  <td>{row.notes}</td>
                  <td className={styles.actionCell}>
                    <button className={styles.actionButton}>
                      <RiMoreFill size={18} />
                    </button>
                  </td>
                </tr>
              ))}
          </tbody>
        </table>
      </div>

      <div className={styles.pagination}>
        <button
          onClick={() => handlePageChange(currentPage - 1)}
          disabled={currentPage === 1}
        >
          &lt;
        </button>
        {renderPagination()}
        <button
          onClick={() => handlePageChange(currentPage + 1)}
          disabled={currentPage === totalPages}
        >
          &gt;
        </button>
      </div>

      {selectedImage && (
        <div 
          className={styles.imagePopup}
          onClick={() => setSelectedImage(null)}
          role="dialog"
          aria-label="CCTV Screenshot Preview"
        >
          <div 
            className={styles.imagePopupContent}
            onClick={(e) => e.stopPropagation()}
          >
            <button 
              className={styles.closeButton}
              onClick={() => setSelectedImage(null)}
              aria-label="Close preview"
            >
              <RiCloseLine size={24} />
            </button>
            <Image
              src={selectedImage}
              alt="CCTV Screenshot"
              width={800}
              height={600}
              objectFit="contain"
              priority
            />
          </div>
        </div>
      )}
    </div>
  );
}