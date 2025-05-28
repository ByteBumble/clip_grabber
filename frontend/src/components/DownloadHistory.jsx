import { Download, Trash2, Play, FolderOpen, ExternalLink, Calendar, Clock, FileVideo, AlertCircle, CheckCircle, Loader2 } from 'lucide-react';
import { useState, useEffect } from 'react';
import VideoPlayer from './VideoPlayer';
import { formatDistanceToNow, format } from 'date-fns';

// Helper function to format file size
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// Helper function to get video duration (mock for now, would need actual video metadata)
const getVideoDuration = () => {
  return '05:23'; // Mock duration
};

export default function DownloadHistory({ jobs, onRedownload, onDelete }) {
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [showPlayer, setShowPlayer] = useState(false);
  const [expandedJob, setExpandedJob] = useState(null);

  const handlePlayVideo = (job) => {
    // Clean up the file path for the URL
    const cleanFilePath = (path) => {
      if (!path) return '';
      path = path.replace(/^[./]*/, '');
      if (path.startsWith('downloads/')) {
        path = path.substring(10); // Remove 'downloads/' prefix
      }
      return path;
    };
  
    const videoUrl = job.file_path ? `http://localhost:8000/stream/${cleanFilePath(job.file_path)}` : '';
    
    setSelectedVideo({
      url: videoUrl,
      title: job.filename || 'Video Preview',
      filename: job.file_path?.split('/').pop() || 'video.mp4'
    });
    setShowPlayer(true);
  };

  const handleShowInFolder = (job) => {
    if (!job.file_path) return;
    
    try {
      // Get the file name from the path
      const fileName = job.file_path.split('/').pop();
      // Remove any 'downloads/' prefix if it exists
      let filePath = job.file_path.replace(/^[./]*/, '');
      if (filePath.startsWith('downloads/')) {
        filePath = filePath.substring(10); // Remove 'downloads/' prefix
      }
      
      // Show file in folder using the browser's built-in download
      const downloadUrl = `http://localhost:8000/download/${filePath}`;
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = fileName;
      link.setAttribute('data-file-path', filePath);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      // Show a helpful message
      alert(`The file "${fileName}" will be downloaded to your default downloads folder.`);
      
    } catch (error) {
      console.error('Error showing file in folder:', error);
      alert('Could not open file location. Please check your downloads folder.');
    }
  };

  const toggleExpand = (jobId) => {
    setExpandedJob(expandedJob === jobId ? null : jobId);
  };

  const getStatusBadge = (status) => {
    const statusConfig = {
      completed: { color: 'bg-green-500', icon: <CheckCircle className="w-4 h-4" />, text: 'Completed' },
      pending: { color: 'bg-yellow-500', icon: <Loader2 className="w-4 h-4 animate-spin" />, text: 'In Progress' },
      failed: { color: 'bg-red-500', icon: <AlertCircle className="w-4 h-4" />, text: 'Failed' },
      done: { color: 'bg-green-500', icon: <CheckCircle className="w-4 h-4" />, text: 'Done' }
    };
    
    const config = statusConfig[status] || { color: 'bg-gray-500', icon: <FileText className="w-4 h-4" />, text: status };
    
    return (
      <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium ${config.color} text-white`}>
        {config.icon}
        {config.text}
      </span>
    );
  };

  return (
    <div className="w-full max-w-6xl mx-auto px-4 py-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-white">Download History</h2>
        <div className="text-sm text-gray-400">
          {jobs.length} {jobs.length === 1 ? 'item' : 'items'}
        </div>
      </div>

      <div className="grid gap-4">
        {jobs.map((job) => {
          const isExpanded = expandedJob === job.id;
          const videoUrl = job.file_path?.startsWith('http') 
            ? job.file_path 
            : `http://localhost:8000/stream/${job.file_path?.replace(/^[./]*/, '')}`;
          
          return (
            <div 
              key={job.id} 
              className="bg-slate-800/60 rounded-xl overflow-hidden transition-all duration-200 hover:shadow-lg"
            >
              <div 
                className="p-4 cursor-pointer flex items-center justify-between"
                onClick={() => toggleExpand(job.id)}
              >
                <div className="flex items-center gap-4 flex-1 min-w-0">
                  <div className="flex-shrink-0 w-12 h-12 bg-slate-700/50 rounded-lg flex items-center justify-center">
                    <FileVideo className="w-6 h-6 text-blue-400" />
                  </div>
                  <div className="min-w-0">
                    <h3 className="text-white font-medium truncate">{job.filename || 'Untitled Video'}</h3>
                    <div className="flex items-center gap-3 mt-1 text-sm text-gray-400">
                      <span className="flex items-center gap-1">
                        <Calendar className="w-3.5 h-3.5" />
                        {job.created_at ? format(new Date(job.created_at), 'MMM d, yyyy') : 'Unknown date'}
                      </span>
                      {job.size && (
                        <span className="flex items-center gap-1">
                          <FileText className="w-3.5 h-3.5" />
                          {formatFileSize(job.size)}
                        </span>
                      )}
                      {job.duration && (
                        <span className="flex items-center gap-1">
                          <Clock className="w-3.5 h-3.5" />
                          {job.duration}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2 ml-4">
                  {getStatusBadge(job.status)}
                  <button 
                    className={`p-2 text-gray-400 hover:text-white transition-colors ${isExpanded ? 'rotate-180' : ''}`}
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleExpand(job.id);
                    }}
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                    </svg>
                  </button>
                </div>
              </div>

              {isExpanded && (
                <div className="border-t border-slate-700/50 p-4 bg-slate-800/30">
                  <div className="flex flex-wrap gap-3">
                    {job.status === 'completed' && job.file_path && (
                      <>
                        <button
                          onClick={() => handlePlayVideo(job)}
                          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg flex items-center gap-2 transition-colors"
                        >
                          <Play className="w-5 h-5" />
                          Play Video
                        </button>
                        <a
                          href={`http://localhost:8000/download/${job.file_path?.replace(/^[./]*/, '')}`}
                          className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg flex items-center gap-2 transition-colors"
                          target="_blank"
                          rel="noopener noreferrer"
                        >
                          <Download className="w-5 h-5" />
                          Download
                        </a>
                        <button
                          onClick={() => handleShowInFolder(job)}
                          className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg flex items-center gap-2 transition-colors"
                          title="Download and show file in folder"
                        >
                          <FolderOpen className="w-5 h-5" />
                          Show in Folder
                        </button>
                      </>
                    )}
                    <button
                      onClick={() => onDelete(job.id)}
                      className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg flex items-center gap-2 transition-colors"
                    >
                      <Trash2 className="w-5 h-5" />
                      Delete
                    </button>
                    <a
                      href={job.video_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-4 py-2 bg-slate-600 hover:bg-slate-700 text-white rounded-lg flex items-center gap-2 transition-colors ml-auto"
                    >
                      <ExternalLink className="w-5 h-5" />
                      Source
                    </a>
                  </div>
                  
                  {job.error_message && (
                    <div className="mt-4 p-3 bg-red-900/30 border border-red-800 rounded-lg text-red-200 text-sm">
                      <div className="font-medium flex items-center gap-2 mb-1">
                        <AlertCircle className="w-4 h-4" />
                        Error
                      </div>
                      <div className="font-mono text-xs">{job.error_message}</div>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Video Player Modal */}
      {showPlayer && selectedVideo && (
        <VideoPlayer 
          videoUrl={selectedVideo.url}
          videoTitle={selectedVideo.title}
          filename={selectedVideo.filename}
          onClose={() => setShowPlayer(false)}
        />
      )}
    </div>
  );
}
