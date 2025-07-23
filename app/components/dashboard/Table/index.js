'use client';

import Image from 'next/image';
import { RiMoreFill, RiImage2Line } from 'react-icons/ri';
import styles from './table.module.css';

const tableData = [
	{
		id: 1,
		screenshot: '/images/cctv1.jpg',
		dateTime: 'Jul 15, 2025',
		location: 'Campus 2',
		status: 'Non-Uniform',
		name: 'Fazi Al Habib',
		actionTaken: 'Officer A',
		verifiedBy: '-',
		notes: '-',
	},
	// Tambahkan 9 data dummy lainnya dengan format yang sama
];

export default function Table() {
	return (
		<div className={styles.tableWrapper}>
			<table className={styles.table}>
				<thead>
					<tr>
						<th className={styles.imageColumn}>CCTV Screenshot</th>
						<th>Date & Time</th>
						<th>Location</th>
						<th>Status</th>
						<th>Name</th>
						<th>Action Taken</th>
						<th>Verified By</th>
						<th>Notes</th>
						<th className={styles.actionColumn}>Actions</th>
					</tr>
				</thead>
				<tbody>
					{tableData.map((row) => (
						<tr key={row.id}>
							<td className={styles.imageCell}>
								<div className={styles.imageWrapper}>
									<RiImage2Line size={20} />
								</div>
							</td>
							<td>{row.dateTime}</td>
							<td>{row.location}</td>
							<td>
								<span className={`${styles.status} ${styles.nonUniform}`}>
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

			<div className={styles.pagination}>
				<button>&lt;</button>
				<button className={styles.active}>1</button>
				<button>2</button>
				<button>3</button>
				<span>...</span>
				<button>10</button>
				<button>&gt;</button>
			</div>
		</div>
	);
}