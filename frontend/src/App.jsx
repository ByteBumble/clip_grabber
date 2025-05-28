import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { createDownloadJob, getDownloadJobs, getDownloadJob, deleteDownloadJob } from './api';

// Icons
const HomeIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 256 256">
    <path d="M224,115.55V208a16,16,0,0,1-16,16H168a16,16,0,0,1-16-16V168a8,8,0,0,0-8-8H112a8,8,0,0,0-8,8v40a16,16,0,0,1-16,16H48a16,16,0,0,1-16-16V115.55a16,16,0,0,1,5.17-11.78l80-75.48.11-.11a16,16,0,0,1,21.53,0l.11.11,80,75.48A16,16,0,0,1,224,115.55Z"></path>
  </svg>
);

const DownloadIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 256 256">
    <path d="M224,152v56a16,16,0,0,1-16,16H48a16,16,0,0,1-16-16V152a8,8,0,0,1,16,0v56H208V152a8,8,0,0,1,16,0Zm-101.66,5.66a8,8,0,0,0,11.32,0l40-40a8,8,0,0,0-11.32-11.32L136,132.69V40a8,8,0,0,0-16,0v92.69L93.66,106.34a8,8,0,0,0-11.32,11.32Z"></path>
  </svg>
);

const HistoryIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 256 256">
    <path d="M136,80v51.47l42.21,22.35a8,8,0,1,1-7.58,14.14l-45-23.82A8,8,0,0,1,120,136V80a8,8,0,0,1,16,0Zm-8-48a96,96,0,1,0,96,96A96.11,96.11,0,0,0,128,32Zm0,176a80,80,0,1,1,80-80A80.09,80.09,0,0,1,128,208Z"></path>
  </svg>
);

const FolderIcon = ({ filled = false }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 256 256">
    <path d={filled ? "M216,72H131.31L104,44.69A15.86,15.86,0,0,0,92.69,40H40A16,16,0,0,0,24,56V200.62A15.4,15.4,0,0,0,39.38,216h177.5A15.13,15.13,0,0,0,232,200.89V88A16,16,0,0,0,216,72ZM40,56H92.69l16,16H40Z" : "M216,72H131.31L104,44.69A15.86,15.86,0,0,0,92.69,40H40A16,16,0,0,0,24,56V200.62A15.4,15.4,0,0,0,39.38,216h177.5A15.13,15.13,0,0,0,232,200.89V88A16,16,0,0,0,216,72ZM40,56H92.69l16,16H40Z"}></path>
  </svg>
);

const GearIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 256 256">
    <path d="M224,124.16a35.76,35.76,0,0,0-8.58-23.22,4,4,0,0,1,.55-5.51l14.11-11.3a12,12,0,0,0,2.16-15.18,103.25,103.25,0,0,0-11.75-16.17A12,12,0,0,0,210.94,56L197.78,60.6a4,4,0,0,1-5.12-2.23,28.21,28.21,0,0,0-9.72-12.1,4,4,0,0,1-1.65-4.25L184,24.34a12,12,0,0,0-13.59-9.09,100.78,100.78,0,0,0-20.82,6.47,4,4,0,0,1-4.38-.87,35.75,35.75,0,0,0-26.41-11.8,4,4,0,0,1-3.77-4.15V4A12,12,0,0,0,103,2.05,100.8,100.8,0,0,0,82.1,8.6,4,4,0,0,1,77.73,8,36,36,0,0,0,52.35,8.59a4,4,0,0,1-1.65,4.25,28,28,0,0,0-9.72,12.1,4,4,0,0,1-5.12,2.23L24.34,24A12,12,0,0,0,13.4,38.21a103.25,103.25,0,0,0-11.75,16.17A12,12,0,0,0,9.51,71.4l14.11,11.3a4,4,0,0,1,.55,5.51A35.75,35.75,0,0,0,16,124.16v7.68a35.75,35.75,0,0,0,8.17,23.21,4,4,0,0,1-.55,5.51L9.51,172.6a12,12,0,0,0-2.16,15.18,103.25,103.25,0,0,0,11.75,16.17A12,12,0,0,0,24.34,216l13.16-4.6a4,4,0,0,1,5.12,2.23,28.21,28.21,0,0,0,9.72,12.1,4,4,0,0,1,1.65,4.25L52,231.66a12,12,0,0,0,13.59,9.09,100.8,100.8,0,0,0,20.82-6.47,4,4,0,0,1,4.38.87,36,36,0,0,0,26.41,11.8,4,4,0,0,1,3.77,4.15V248a12,12,0,0,0,12,12h1.06a100.8,100.8,0,0,0,21.1-6.43,4,4,0,0,1,4.38.87,36,36,0,0,0,25.41,10.54,4,4,0,0,1,3.77,4.15V248a12,12,0,0,0,12-12v-1.06a100.8,100.8,0,0,0,6.43-21.1,4,4,0,0,1,2.23-5.12l11.3-14.11a12,12,0,0,0-2.16-15.18,103.25,103.25,0,0,0-11.75-16.17,12,12,0,0,0-15.18-2.16l-11.3,14.11a4,4,0,0,1-5.51.55A35.75,35.75,0,0,0,128,152.16Zm-32,4.16a28,28,0,1,1,28-28A28,28,0,0,1,96,156.32Z"></path>
  </svg>
);

