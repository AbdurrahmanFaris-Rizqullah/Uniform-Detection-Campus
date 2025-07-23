'use client';

import { useState } from 'react';
import { RiUser3Fill, RiCloseLine } from 'react-icons/ri';
import Sidebar from '../components/layouts/Sidebar';
import Header from '../components/layouts/Header';
import styles from './access-control.module.css';

export default function AccessControl() {
  const [showMaintenance, setShowMaintenance] = useState(false);
  
  const users = [
    {
      id: 1,
      name: 'Febry Andrias',
      role: 'Admin',
      lastLogin: '10/11/2024 - 09:34 AM'
    },
    {
      id: 2,
      name: 'Dyah Ayu',
      role: 'Admin',
      lastLogin: '10/11/2024 - 09:34 AM'
    },
    {
      id: 3,
      name: 'Abdurrahman Faris',
      role: 'Admin',
      lastLogin: '10/11/2024 - 09:34 AM'
    },
    {
      id: 4,
      name: 'Adelia Kurnia',
      role: 'Admin',
      lastLogin: '10/11/2024 - 09:34 AM'
    }
  ];

  const handleEdit = (userId) => {
    setShowMaintenance(true);
  };

  const handleRemove = (userId) => {
    setShowMaintenance(true);
  };

  const handleAddUser = () => {
    setShowMaintenance(true);
  };

  return (
    <div className={styles.container}>
      <Sidebar />
      <div className={styles.main}>
        <Header />
        <div className={styles.content}>
          <div className={styles.titleContainer}>
            <h1 className={styles.title}>Access Control</h1>
            <button className={styles.addButton} onClick={handleAddUser}>
              Add New User
            </button>
          </div>

          <div className={styles.userList}>
            {users.map(user => (
              <div key={user.id} className={styles.userCard}>
                <div className={styles.userInfo}>
                  <div className={styles.avatar}>
                    <RiUser3Fill size={24} />
                  </div>
                  <div className={styles.details}>
                    <h3 className={styles.userName}>{user.name}</h3>
                    <span className={styles.role}>{user.role}</span>
                    <p className={styles.lastLogin}>Last login: {user.lastLogin}</p>
                  </div>
                </div>
                <div className={styles.actions}>
                  <button
                    className={`${styles.actionButton} ${styles.editButton}`}
                    onClick={() => handleEdit(user.id)}
                  >
                    Edit
                  </button>
                  <button
                    className={`${styles.actionButton} ${styles.removeButton}`}
                    onClick={() => handleRemove(user.id)}
                  >
                    Remove
                  </button>
                </div>
              </div>
            ))}
          </div>

          {showMaintenance && (
            <div className={styles.modal}>
              <div className={styles.modalContent}>
                <button className={styles.closeButton} onClick={() => setShowMaintenance(false)}>
                  <RiCloseLine size={24} />
                </button>
                <div className={styles.maintenanceMessage}>
                  <h2>Under Maintenance</h2>
                  <p>This feature is currently under maintenance. Please try again later.</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}