// API utility for backend communication
const API_BASE = 'http://localhost:8000/api/v1/downloads';

export async function createDownloadJob(video_url, output_format, resolution) {
  const body = { video_url, output_format };
  if (resolution) body.resolution = resolution;
  console.log('createDownloadJob request body:', body);
  const res = await fetch(API_BASE + '/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    let msg = 'Failed to create download job';
    try {
      const err = await res.json();
      console.error('Backend error:', err);
      msg = err.detail || JSON.stringify(err) || msg;
    } catch (e) {
      console.error('Error parsing backend error:', e);
    }
    throw new Error(msg);
  }
  return await res.json();
}

export async function getDownloadJobs() {
  const res = await fetch(API_BASE + '/');
  if (!res.ok) throw new Error('Failed to fetch jobs');
  return await res.json();
}

export async function getDownloadJob(jobId) {
  const res = await fetch(`${API_BASE}/${jobId}`);
  if (!res.ok) throw new Error('Failed to fetch job');
  return await res.json();
}

export async function deleteDownloadJob(jobId) {
  const res = await fetch(`${API_BASE}/${jobId}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Failed to delete job');
  return await res.json();
}
