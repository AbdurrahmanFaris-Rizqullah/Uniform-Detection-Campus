'use client';

import Sidebar from '../components/layouts/Sidebar';
import Header from '../components/layouts/Header';
import StatsCard from '../components/dashboard/Stats/StatsCard';
import DonutChart from '../components/dashboard/Charts/DonutChart';
import BarChart from '../components/dashboard/Charts/BarChart';
import { RiEyeLine, RiAlertLine, RiCheckLine, RiCloseLine } from 'react-icons/ri';
import styles from './dashboard.module.css';

const statsData = [
	{
		title: 'Total Detection',
		value: '40',
		icon: RiEyeLine,
		info: 'Total number of uniform detections today',
	},
	{
		title: 'Total Violations',
		value: '22',
		icon: RiAlertLine,
		info: 'Number of uniform violations detected',
	},
	{
		title: 'Compliance Percentage',
		value: '18%',
		icon: RiCheckLine,
		info: 'Percentage of students following uniform rules',
	},
	{
		title: 'Non-compliance Percentage',
		value: '22%',
		icon: RiCloseLine,
		info: 'Percentage of students violating uniform rules',
	},
];

export default function DashboardPage() {
	return (
		<div className={styles.container}>
			<Sidebar />
			<main className={styles.main}>
				<Header />
				<div className={styles.content}>
					<div className={styles.stats}>
						{statsData.map((stat, index) => (
							<StatsCard key={index} {...stat} />
						))}
					</div>
					
					<div className={styles.charts}>
						<DonutChart />
						<BarChart />
					</div>
					
					<div className={styles.table}>
						{/* Data table */}
					</div>
				</div>
			</main>
		</div>
	);
}