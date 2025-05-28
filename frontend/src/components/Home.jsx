import { useRef, useEffect, useState } from 'react';
import { Download, Music, Video } from 'lucide-react';

const formats = [
  { value: 'mp4', label: 'Best Quality', resolution: 'best' },
  { value: 'mp3', label: 'Audio Only (mp3)', resolution: undefined },
];

export default function Home({ onDownload, error }) {
  const [url, setUrl] = useState('');
  const [format, setFormat] = useState('mp4');
  const inputRef = useRef(null);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  function handleSubmit(e) {
    e.preventDefault();
    if (url.trim()) {
      const selected = formats.find(f => f.value === format);
      onDownload(url, selected.value, selected.resolution);
    }
  }

  return (
    <div className="flex flex-col items-center p-4 space-y-4 min-h-[80vh] justify-center bg-gradient-to-br from-gray-900 via-slate-800 to-sky-900 rounded-xl shadow-lg backdrop-blur-md">
      <h1 className="text-2xl font-bold text-sky-300 mb-2">Video Downloader</h1>
      {error && <div className="alert alert-error text-xs mb-2">{typeof error === 'string' ? error : (error?.message || String(error))}</div>}
      <form className="flex flex-col space-y-3 w-full max-w-md" onSubmit={handleSubmit}>
        <input
          ref={inputRef}
          type="url"
          placeholder="Paste YouTube or TikTok link..."
          className="input input-bordered input-primary w-full rounded-lg px-4 py-2 bg-white/10 text-white placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-400"
          value={url}
          onChange={e => setUrl(e.target.value)}
          required
        />
        <select
          className="select select-primary w-full rounded-lg bg-white/10 text-white"
          value={format}
          onChange={e => setFormat(e.target.value)}
        >
          {formats.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>
        <button
          type="submit"
          className="btn btn-primary w-full flex items-center justify-center gap-2 bg-sky-500 hover:bg-sky-600 text-white rounded-lg shadow-md px-4 py-2 transition-all duration-150"
        >
          <Download className="w-5 h-5" /> Download
        </button>
      </form>
    </div>
  );
}
