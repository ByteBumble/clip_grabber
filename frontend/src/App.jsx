import './App.css';
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Home, DownloadProgress, DownloadHistory } from './components';
import { Download, History, Home as HomeIcon, Folder } from 'lucide-react';
import { createDownloadJob, getDownloadJobs, deleteDownloadJob } from './api';

function App() {
  const [page, setPage] = useState('home');
  const [activeJobId, setActiveJobId] = useState(null);
  const queryClient = useQueryClient();

  // Fetch jobs from backend, poll every 2 seconds
  const { data: jobs = [], isLoading, refetch } = useQuery({
    queryKey: ['jobs'],
    queryFn: getDownloadJobs,
    refetchInterval: 2000,
  });
  const activeJob = jobs.find(j => j.status === 'downloading' || j.status === 'queued');

  // Create job mutation
  const createJob = useMutation({
    mutationFn: ({ video_url, output_format }) => createDownloadJob(video_url, output_format),
    onSuccess: (job) => {
      setActiveJobId(job.id);
      setPage('progress');
      queryClient.invalidateQueries(['jobs']);
    }
  });

  // Delete job mutation
  const deleteJob = useMutation({
    mutationFn: deleteDownloadJob,
    onSuccess: () => queryClient.invalidateQueries(['jobs'])
  });

  function handleDownload(url, format) {
    createJob.mutate({ video_url: url, output_format: format });
  }

  function handleCancel(jobId) {
    // Optionally implement cancel logic on backend
    // For now, just delete the job
    deleteJob.mutate(jobId);
    setActiveJobId(null);
    setPage('history');
  }

  function handleDelete(jobId) {
    deleteJob.mutate(jobId);
  }

  function handleRedownload(jobId) {
    const job = jobs.find(j => j.id === jobId);
    if (job) handleDownload(job.video_url, job.output_format);
  }

  // Navigation bar
  const nav = (
    <nav className="fixed bottom-0 left-0 w-full bg-gray-950/90 flex justify-around py-2 border-t border-slate-800 z-50">
      <button className={page === 'home' ? 'text-sky-400' : 'text-slate-400'} onClick={() => setPage('home')}><HomeIcon className="inline w-6 h-6" /><div className="text-xs">Home</div></button>
      <button className={page === 'progress' ? 'text-sky-400' : 'text-slate-400'} onClick={() => setPage('progress')}><Download className="inline w-6 h-6" /><div className="text-xs">Progress</div></button>
      <button className={page === 'history' ? 'text-sky-400' : 'text-slate-400'} onClick={() => setPage('history')}><History className="inline w-6 h-6" /><div className="text-xs">History</div></button>
      <a href="../Downloads" target="_blank" className="text-slate-400"><Folder className="inline w-6 h-6" /><div className="text-xs">Downloads</div></a>
    </nav>
  );

  return (
    <div className="relative min-h-screen bg-gradient-to-br from-gray-900 via-slate-800 to-sky-900 flex flex-col items-center justify-start pb-24 w-full">
      <div className="w-full flex-grow flex flex-col items-center justify-center pt-8 px-2">
        {page === 'home' && <>
          <Home onDownload={handleDownload} error={createJob.error?.message} loading={createJob.isLoading} />
          <div className="mt-6 text-slate-400 text-sm text-center">
            <Folder className="inline w-5 h-5 mb-1 mr-1" />
            Downloaded videos are saved in: <span className="font-mono text-white">Downloads/</span> folder in your project directory.
          </div>
        </>}
        {isLoading && (
          <div className="flex flex-col items-center justify-center mt-8">
            <span className="loading loading-spinner loading-lg text-sky-400"></span>
            <div className="text-slate-400 mt-2">Loading jobs...</div>
          </div>
        )}
        {page === 'progress' && activeJob && (
          <DownloadProgress job={activeJob} onCancel={handleCancel} />
        )}
        {page === 'history' && (
          <DownloadHistory jobs={jobs} onRedownload={handleRedownload} onDelete={handleDelete} />
        )}
      </div>
      {nav}
    </div>
  );
}

export default App;
