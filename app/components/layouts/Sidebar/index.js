'use client';

import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import { RiDashboardLine, RiFileList3Line, RiUserSettingsLine, RiAddLine } from 'react-icons/ri';
import styles from './sidebar.module.css';

const menuItems = [
  { icon: RiDashboardLine, label: 'Dashboard', path: '/dashboard' },
  { icon: RiFileList3Line, label: 'Report', path: '/report' },
  { icon: RiUserSettingsLine, label: 'Access Control', path: '/access' },
  { icon: RiAddLine, label: 'Add New Location', path: '/location/new' },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className={styles.sidebar}>
      <div className={styles.logo}>
        <Image 
          src="/img/logo.svg" 
          alt="Uniform Detection" 
          width={40} 
          height={40} 
        />
        <span>UNIFORM</span>
      </div>

      <nav className={styles.nav}>
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.path;
          
          return (
            <Link 
              key={item.path}
              href={item.path}
              className={`${styles.navItem} ${isActive ? styles.active : ''}`}
            >
              <Icon size={20} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className={styles.profile}>
        <Image
          src="/img/avatar.jpg"
          alt="User Avatar"
          width={40}
          height={40}
          className={styles.avatar}
        />
        <div className={styles.profileInfo}>
          <span className={styles.name}>Febry Andrias</span>
          <span className={styles.role}>Admin</span>
        </div>
      </div>
    </aside>
  );
}