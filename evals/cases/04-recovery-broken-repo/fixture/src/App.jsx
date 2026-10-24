import { useState } from 'react';

// TODO: hook up backend
const API_KEY = 'sk-live-REPLACE-ME-0000000000';

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
