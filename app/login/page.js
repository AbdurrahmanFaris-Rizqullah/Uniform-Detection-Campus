'use client';

import { useState, useEffect } from 'react';
import Image from 'next/image';
import { HiEye, HiEyeOff } from 'react-icons/hi';  // tambahkan import ini
import styles from './login.module.css';

const slides = [
  {
    title: "Always monitoring your day",
    description: "On the shot, you see the main screen with all the rooms, and users can control each camera with the help of remote control"
  },
  {
    title: "Real-time Detection",
    description: "Instantly detect and report uniform violations through our advanced AI system"
  },
  {
    title: "Comprehensive Reporting",
    description: "Access detailed reports and analytics of uniform compliance"
  }
];

export default function LoginPage() {
  const [currentSlide, setCurrentSlide] = useState(0);
  const [showPassword, setShowPassword] = useState(false);
  const [isChanging, setIsChanging] = useState(false);

  useEffect(() => {
    const timer = setInterval(() => {
      setIsChanging(true); // Mulai animasi slide
      
      setTimeout(() => {
        setCurrentSlide((prevSlide) => 
          prevSlide === slides.length - 1 ? 0 : prevSlide + 1
        );
        setIsChanging(false); // Reset posisi
      }, 500); // Sesuaikan dengan durasi transisi CSS
      
    }, 5000);

    return () => clearInterval(timer);
  }, []);

  return (
    <div className={styles.container}>
      <div className={styles.loginSection}>
        <h3 className={styles.title}>LOGIN UNIFORM DETECTION</h3>
        
        <form className={styles.form}>
          <div className={styles.inputGroup}>
            <input 
              type="text" 
              placeholder="Enter email or phone number"
              className={styles.input}
            />
          </div>

          <div className={styles.inputGroup}>
            <input 
              type={showPassword ? "text" : "password"}
              placeholder="Password"
              className={styles.input}
            />
            <button 
              type="button"
              className={styles.togglePassword}
              onClick={() => setShowPassword(!showPassword)}
            >
              {showPassword ? <HiEye size={20} color="#16205F" /> : <HiEyeOff size={20} color="#16205F" />}
            </button>
          </div>

          <div className={styles.recoveryLink}>
            <a href="/recovery">Recovery Password</a>
          </div>

          <button type="submit" className={styles.loginButton}>
            Login
          </button>
        </form>
      </div>

      <div className={styles.sliderSection}>
        <div className={styles.imageWrapper}>
          <Image
            src="/img/login/cctv.svg"
            alt="CCTV monitoring"
            width={395.41}
            height={297.32}
            priority
          />
        </div>
        <div className={`${styles.slideContent} ${isChanging ? styles.changing : ''}`}>
          <h4>{slides[currentSlide].title}</h4>
          <p>{slides[currentSlide].description}</p>
          
          <div className={styles.dots}>
            {slides.map((_, index) => (
              <button
                key={index}
                className={`${styles.dot} ${currentSlide === index ? styles.activeDot : ''}`}
                onClick={() => setCurrentSlide(index)}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}