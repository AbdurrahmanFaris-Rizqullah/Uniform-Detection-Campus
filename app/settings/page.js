'use client';

import { useState } from 'react';
import { RiImageAddLine, RiArrowRightSLine } from 'react-icons/ri';
import Sidebar from '../components/layouts/Sidebar';
import Header from '../components/layouts/Header';
import styles from './settings.module.css';

export default function Settings() {
  const [formData, setFormData] = useState({
    fullName: '',
    username: '',
    email: '',
    phoneNumber: '',
    password: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('Form submitted:', formData);
  };

  const handleReset = () => {
    setFormData({
      fullName: '',
      username: '',
      email: '',
      phoneNumber: '',
      password: ''
    });
  };

  const handleLogout = () => {
    console.log('Logging out...');
  };

  return (
    <div className={styles.container}>
      <Sidebar />
      <div className={styles.main}>
        <Header />
        <div className={styles.content}>
          <h1 className={styles.title}>Settings</h1>
          
          <div className={styles.settingsLayout}>
            <div className={styles.leftSection}>
              <div className={styles.searchContainer}>
                <input
                  type="text"
                  placeholder="Search"
                  className={styles.searchInput}
                />
              </div>

              <div className={styles.menuContainer}>
                <div className={styles.menuItem} onClick={() => console.log('Management Account clicked')}>
                  <span>Management Account</span>
                  <RiArrowRightSLine size={20} />
                </div>
                <div className={styles.menuItem} onClick={handleLogout}>
                  <span>Logout</span>
                  <RiArrowRightSLine size={20} />
                </div>
              </div>
            </div>

            <div className={styles.rightSection}>
              <div className={styles.settingsContainer}>
                <div className={styles.section}>
                  <h2>Account Setting</h2>
                  
                  <form onSubmit={handleSubmit} className={styles.form}>
                    <div className={styles.profilePicture}>
                      <p>Your Profile Picture</p>
                      <div className={styles.uploadArea}>
                        <RiImageAddLine size={24} />
                      </div>
                    </div>

                    <div className={styles.formGroup}>
                      <label htmlFor="fullName">Full name</label>
                      <input
                        type="text"
                        id="fullName"
                        name="fullName"
                        value={formData.fullName}
                        onChange={handleChange}
                        placeholder="Please enter your full name"
                      />
                    </div>

                    <div className={styles.formGroup}>
                      <label htmlFor="username">Username</label>
                      <input
                        type="text"
                        id="username"
                        name="username"
                        value={formData.username}
                        onChange={handleChange}
                        placeholder="Please enter your username"
                      />
                    </div>

                    <div className={styles.formGroup}>
                      <label htmlFor="email">Email</label>
                      <input
                        type="email"
                        id="email"
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                        placeholder="Please enter your email"
                      />
                    </div>

                    <div className={styles.formGroup}>
                      <label htmlFor="phoneNumber">Phone number</label>
                      <input
                        type="tel"
                        id="phoneNumber"
                        name="phoneNumber"
                        value={formData.phoneNumber}
                        onChange={handleChange}
                        placeholder="Please enter your phone number"
                      />
                    </div>

                    <div className={styles.formGroup}>
                      <label htmlFor="password">Reset Password</label>
                      <input
                        type="password"
                        id="password"
                        name="password"
                        value={formData.password}
                        onChange={handleChange}
                        placeholder="Please enter your password"
                      />
                    </div>

                    <div className={styles.buttonGroup}>
                      <button type="submit" className={styles.updateButton}>Update Profile</button>
                      <button type="button" onClick={handleReset} className={styles.resetButton}>Reset</button>
                    </div>
                  </form>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}