
import { useState, useEffect, useMemo } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import { useToast } from "@/hooks/use-toast";
import {
  ArrowLeft, Settings, Code, Share, Maximize2, RefreshCw, Send
} from 'lucide-react';

type MaybeNumberString = number | string;

interface StartProcessingResponse {
  message?: string;
  session_id?: MaybeNumberString;
  status?: string;
  user_prompt?: string;
  category?: string;
  ai_processing?: {
    session_id?: MaybeNumberString;
    status?: string;
    images?: string[];
    prompts?: {
      video_prompt?: string;
      audio_prompt?: string;
    };
    user_prompt?: string;
    category?: string;
    pdfs?: Array<{ url: string; title?: string }> | string[];
  };
  output_video_path?: string;
  video_url?: string;
  [k: string]: unknown;
}

const categoryLabelMap: Record<string, string> = {
  congratulation_video: 'Congratulations Video',
  event_propagation_video: 'Event Propagation Video',
  company_introduction_video: 'Company Introduction Video',
  general_video: 'General Video',
};

const isPdfObjectArray = (v: unknown): v is Array<{ url: string; title?: string }> =>
  Array.isArray(v) && v.every(i => typeof i === 'object' && i !== null && 'url' in i);

const isStringArray = (v: unknown): v is string[] =>
  Array.isArray(v) && v.every(i => typeof i === 'string');

