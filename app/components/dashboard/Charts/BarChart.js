'use client';

import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend
} from 'chart.js';
import { RiQuestionLine } from 'react-icons/ri';
import styles from './charts.module.css';

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

const data = {
  labels: ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
  datasets: [
    {
      label: 'Uniform',
      data: [20, 12, 35, 15, 45, 5],
      backgroundColor: '#16205F',
      borderRadius: 4,
      barThickness: 12,
    },
    {
      label: 'Non-Uniform',
      data: [35, 20, 12, 35, 35, 15],
      backgroundColor: '#4318FF',
      borderRadius: 4,
      barThickness: 12,
    }
  ],
};

const options = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom',
      labels: {
        usePointStyle: true,
        pointStyle: 'circle',
        padding: 20,
        color: '#64748B',
        font: {
          size: 12,
          family: "'Inter', sans-serif"
        }
      }
    }
  },
  scales: {
    x: {
      grid: {
        display: false
      },
      ticks: {
        color: '#64748B',
        font: {
          size: 12
        }
      }
    },
    y: {
      grid: {
        color: '#E2E8F0'
      },
      ticks: {
        color: '#64748B',
        font: {
          size: 12
        }
      }
    }
  }
};

export default function BarChart() {
  return (
    <div className={styles.chartCard}>
      <div className={styles.chartHeader}>
        <h3>Incidents by Severity</h3>
        <button className={styles.infoButton}>
          <RiQuestionLine size={12} />
        </button>
      </div>
      <div className={styles.barChartWrapper}>
        <Bar data={data} options={options} />
      </div>
    </div>
  );
}