function App() {
  const [url, setUrl] = useState('');
  const [quality, setQuality] = useState('best');
  const [isDownloading, setIsDownloading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [downloads, setDownloads] = useState([]);
  const [activeTab, setActiveTab] = useState('downloads');
  const [page, setPage] = useState('home');
  const [activeJobId, setActiveJobId] = useState(null);
  const queryClient = useQueryClient();

  const handleDownload = async () => {
    if (!url) return;
    
    setIsDownloading(true);
    setProgress(0);
    
    try {
      const result = await createDownloadJob(url, quality);
      setActiveJobId(result.id);
      
      // Poll for progress
      const interval = setInterval(async () => {
        if (!activeJobId) return;
        
        const job = await getDownloadJob(activeJobId);
        setProgress(job.progress);
        
        if (job.status === 'completed' || job.status === 'failed') {
          clearInterval(interval);
          setActiveJobId(null);
          setIsDownloading(false);
          fetchDownloads();
        }
      }, 1000);
    } catch (error) {
      console.error('Download failed:', error);
      setIsDownloading(false);
    }
  };

  const fetchDownloads = async () => {
    try {
      const jobs = await getDownloadJobs();
      setDownloads(jobs);
    } catch (error) {
      console.error('Failed to fetch downloads:', error);
    }
  };

  useEffect(() => {
    fetchDownloads();
  }, []);

  const renderTabContent = () => {
    switch(activeTab) {
      case 'home':
        return (
          <div className="p-4">
            <h2 className="text-2xl font-bold mb-4">Home</h2>
            <p>Welcome to Clip Grabber</p>
          </div>
        );
      case 'progress':
        return (
          <div className="p-4">
            <h2 className="text-2xl font-bold mb-4">Download Progress</h2>
            {isDownloading ? (
              <div className="w-full bg-gray-200 rounded-full h-2.5">
                <div 
                  className="bg-blue-600 h-2.5 rounded-full" 
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
            ) : (
              <p>No active downloads</p>
            )}
          </div>
        );
      case 'history':
        return (
          <div className="p-4">
            <h2 className="text-2xl font-bold mb-4">History</h2>
            <div className="space-y-2">
              {downloads.map((item, index) => (
                <div key={index} className="p-3 border-b border-gray-200">
                  <p className="font-medium">{item.title}</p>
                  <p className="text-sm text-gray-500">{new Date(item.date).toLocaleString()}</p>
                </div>
              ))}
            </div>
          </div>
        );
      case 'downloads':
      default:
        return (
          <div className="p-4">
            <h2 className="text-black text-[32px] font-bold text-center pb-4">
              <span className="block">Grab'dat</span>
              <span className="block">Clip</span>
            </h2>
            
            <div className="mb-4">
              <input
                type="text"
                placeholder="Paste YouTube or TikTok link..."
                className="w-full rounded-xl border border-[#E0E0E0] h-14 px-4 text-base focus:outline-none focus:ring-0 focus:border-[#E0E0E0]"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
              />
            </div>
            
            <div className="mb-6">
              <p className="text-black text-base font-medium mb-2">Quality</p>
              <select 
                className="w-full rounded-xl border border-[#E0E0E0] h-14 px-4 text-base focus:outline-none focus:ring-0 focus:border-[#E0E0E0] appearance-none bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgZmlsbD0iIzczNzM3MyIgdmlld0JveD0iMCAwIDI1NiAyNTYiPjxwYXRoIGQ9Ik0xODEuNjYsMTcwLjM0YTgsOCwwLDAsMSwwLDExLjMyLTExLjMyTDE1MiwxMzguMzRsLTQyLjM0LDQyLjM0QTgsOCwwLDAsMSw5OC4zNCwxNzAuMzRsNDgtNDhBOCw4LDAsMCwxLDE1MiwxMjguNjlsNDIuMzQsNDIuMzVabS05Ni04NC42OEwxMjgsNDMuMzFsNDIuMzQsNDIuMzVBOCw4LDAsMCwxLDE2NS42Niw5NS4zNGwtNDgtNDhBOCw4LDAsMCwxLDEwNiw0My4zMWw0Miw0MkE4LDgsMCwwLDEsODUuNjYsODUuNjZaIj48L3BhdGg+PC9zdmc+')] bg-no-repeat bg-[right_1rem_center] bg-[length:24px_24px] pr-10"
                value={quality}
                onChange={(e) => setQuality(e.target.value)}
              >
                <option value="best">Best Quality</option>
                <option value="1080p">1080p</option>
                <option value="720p">720p</option>
                <option value="480p">480p</option>
                <option value="360p">360p</option>
              </select>
            </div>
            
            <div className="flex justify-center">
              <button
                onClick={handleDownload}
                disabled={!url || isDownloading}
                className="flex items-center justify-center rounded-full bg-[#EA2831] text-[#F5F5F5] px-6 py-3 font-bold text-sm gap-2 min-w-[120px] disabled:opacity-50"
              >
                <DownloadIcon />
                <span>{isDownloading ? 'Downloading...' : 'Download'}</span>
              </button>
            </div>
            
            <p className="text-neutral-500 text-sm text-center mt-4">
              Downloaded videos are saved in: Downloads/ folder
            </p>
          </div>
        );
    }
  };

  return (
    <div className="flex flex-col min-h-screen bg-white">
      {/* Header */}
      <header className="flex items-center justify-between p-4 border-b border-[#EEEEEE]">
        <div className="w-12">
          <button className="text-black">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" viewBox="0 0 256 256">
              <path d="M224,128a8,8,0,0,1-8,8H40a8,8,0,0,1,0-16H216A8,8,0,0,1,224,128ZM40,72H216a8,8,0,0,0,0-16H40a8,8,0,0,0,0,16ZM216,184H40a8,8,0,0,0,0,16H216a8,8,0,0,0,0-16Z"></path>
            </svg>
          </button>
        </div>
        <h1 className="text-lg font-bold">Downloads</h1>
        <div className="w-12 flex justify-end">
          <button className="text-black">
            <GearIcon />
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto pb-16">
        {renderTabContent()}
      </main>

      {/* Bottom Navigation */}
      <nav className="flex border-t border-[#EEEEEE] bg-white">
        <button
          onClick={() => setActiveTab('home')}
          className={`flex-1 flex flex-col items-center justify-center py-2 ${activeTab === 'home' ? 'text-black' : 'text-neutral-500'}`}
        >
          <div className="h-8 flex items-center">
            <HomeIcon />
          </div>
        </button>
      </nav>
    </div>
  );
}

export default App;