const VideoWorkspace = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const { slug } = useParams<{ slug: string }>();
  const location = useLocation() as { state?: { response?: StartProcessingResponse } };

  // Get response from route state; if not available, use empty object as fallback
  const resp: StartProcessingResponse | undefined = location.state?.response;

  const [prompt, setPrompt] = useState('');
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Extract key information from response
  const sessionId = useMemo(() => String(resp?.session_id ?? slug ?? ''), [resp?.session_id, slug]);
  const category = useMemo(() => {
    const raw = (resp?.category || resp?.ai_processing?.category || 'general_video') as string;
    return raw;
  }, [resp?.category, resp?.ai_processing?.category]);
  const categoryLabel = categoryLabelMap[category] ?? 'General Video';

  const userPromptDisplayed = useMemo(() => {
    return resp?.user_prompt || resp?.ai_processing?.user_prompt || '';
  }, [resp?.user_prompt, resp?.ai_processing?.user_prompt]);

  const videoUrl = resp?.video_url;

  const aiVideoPrompt = resp?.ai_processing?.prompts?.video_prompt;
  const aiAudioPrompt = resp?.ai_processing?.prompts?.audio_prompt;

  const images: string[] = useMemo(() => {
    return resp?.ai_processing?.images?.filter(Boolean) ?? [];
  }, [resp?.ai_processing?.images]);

  // Handle different PDF field formats
  const pdfList: Array<{ url: string; title?: string }> = useMemo(() => {
    const pdfs = resp?.ai_processing?.pdfs as unknown;
    if (isPdfObjectArray(pdfs)) return pdfs;
    if (isStringArray(pdfs)) return pdfs.map((url) => ({ url, title: undefined }));
    // Also check for pdfs or pdf_urls at top level
    const fallback = (resp as Record<string, unknown>)?.pdfs ?? (resp as Record<string, unknown>)?.pdf_urls;
    if (isPdfObjectArray(fallback)) return fallback;
    if (isStringArray(fallback)) return fallback.map((url) => ({ url, title: undefined }));
    return [];
  }, [resp]);

  useEffect(() => {
    if (!sessionId) {
      toast({
        title: 'Missing Session',
        description: 'No session id found in the route.',
        variant: 'destructive',
      });
    }
  }, [sessionId, toast]);

  const handleSubmitPrompt = () => {
    if (!prompt.trim()) {
      toast({
        title: "Please enter a prompt",
        variant: "destructive",
      });
      return;
    }
    // Future: send new instruction and refresh
    toast({ title: 'Prompt sent', description: 'We will update your video shortly.' });
    setPrompt('');
  };

  const handleShare = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      toast({
        title: "Share link copied!",
        description: "video link has been copied to your clipboard.",
      });
    } catch {
      toast({
        title: "Copy failed",
        description: "Please copy the URL from the address bar.",
        variant: "destructive",
      });
    }
  };

  const toggleFullscreen = () => setIsFullscreen(!isFullscreen);

  const handleRefresh = () => {
    toast({ title: "Refreshing video..." });
    setTimeout(() => {
      toast({ title: "video refreshed!" });
    }, 800);
  };

  const backToCreate = () => navigate('/create-video');

  return (
    <div className="flex flex-col h-screen bg-arcade-dark">
      {/* Header Bar */}
      <header className="bg-black border-b border-gray-800 p-3 flex items-center justify-between">
        <div className="flex items-center">
          <button
            onClick={backToCreate}
            className="text-gray-300 hover:text-white flex items-center mr-4"
          >
            <ArrowLeft size={20} className="mr-1" />
            <span>Back</span>
          </button>
          <div className="flex items-center">
            <div className="w-6 h-6 bg-arcade-purple rounded-sm flex items-center justify-center mr-2">
              <span className="text-xs">🎮</span>
            </div>
            <h1 className="text-white font-semibold">Video Workspace</h1>
            <span className="text-gray-500 text-xs ml-2">#{sessionId}</span>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={handleShare}
            className="flex items-center px-3 py-1.5 text-white bg-arcade-purple hover:bg-opacity-90 rounded-md"
          >
            <Share size={18} className="mr-1.5" />
            <span>Share Your Video</span>
          </button>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Left Panel - Conversation and Details (1/4 width) */}
        <div className="w-1/4 min-w-[320px] flex flex-col bg-gray-900 border-r border-gray-800">
          {/* Category Title */}
          <div className="px-4 py-3 border-b border-gray-800">
            <h2 className="text-white text-lg font-semibold">{categoryLabel}</h2>
            {userPromptDisplayed ? (
              <p className="text-gray-300 text-sm mt-1 break-words">
                {userPromptDisplayed}
              </p>
            ) : null}
          </div>

          {/* AI Prompts Summary */}
          {(aiVideoPrompt || aiAudioPrompt) && (
            <div className="p-4 border-b border-gray-800 text-gray-300 space-y-1">
              {aiVideoPrompt && (
                <div>
                  <div className="text-xs uppercase tracking-wide text-gray-400 mb-0.5">Video Prompt</div>
                  <div className="text-sm">{aiVideoPrompt}</div>
                </div>
              )}
              {aiAudioPrompt && (
                <div>
                  <div className="text-xs uppercase tracking-wide text-gray-400 mt-2 mb-0.5">Audio Prompt</div>
                  <div className="text-sm">{aiAudioPrompt}</div>
                </div>
              )}
            </div>
          )}

          {/* Images Preview */}
          {images.length > 0 && (
            <div className="p-4 border-b border-gray-800">
              <div className="text-white font-medium mb-2">Image Previews</div>
              <div className="grid grid-cols-2 gap-2">
                {images.map((url, idx) => (
                  <div key={`${url}-${idx}`} className="rounded overflow-hidden bg-black/30 border border-gray-800">
                    <img src={url} alt={`img-${idx}`} className="w-full h-24 object-cover" />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* PDFs Preview (if any) */}
          {pdfList.length > 0 && (
            <div className="p-4 border-b border-gray-800">
              <div className="text-white font-medium mb-2">PDF Documents</div>
              <div className="space-y-2">
                {pdfList.map((item, idx) => {
                  const title = item.title || `Document ${idx + 1}`;
                  return (
                    <a
                      key={`${item.url}-${idx}`}
                      href={item.url}
                      target="_blank"
                      rel="noreferrer"
                      className="block bg-black/30 border border-gray-800 rounded p-2 hover:bg-black/50 transition-colors"
                      title={title}
                    >
                      <div className="text-sm text-gray-200 truncate">{title}</div>
                      <div className="text-xs text-gray-500 truncate">{item.url}</div>
                    </a>
                  );
                })}
              </div>
            </div>
          )}

          {/* Conversation Area */}
          <div className="flex-1 p-4 overflow-y-auto">
            <div className="bg-black/30 rounded-lg p-4 text-gray-300">
              <p>
                {videoUrl
                  ? "Your video is ready. Use the panel on the right to preview it."
                  : "We are preparing your video preview. Please wait or try refresh."}
              </p>
            </div>
          </div>
        </div>

        {/* Right Panel - Video Preview (3/4 width) */}
        <div className="w-3/4 bg-black relative flex items-center justify-center">
          <div className={`w-full h-full ${isFullscreen ? 'p-0' : 'p-6'}`}>
            {videoUrl ? (
              <div className="w-full h-full">
                <video
                  src={videoUrl}
                  controls
                  className="w-full h-full rounded-lg bg-black object-contain"
                />
              </div>
            ) : (
              <div className="w-full h-full flex items-center justify-center text-gray-400">
                No video available yet.
              </div>
            )}
          </div>

          {/* Controls */}
          <div className="absolute top-4 right-4 flex space-x-2">
            <button
              onClick={toggleFullscreen}
              className="bg-black/50 p-2 rounded-md text-white hover:bg-black/80"
            >
              <Maximize2 size={16} />
            </button>
            <button
              onClick={handleRefresh}
              className="bg-black/50 p-2 rounded-md text-white hover:bg-black/80"
            >
              <RefreshCw size={16} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VideoWorkspace;
