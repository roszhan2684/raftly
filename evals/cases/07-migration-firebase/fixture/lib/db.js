import { initializeApp } from 'firebase/app';
import { getFirestore, collection, addDoc, getDocs } from 'firebase/firestore';

const app = initializeApp({ projectId: process.env.FIREBASE_PROJECT_ID });
export const db = getFirestore(app);

export async function addTask(teamId, task) {
  return addDoc(collection(db, 'teams', teamId, 'tasks'), task);
}

export async function listTasks(teamId) {
  const snap = await getDocs(collection(db, 'teams', teamId, 'tasks'));
  return snap.docs.map(d => ({ id: d.id, ...d.data() }));
}
