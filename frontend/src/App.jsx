
import { useState, useRef } from 'react';
import axios from 'axios';
import {
  Upload,
  Video,
  FileVideo,
  Download,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  Play,
  ChevronRight,
  MonitorPlay,
  Cpu
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

function App() {
  const [file, setFile] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [resultVideo, setResultVideo] = useState(null);
  const [error, setError] = useState(null);
  const [progress, setProgress] = useState(0);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type.startsWith('video/')) {
      setFile(selectedFile);
      setError(null);
      setResultVideo(null);
    } else {
      setError("Please select a valid video file (MP4, MOV, etc.).");
    }
  };

  const handleDubVideo = async () => {
    if (!file) return;

    setIsProcessing(true);
    setError(null);
    setProgress(0);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('/api/dub-video', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        responseType: 'blob',
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setProgress(percentCompleted);
        }
      });

      const videoUrl = URL.createObjectURL(new Blob([response.data], { type: 'video/mp4' }));
      setResultVideo(videoUrl);
    } catch (err) {
      console.error("Dubbing failed:", err);
      setError("The dubbing process failed. Please check your API keys and try again.");
    } finally {
      setIsProcessing(false);
      setProgress(0);
    }
  };

  const reset = () => {
    setFile(null);
    setResultVideo(null);
    setIsProcessing(false);
    setError(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center p-4 md:p-8 bg-mesh">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card w-full max-w-5xl overflow-hidden"
      >
        {/* Top Navbar Simulation */}
        <div className="px-8 py-6 border-b border-white/5 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <Video className="w-6 h-6 text-white" />
            </div>
            <span className="text-xl font-bold tracking-tight">Dubbing<span className="text-indigo-400">AI</span></span>
          </div>
          <div className="hidden md:flex items-center gap-6 text-sm font-medium text-text-muted">
            <span className="hover:text-white transition-colors cursor-pointer">Technology</span>
            <span className="hover:text-white transition-colors cursor-pointer">Voices</span>
            <span className="hover:text-white transition-colors cursor-pointer">API</span>
          </div>
        </div>

        <div className="p-8 md:p-12">
          {/* Header Section */}
          <div className="max-w-2xl mb-12">
            <motion.h1
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="text-5xl md:text-6xl font-extrabold mb-4 leading-tight gradient-text"
            >
              Break Language <br />
              <span className="text-glow text-indigo-400">Barriers Globally</span>
            </motion.h1>
            <p className="text-text-muted text-lg leading-relaxed">
              Professional video dubbing in Telugu powered by Google Translate and OpenAI GPT-4o.
              Upload your video and get high-quality audio with synchronized lip movements.
            </p>
          </div>

          <main className="relative">
            <AnimatePresence mode="wait">
              {!file && !resultVideo && (
                <motion.div
                  key="upload"
                  initial={{ opacity: 0, scale: 0.98 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.98 }}
                  onClick={() => fileInputRef.current?.click()}
                  className="upload-zone group relative overflow-hidden"
                >
                  <div className="absolute inset-0 bg-indigo-500/5 opacity-0 group-hover:opacity-100 transition-opacity" />
                  <input
                    type="file"
                    ref={fileInputRef}
                    onChange={handleFileChange}
                    className="hidden"
                    accept="video/*"
                  />
                  <div className="relative flex flex-col items-center gap-6 py-8">
                    <div className="relative">
                      <div className="absolute inset-0 scale-150 blur-2xl bg-indigo-500/20 rounded-full" />
                      <div className="relative w-20 h-20 rounded-3xl bg-white/5 border border-white/10 flex items-center justify-center group-hover:border-indigo-500/50 transition-all duration-500">
                        <Upload className="w-10 h-10 text-text-muted group-hover:text-indigo-400 group-hover:translate-y-[-4px] transition-all duration-500" />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <p className="text-2xl font-bold">Pick your video file</p>
                      <p className="text-text-muted font-medium">Drag & Drop or click to browse</p>
                    </div>
                    <div className="flex gap-4 mt-2">
                      <span className="px-4 py-1.5 rounded-full bg-white/5 border border-white/5 text-xs font-semibold text-text-muted uppercase tracking-widest">MP4</span>
                      <span className="px-4 py-1.5 rounded-full bg-white/5 border border-white/5 text-xs font-semibold text-text-muted uppercase tracking-widest">MOV</span>
                      <span className="px-4 py-1.5 rounded-full bg-white/5 border border-white/5 text-xs font-semibold text-text-muted uppercase tracking-widest">AVI</span>
                    </div>
                  </div>
                </motion.div>
              )}

              {file && !resultVideo && (
                <motion.div
                  key="preview"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="space-y-8"
                >
                  <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 rounded-3xl bg-white/5 border border-white/10">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 flex items-center justify-center">
                        <FileVideo className="w-6 h-6 text-indigo-400" />
                      </div>
                      <div>
                        <p className="text-lg font-bold leading-none mb-1">{file.name}</p>
                        <p className="text-sm text-text-muted font-medium">{(file.size / (1024 * 1024)).toFixed(2)} MB • Ready to process</p>
                      </div>
                    </div>
                    <button
                      onClick={reset}
                      className="text-text-muted hover:text-white text-sm font-semibold transition-colors flex items-center gap-2"
                      disabled={isProcessing}
                    >
                      <RefreshCw className="w-4 h-4" /> Change Source
                    </button>
                  </div>

                  <div className="grid md:grid-cols-5 gap-8">
                    <div className="md:col-span-3 space-y-4">
                      <div className="video-container group">
                        <video src={URL.createObjectURL(file)} controls className="w-full h-full" />
                        <div className="absolute top-4 left-4">
                          <span className="bg-black/60 backdrop-blur-md text-white text-[10px] font-bold px-3 py-1 rounded-full uppercase tracking-widest border border-white/10">Input Preview</span>
                        </div>
                      </div>
                    </div>

                    <div className="md:col-span-2 flex flex-col justify-center space-y-6">
                      <div className="space-y-4">
                        <h3 className="text-xl font-bold flex items-center gap-2">
                          <Cpu className="w-5 h-5 text-indigo-400" /> AI Pipeline Ready
                        </h3>
                        <div className="space-y-3">
                          {[
                            { label: 'Whisper Segmentation', status: 'Ready' },
                            { label: 'Google Translation', status: 'Ready' },
                            { label: 'OpenAI Polishing', status: 'Ready' },
                            { label: 'Falcon TTS (Murf)', status: 'Online' }
                          ].map((item, idx) => (
                            <div key={idx} className="flex items-center justify-between p-3 rounded-xl bg-white/5 border border-white/5 text-sm">
                              <span className="text-text-muted">{item.label}</span>
                              <span className="text-indigo-400 font-bold text-xs uppercase tracking-wider">{item.status}</span>
                            </div>
                          ))}
                        </div>
                      </div>

                      {isProcessing ? (
                        <div className="space-y-6">
                          <div className="p-6 rounded-3xl bg-indigo-500/5 border border-indigo-500/20">
                            <div className="flex items-center justify-center gap-3 text-indigo-400 mb-4 font-bold text-xl">
                              <RefreshCw className="w-6 h-6 animate-spin" />
                              <span>AI at Work...</span>
                            </div>
                            <div className="h-2.5 w-full bg-white/5 rounded-full overflow-hidden mb-2">
                              <motion.div
                                className="h-full bg-indigo-500 shadow-[0_0_15px_rgba(99,102,241,0.5)]"
                                initial={{ width: 0 }}
                                animate={{ width: `${progress < 5 ? 5 : progress}%` }}
                                transition={{ type: "spring", stiffness: 50 }}
                              />
                            </div>
                            <div className="flex justify-between text-xs font-bold text-text-muted uppercase tracking-widest">
                              <span>Processing</span>
                              <span>{progress}%</span>
                            </div>
                          </div>
                          <p className="text-center text-sm text-text-muted italic">
                            Translating audio and aligning lip movements. <br /> This takes about 30-60 seconds.
                          </p>
                        </div>
                      ) : (
                        <button
                          onClick={handleDubVideo}
                          className="primary-button text-xl py-6 shadow-2xl shadow-indigo-500/40 relative group overflow-hidden"
                        >
                          <div className="absolute inset-0 bg-white/10 translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700" />
                          <span className="relative flex items-center gap-3">
                            Start Project Dubbing <ChevronRight className="w-6 h-6" />
                          </span>
                        </button>
                      )}
                    </div>
                  </div>
                </motion.div>
              )}

              {resultVideo && (
                <motion.div
                  key="result"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-8"
                >
                  <div className="flex items-center justify-between bg-indigo-500/10 border border-indigo-500/20 p-6 rounded-3xl">
                    <div className="flex items-center gap-4 text-white">
                      <div className="w-12 h-12 rounded-2xl bg-indigo-500 flex items-center justify-center shadow-lg shadow-indigo-500/30">
                        <CheckCircle2 className="w-7 h-7" />
                      </div>
                      <div>
                        <p className="text-xl font-bold">Dubbing Successfully Completed</p>
                        <p className="text-indigo-400/80 font-medium text-sm">Your Telugu version is ready for download</p>
                      </div>
                    </div>
                    <button
                      onClick={reset}
                      className="secondary-button text-sm"
                    >
                      New Project
                    </button>
                  </div>

                  <div className="grid md:grid-cols-2 gap-8">
                    <div className="space-y-4">
                      <p className="text-sm font-bold uppercase tracking-widest text-text-muted px-2">Output Preview</p>
                      <div className="video-container border-2 border-indigo-500/30">
                        <video src={resultVideo} controls autoPlay className="w-full h-full" />
                      </div>
                    </div>

                    <div className="flex flex-col justify-center space-y-6">
                      <div className="p-8 rounded-3xl bg-white/5 border border-white/5 space-y-6">
                        <div className="space-y-2">
                          <h4 className="text-2xl font-bold">Ready for Export</h4>
                          <p className="text-text-muted">The final MP4 includes translated Telugu audio and optimized lip-syncing.</p>
                        </div>

                        <div className="grid gap-3">
                          <a
                            href={resultVideo}
                            download="dubbed_video_telugu.mp4"
                            className="primary-button text-xl py-5 no-underline"
                          >
                            <Download className="w-6 h-6" /> Download MP4
                          </a>
                          <button
                            onClick={reset}
                            className="secondary-button py-5"
                          >
                            <RefreshCw className="w-5 h-5" /> Process Another
                          </button>
                        </div>
                      </div>

                      <div className="flex items-center gap-3 p-4 px-6 rounded-2xl bg-white/5 text-sm text-text-muted">
                        <MonitorPlay className="w-5 h-5" />
                        <span>Optimized for web and social media sharing</span>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {error && (
              <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="flex items-center gap-4 p-5 mt-8 rounded-3xl bg-red-500/10 border border-red-500/20 text-red-400 mx-auto max-w-xl"
              >
                <AlertCircle className="w-6 h-6 flex-shrink-0" />
                <p className="font-medium">{error}</p>
              </motion.div>
            )}
          </main>
        </div>

        {/* Footer */}
        <footer className="px-12 py-8 bg-black/20 border-t border-white/5">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="text-sm text-text-muted flex items-center gap-4">
              <span>Privacy Policy</span>
              <span className="w-1 h-1 rounded-full bg-white/10" />
              <span>Terms of Service</span>
              <span className="w-1 h-1 rounded-full bg-white/10" />
              <span>OpenAI GPT-4o v1.0</span>
            </div>
            <div className="flex items-center gap-2 grayscale opacity-50 hover:opacity-100 transition-opacity">
              <span className="text-[10px] font-bold uppercase tracking-[2px] text-text-muted mr-2">Powered by</span>
              <img src="https://upload.wikimedia.org/wikipedia/commons/e/ef/Google_Translate_Icon.svg" alt="Google" className="h-5" />
              <span className="text-sm font-bold ml-2">OpenAI GPT-4o & Whisper</span>
            </div>
          </div>
        </footer>
      </motion.div>
    </div>
  );
}

export default App;
