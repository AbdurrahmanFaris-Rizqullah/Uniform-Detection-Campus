'use client';

import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip } from 'chart.js';
import { RiQuestionLine } from 'react-icons/ri';
import styles from './charts.module.css';

ChartJS.register(ArcElement, Tooltip);

const data = {
  labels: ['Non-Uniform', 'Uniform'],
  datasets: [
    {
      data: [55, 45],
      backgroundColor: ['#4318FF', '#16205F'],
      borderWidth: 0,
      cutout: '75%',
    },
  ],
};

const options = {
  responsive: true,
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      enabled: false
    }
  },
  maintainAspectRatio: false
};

export default function DonutChart() {
  return (
    <div className={styles.chartCard}>
      <div className={styles.chartHeader}>
        <h3>Incidents by Rate</h3>
        <button className={styles.infoButton}>
          <RiQuestionLine size={12} />
        </button>
      </div>
      <div className={styles.chartContent}>
        <div className={styles.chartWrapper}>
          <Doughnut data={data} options={options} />
        </div>
        <div className={styles.legend}>
          <div className={styles.legendTitle}>
            <span>Incident Type</span>
            <span>Amount</span>
          </div>
          {data.labels.map((label, index) => (
            <div key={label} className={styles.legendItem}>
              <div className={styles.legendLabel}>
                <span 
                  className={styles.legendDot}
                  style={{ backgroundColor: data.datasets[0].backgroundColor[index] }}
                />
                <span>{label}</span>
              </div>
              <span className={styles.legendValue}>{data.datasets[0].data[index]}%</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}