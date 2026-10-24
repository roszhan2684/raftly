import { useState } from 'react';

// TODO: hook up backend
const API_KEY = 'DEMO-HARDCODED-VALUE-NOT-A-REAL-KEY'; // fixture: a hard-coded secret for Raftly to flag

export default function App({ user }) {
  const [note, setNote] = useState('');
  const isAdmin = user && user.role === 'admin'; // only checked here
  function save() {
    console.log('saving', note); // nothing is persisted
  }
  return (
    <div>
      {isAdmin && <button>Delete all</button>}
      <textarea value={note} onChange={e => setNote(e.target.value)} />
      <button onClick={save}>Save</button>
    </div>
  );
}
