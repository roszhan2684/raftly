import { initializeApp } from 'firebase/app';
import { getFirestore, collection, addDoc, getDocs } from 'firebase/firestore';

// Fixture only: never executed. Uses a placeholder project id instead of reading the environment.
const app = initializeApp({ projectId: 'demo-team-tasks' });
export const db = getFirestore(app);

export async function addTask(teamId, task) {
  return addDoc(collection(db, 'teams', teamId, 'tasks'), task);
}

export async function listTasks(teamId) {
  const snap = await getDocs(collection(db, 'teams', teamId, 'tasks'));
  return snap.docs.map(d => ({ id: d.id, ...d.data() }));
}
