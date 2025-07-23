'use client';

import { useState } from 'react';
import Sidebar from '../components/layouts/Sidebar';
import Header from '../components/layouts/Header';
import StatsCard from '../components/dashboard/Stats/StatsCard';
import DonutChart from '../components/dashboard/Charts/DonutChart';
import BarChart from '../components/dashboard/Charts/BarChart';
import Table from '../components/dashboard/Table';
import { RiEyeLine, RiAlertLine, RiCheckLine, RiCloseLine } from 'react-icons/ri';
import styles from './dashboard.module.css';
import FilterBar from '../components/dashboard/Filters/FilterBar';
import BottomFilterBar from '../components/dashboard/Filters/bottomfilterBar';

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
	const [viewMode, setViewMode] = useState('all');

	return (
		<div className={styles.container}>
			<Sidebar />
			<main className={styles.main}>
				<Header />
				<div className={styles.content}>
					<FilterBar viewMode={viewMode} onViewModeChange={setViewMode} />
					{(viewMode === 'all' || viewMode === 'analytics') && (
						<>
							<div className={styles.stats}>
								{statsData.map((stat, index) => (
									<StatsCard key={index} {...stat} />
								))}
							</div>
							<div className={styles.charts}>
								<DonutChart />
								<BarChart />
							</div>
						</>
					)}
					{(viewMode === 'all' || viewMode === 'table') && (
						<>
							<BottomFilterBar />
							<Table />
						</>
					)}
				</div>
			</main>
		</div>
	);
}