import styles from './stats.module.css';

export default function StatsCard({ title, value, icon: Icon, info }) {
  return (
    <div className={styles.card}>
      <div className={styles.content}>
        <div className={styles.icon}>
          <Icon size={24} />
        </div>
        <div className={styles.info}>
          <h3>{value}</h3>
          <p>{title}</p>
        </div>
      </div>
      {info && (
        <div className={styles.tooltip}>
          <span>?</span>
          <div className={styles.tooltipText}>{info}</div>
        </div>
      )}
    </div>
  );
}