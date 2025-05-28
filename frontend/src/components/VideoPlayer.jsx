import { Download, X } from 'lucide-react';
import { useEffect, useState } from 'react';

export default function VideoPlayer({ videoUrl, videoTitle, filename, onClose }) {
  const [isOpen, setIsOpen] = useState(true);
  const [videoSource, setVideoSource] = useState('');

  useEffect(() => {
    if (videoUrl) {
      try {
        // Convert download URL to stream URL
        const url = new URL(videoUrl);
        const filename = url.pathname.split('/').pop();
        const streamUrl = `/stream/${filename}`;
        
        // Create a new URL with the stream endpoint
        const streamUrlObj = new URL(streamUrl, window.location.origin);
        
        // Add a timestamp to prevent caching
        streamUrlObj.searchParams.append('t', Date.now());
        
        console.log('Streaming video from:', streamUrlObj.toString());
        setVideoSource(streamUrlObj.toString());
      } catch (error) {
        console.error('Error creating video source URL:', error);
        // Fallback to original URL if there's an error
        setVideoSource(videoUrl);
      }
    }
  }, [videoUrl]);

  if (!isOpen) return null;

  const handleDownload = (e) => {
    // Let the browser handle the download
    // The anchor tag's href is already set to the correct URL
  };

  const handleClose = () => {
    setIsOpen(false);
    onClose?.();
  };

  return (
    <div className="fixed inset-0 bg-black/90 z-50 flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-4xl bg-slate-800 rounded-xl overflow-hidden shadow-2xl">
        <div className="flex justify-between items-center bg-slate-900 px-4 py-3">
          <h3 className="text-white font-medium truncate max-w-[80%]">
            {videoTitle || 'Video Player'}
          </h3>
          <div className="flex space-x-2">
            <a
              href={videoUrl}
              download={filename || 'video.mp4'}
              onClick={handleDownload}
              className="p-2 text-green-400 hover:bg-slate-700 rounded-full transition-colors"
              title="Download Video"
            >
              <Download className="w-5 h-5" />
            </a>
            <button
              onClick={handleClose}
              className="p-2 text-gray-300 hover:bg-slate-700 rounded-full transition-colors"
              title="Close"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>
        <div className="aspect-video bg-black">
          {videoSource ? (
            <video
              key={videoSource} // Force re-render when source changes
              src={videoSource}
              controls
              autoPlay
              playsInline
              className="w-full h-full"
              onError={(e) => {
                console.error('Error loading video:', e);
                console.log('Video source URL:', videoSource);
                alert('Error loading video. The file format might not be supported in the browser or the video might still be processing. Try downloading it instead.');
              }}
              onCanPlay={() => console.log('Video can play')}
              onStalled={(e) => console.log('Video stalled:', e)}
              onSuspend={(e) => console.log('Video suspended:', e)}
            >
              Your browser does not support the video tag.
              <a href={videoSource} download={filename} className="text-blue-400 underline">
                Download the video
              </a>
            </video>
          ) : (
            <div className="w-full h-full flex items-center justify-center text-white">
              Loading video...
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
