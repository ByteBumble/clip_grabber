import { useEffect } from 'react';
import { Loader2, X, CheckCircle, AlertCircle } from 'lucide-react';

export default function DownloadProgress({ job, onCancel }) {
  // job: { id, filename, progress, status }
  // status: 'queued' | 'downloading' | 'done' | 'failed'
  useEffect(() => {}, [job]);

  let statusColor = {
    queued: 'bg-gray-400',
    downloading: 'bg-blue-400',
    done: 'bg-green-400',
    failed: 'bg-red-400',
  }[job.status] || 'bg-gray-400';

  let statusIcon = {
    queued: <Loader2 className="animate-spin w-5 h-5" />,
    downloading: <Loader2 className="animate-spin w-5 h-5" />,
    done: <CheckCircle className="w-5 h-5 text-green-500" />,
    failed: <AlertCircle className="w-5 h-5 text-red-500" />,
  }[job.status] || <Loader2 className="w-5 h-5" />;

  return (
    <div className="card bg-white/10 shadow-lg p-4 rounded-xl flex flex-col items-center space-y-2 w-full max-w-md mx-auto">
      <div className="flex items-center gap-2">
        <h2 className="font-semibold text-lg text-white">Downloading: {job.filename}</h2>
        {statusIcon}
      </div>
      <progress className="progress progress-info w-full" value={job.progress} max="100" />
      <div className="flex items-center gap-2">
        <span className={`badge ${statusColor} text-white px-3 py-1 rounded-full text-xs`}>{job.status.charAt(0).toUpperCase() + job.status.slice(1)}</span>
        {job.status === 'downloading' && (
          <button className="btn btn-xs btn-error ml-2 flex items-center gap-1" onClick={() => onCancel(job.id)}>
            <X className="w-4 h-4" /> Cancel
          </button>
        )}
      </div>
    </div>
  );
}
