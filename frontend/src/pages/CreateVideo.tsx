import { useState, useMemo, useEffect } from 'react';
import { Share2, Download, Lock, Sparkles, ArrowLeft, ChevronDown, Loader2 } from 'lucide-react';
import { useToast } from "@/hooks/use-toast";
import { useNavigate } from 'react-router-dom';
import { apiClient } from '@/services/api';
import { createVideoSessionForCurrentUser, getCurrentUserIdFromStorage } from '@/services/videoSessionService';
import ImageUploader from '../components/uploader/ImageUploader';
import PDFUploader from '../components/uploader/PDFUploader';
import type { PreparedFile } from '../types/upload';

// Session ID localStorage key (matches existing project pattern)
const SESSION_ID_KEY = 'currentSessionId';

enum VideoCategory {
  CONGRATULATION_VIDEO = "congratulation_video",
  EVENT_PROPAGATION_VIDEO = "event_propagation_video",
  COMPANY_INTRODUCTION_VIDEO = "company_introduction_video", 
  GENERAL_VIDEO = "general_video"
}

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
  task_id?: string;
  file_size?: number;
  elapsed_seconds?: number;
  veo3_inputs?: Record<string, unknown>;
  [k: string]: unknown;
}

const categoryOptions: Array<{ id: VideoCategory; label: string; icon?: React.ReactNode }> = [
  { 
    id: VideoCategory.CONGRATULATION_VIDEO, 
    label: 'Congratulations Video',
    icon: <span className="text-lg">🎉</span> 
  },
  { 
    id: VideoCategory.EVENT_PROPAGATION_VIDEO, 
    label: 'Event Propagation Video',
    icon: <span className="text-lg">📣</span> 
  },
  { 
    id: VideoCategory.COMPANY_INTRODUCTION_VIDEO, 
    label: 'Company Introduction Video',
    icon: <span className="text-lg">🏢</span> 
  },
  { 
    id: VideoCategory.GENERAL_VIDEO, 
    label: 'General Video',
    icon: <span className="text-lg">🎬</span> 
  }
];

// Global Loading Overlay Component
const GlobalLoader = ({ isVisible }: { isVisible: boolean }) => {
  if (!isVisible) return null;

  return (
    <div className="fixed inset-0 z-50 bg-arcade-dark/95 backdrop-blur-sm flex items-center justify-center">
      <div className="text-center">
        {/* Main loading animation */}
        <div className="relative mb-8">
          {/* Outer rotating ring */}
          <div className="w-32 h-32 border-4 border-gray-800 border-t-arcade-purple rounded-full animate-spin"></div>
          {/* Inner pulsing circle */}
          <div className="absolute inset-4 bg-arcade-purple/20 rounded-full animate-pulse flex items-center justify-center">
            <div className="text-4xl">🎬</div>
          </div>
        </div>
        
        {/* Loading text */}
        <div className="space-y-4">
          <h2 className="text-2xl font-bold text-white">
            Your Video is Processing
          </h2>
          <p className="text-gray-300 max-w-md mx-auto">
            We're creating your video with AI magic. This usually takes 1-2 minutes.
          </p>
          
          {/* Progress dots animation */}
          <div className="flex items-center justify-center space-x-1 mt-6">
            <div className="w-2 h-2 bg-arcade-purple rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
            <div className="w-2 h-2 bg-arcade-purple rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
            <div className="w-2 h-2 bg-arcade-purple rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
          </div>
        </div>
        
        {/* Background particles effect */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          {[...Array(6)].map((_, i) => (
            <div
              key={i}
              className="absolute bg-arcade-purple/10 rounded-full animate-pulse"
              style={{
                width: Math.random() * 100 + 50 + 'px',
                height: Math.random() * 100 + 50 + 'px',
                left: Math.random() * 100 + '%',
                top: Math.random() * 100 + '%',
                animationDelay: Math.random() * 2000 + 'ms',
                animationDuration: (Math.random() * 3 + 2) + 's',
              }}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

const CreateVideo = () => {
  const [videoIdea, setVideoIdea] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [isInitializing, setIsInitializing] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<VideoCategory>(VideoCategory.CONGRATULATION_VIDEO);
  const [uploadedImages, setUploadedImages] = useState<PreparedFile[]>([]);
  const [uploadedPDFs, setUploadedPDFs] = useState<PreparedFile[]>([]);
  const [imagesSkipped, setImagesSkipped] = useState(false);
  const [pdfsSkipped, setPdfsSkipped] = useState(false);
  const [editingImages, setEditingImages] = useState(false);
  const [editingPDFs, setEditingPDFs] = useState(false);
  const { toast } = useToast();
  const navigate = useNavigate();
  
  useEffect(() => {
    const initializeSession = async () => {
      try {
        setIsInitializing(true);
        
        const userId = getCurrentUserIdFromStorage();
        if (!userId) {
          toast({
            title: 'Cannot find the user',
            description: 'Please create a new account first. 😃',
            variant: 'destructive',
          });
          navigate('/');
          return;
        }
        
        await createVideoSessionForCurrentUser();
        
        toast({
          title: 'Created a new video session ready',
          description: 'Created a new video session ready. You can start creating your video now. 😊',
          duration: 2000,
        });
        
      } catch (error) {
        console.error('Failed to create video session:', error);
        toast({
          title: 'Failed to create video session',
          description: 'Failed to create video session, please refresh 🥹',
          variant: 'destructive',
        });
      } finally {
        setIsInitializing(false);
      }
    };

    initializeSession();
  }, []);

  // Progressive disclosure logic - Apple style with skip functionality
  const hasVideoIdea = videoIdea.trim().length > 0;
  const hasImages = uploadedImages.length > 0;
  const hasPDFs = uploadedPDFs.length > 0;
  const imageStepCompleted = (hasImages || imagesSkipped) && !editingImages;
  const pdfStepCompleted = (hasPDFs || pdfsSkipped) && !editingPDFs;
  
  const canShowImageUploader = hasVideoIdea;
  const canShowPDFUploader = hasVideoIdea && imageStepCompleted;
  const canShowCategory = hasVideoIdea && imageStepCompleted && pdfStepCompleted;
  
  const showImageUploader = canShowImageUploader && editingImages;
  const showPDFUploader = canShowPDFUploader && editingPDFs;

  const canCreate = useMemo(() => {
    return !!videoIdea.trim() && !!selectedCategory && imageStepCompleted && pdfStepCompleted && !isCreating && !isInitializing;
  }, [videoIdea, selectedCategory, imageStepCompleted, pdfStepCompleted, isCreating, isInitializing]);

  // Handler functions for skip actions
  const handleSkipImages = () => {
    setImagesSkipped(true);
    setEditingImages(false);
    if (hasVideoIdea && (hasImages || true)) {
      setEditingPDFs(true);
    }
    toast({
      title: "Images Skipped 🌠",
      description: "Proceeding without images. You can add them later if needed.",
      duration: 2000,
    });
  };

  const handleSkipPDFs = () => {
    setPdfsSkipped(true);
    setEditingPDFs(false);
    toast({
      title: "PDFs Skipped 📄",
      description: "Proceeding without PDF documents. You can add them later if needed.",
      duration: 2000,
    });
  };

  const handleImageChange = (files: PreparedFile[]) => {
    setUploadedImages(files);
    if (files.length > 0 && imagesSkipped) {
      setImagesSkipped(false);
    }
    console.log('Ready image files:', files);
  };

  const handlePDFChange = (files: PreparedFile[]) => {
    setUploadedPDFs(files);
    if (files.length > 0 && pdfsSkipped) {
      setPdfsSkipped(false);
    }
    console.log('Ready PDF files:', files);
  };

  const startVideoSession = async () => {
    const sessionId = window.localStorage.getItem(SESSION_ID_KEY);
    if (!sessionId) {
      toast({
        title: 'Session ID Missing 🙃',
        description: 'No session ID found. Please create or restore a session first.',
        variant: 'destructive',
      });
      return;
    }

    try {
      setIsCreating(true);

      const formData = new FormData();
      formData.append('user_prompt', videoIdea.trim());
      formData.append('category', selectedCategory);

      // Send request and wait for server response - this is where the long processing happens
      const resp = await apiClient.request(`/video-sessions/${encodeURIComponent(sessionId)}/start-processing`, {
        method: 'POST',
        body: formData,
        headers: {},
      }) as StartProcessingResponse;

      const status = resp?.status;
      const sid = (resp?.session_id ?? sessionId) as MaybeNumberString;
      
      if (status === 'completed' && sid) {
        toast({
          title: 'Success 😆',
          description: 'Video processing completed successfully.',
          duration: 3000,
        });

        // Navigate to workspace with session_id and pass complete response via state
        navigate(`/workspace/${encodeURIComponent(String(sid))}`, {
          state: { response: resp }
        });
      } else {
        const reason = resp?.message || 'Processing not completed yet.';
        toast({
          title: 'Start Failed 😨',
          description: String(reason),
          variant: 'destructive',
        });
      }
    } catch (err: unknown) {
      const message = (err instanceof Error ? err.message : null) || 'Request failed, please try again later.';
      toast({
        title: 'Start Failed 😨',
        description: message,
        variant: 'destructive',
      });
    } finally {
      setIsCreating(false);
    }
  };

  const handleCreate = () => {
    if (!videoIdea.trim()) {
      toast({
        title: "Please enter your video idea 💡",
        variant: "destructive",
      });
      return;
    }
    // Trigger the actual backend request
    startVideoSession();
  };

  const goBack = () => {
    navigate('/');
  };

  // Show loading screen while initializing
  if (isInitializing) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-arcade-dark">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-gray-800 border-t-arcade-purple rounded-full animate-spin mb-4"></div>
          <h2 className="text-xl font-bold text-white mb-2">Prepare for the create video...</h2>
          <p className="text-gray-400">Initializing session...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      {/* Global Loading Overlay */}
      <GlobalLoader isVisible={isCreating} />
      
      <div className="min-h-screen flex flex-col overflow-hidden bg-arcade-dark">
        <div className="flex-1 container mx-auto px-4 py-8 max-w-6xl">
          {/* Back button */}
          <button 
            onClick={goBack}
            className="flex items-center text-gray-400 hover:text-white mb-6 transition-colors"
            disabled={isCreating}
          >
            <ArrowLeft size={20} className="mr-2" />
            <span>Back to home</span>
          </button>
          
          {/* Icon at the top */}
          <div className="w-full flex justify-center mb-6">
            <div className="w-24 h-24 rounded-full bg-arcade-terminal flex items-center justify-center relative">
              <div className="absolute inset-0 rounded-full bg-arcade-purple opacity-20 blur-xl"></div>
              <div className="text-3xl">🎬</div>
            </div>
          </div>
          
          {/* Main heading */}
          <h1 className="text-4xl md:text-6xl font-bold text-white text-center mb-16 tracking-tight">
            Idea to video in seconds.
          </h1>
          
          {/* Video creation area */}
          <div className="bg-arcade-terminal/40 backdrop-blur-sm rounded-xl p-6 border border-gray-800 shadow-xl max-w-4xl mx-auto mb-8">
            <div className="mb-4">
              <h3 className="text-white text-lg font-semibold mb-2 flex items-center justify-center">
                <span className="text-2xl mr-2">💭</span>
                Your Video Idea
              </h3>
              <p className="text-gray-400 text-sm text-center">Describe what kind of video you want to create</p>
            </div>
            <textarea
              value={videoIdea}
              onChange={(e) => setVideoIdea(e.target.value)}
              placeholder="Describe your video idea..."
              className="w-full bg-arcade-terminal border border-gray-700 rounded-lg p-4 min-h-24 text-white focus:outline-none focus:ring-2 focus:ring-arcade-purple resize-none"
              disabled={isCreating}
            />
          </div>
          
          {/* Progressive Disclosure Sections */}
          <div className="max-w-4xl mx-auto space-y-6">
            
            {/* Step 1: Image Upload - Shows when video idea is entered */}
            <div className={`progressive-section ${canShowImageUploader ? 'visible' : 'hidden'}`}>
              {canShowImageUploader && (
                <div className="animate-slideDown hover-lift">
                  {(showImageUploader || editingImages) ? (
                    /* Upload Interface */
                    <div className="bg-arcade-terminal/40 backdrop-blur-sm rounded-xl border border-gray-800 shadow-xl overflow-hidden content-transition">
                      <ImageUploader
                        maxFiles={1}
                        maxFileSizeMB={10}
                        onChange={handleImageChange}
                      />
                      {/* Skip Option or Cancel Edit */}
                      <div className="px-6 pb-4 border-t border-gray-700 bg-arcade-terminal/20">
                        <div className="flex items-center justify-between pt-4">
                          {!editingImages ? (
                            <>
                              <span className="text-gray-400 text-sm">
                                Don't have an image? No problem!
                              </span>
                              <button
                                onClick={handleSkipImages}
                                disabled={isCreating}
                                className="text-gray-400 hover:text-white text-sm underline-offset-2 hover:underline transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                              >
                                Skip for now →
                              </button>
                            </>
                          ) : (
                            <>
                              <span className="text-gray-400 text-sm">
                                {uploadedImages.length > 0 ? 'Image uploaded' : 'Upload an image for your video'}
                              </span>
                              <div className="flex items-center space-x-3">
                                <button
                                  onClick={handleSkipImages}
                                  disabled={isCreating}
                                  className="text-gray-400 hover:text-white text-sm underline-offset-2 hover:underline transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                  Skip
                                </button>
                                <button
                                  onClick={() => setEditingImages(false)}
                                  disabled={isCreating}
                                  className="text-gray-400 hover:text-white text-sm underline-offset-2 hover:underline transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                  Cancel
                                </button>
                                {uploadedImages.length > 0 && (
                                  <button
                                    onClick={() => setEditingImages(false)}
                                    disabled={isCreating}
                                    className="bg-arcade-purple hover:bg-opacity-90 text-white rounded px-3 py-1.5 text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                  >
                                    Done
                                  </button>
                                )}
                              </div>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                  ) : (
                    /* Completion Status */
                    <div className="bg-arcade-terminal/40 backdrop-blur-sm rounded-xl p-4 border border-gray-800 shadow-xl content-transition">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <span className="text-2xl">📸</span>
                          <div>
                            <h4 className="text-white font-medium">
                              {imagesSkipped ? 'Image Skipped' : uploadedImages.length > 0 ? 'Image Added' : 'No Image'}
                            </h4>
                            <p className="text-gray-400 text-sm">
                              {imagesSkipped ? 'You can add an image later if needed' : uploadedImages.length > 0 ? 'Image ready for video creation' : 'Upload an image to enhance your video'}
                            </p>
                          </div>
                        </div>
                        {!imagesSkipped && (
                          <button
                            onClick={() => setEditingImages(true)}
                            disabled={isCreating}
                            className="text-gray-400 hover:text-white text-sm underline-offset-2 hover:underline transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            Edit
                          </button>
                        )}
                        {imagesSkipped && (
                          <button
                            onClick={() => setImagesSkipped(false)}
                            disabled={isCreating}
                            className="text-gray-400 hover:text-white text-sm underline-offset-2 hover:underline transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            Add Image
                          </button>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Step 2: PDF Upload - Shows when images are uploaded */}
            <div className={`progressive-section ${canShowPDFUploader ? 'visible' : 'hidden'}`}>
              {canShowPDFUploader && (
                <div className="animate-slideDown hover-lift">
                  {showPDFUploader ? (
                    /* Upload Interface */
                    <div className="bg-arcade-terminal/40 backdrop-blur-sm rounded-xl border border-gray-800 shadow-xl overflow-hidden content-transition">
                      <PDFUploader
                        maxFiles={10}
                        maxFileSizeMB={10}
                        onChange={handlePDFChange}
                      />
                      {/* Skip Option or Cancel Edit */}
                      <div className="px-6 pb-4 border-t border-gray-700 bg-arcade-terminal/20">
                        <div className="flex items-center justify-between pt-4">
                          {!editingPDFs ? (
                            <>
                              <span className="text-gray-400 text-sm">
                                Don't have PDF documents? You can continue without them!
                              </span>
                              <button
                                onClick={handleSkipPDFs}
                                disabled={isCreating}
                                className="text-gray-400 hover:text-white text-sm underline-offset-2 hover:underline transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                              >
                                Skip for now →
                              </button>
                            </>
                          ) : (
                            <>
                              <span className="text-gray-400 text-sm">
                                {uploadedPDFs.length > 0 ? `${uploadedPDFs.length} PDF(s) uploaded` : 'Upload PDF documents for your video'}
                              </span>
                              <div className="flex items-center space-x-3">
                                <button
                                  onClick={handleSkipPDFs}
                                  disabled={isCreating}
                                  className="text-gray-400 hover:text-white text-sm underline-offset-2 hover:underline transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                  Skip
                                </button>
                                <button
                                  onClick={() => setEditingPDFs(false)}
                                  disabled={isCreating}
                                  className="text-gray-400 hover:text-white text-sm underline-offset-2 hover:underline transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                  Cancel
                                </button>
                                {uploadedPDFs.length > 0 && (
                                  <button
                                    onClick={() => setEditingPDFs(false)}
                                    disabled={isCreating}
                                    className="bg-arcade-purple hover:bg-opacity-90 text-white rounded px-3 py-1.5 text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                                  >
                                    Done
                                  </button>
                                )}
                              </div>
                            </>
                          )}
                        </div>
                      </div>
                    </div>
                  ) : (
                    /* Completion Status */
                    <div className="bg-arcade-terminal/40 backdrop-blur-sm rounded-xl p-4 border border-gray-800 shadow-xl content-transition">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <span className="text-2xl">📄</span>
                          <div>
                            <h4 className="text-white font-medium">
                              {pdfsSkipped ? 'PDFs Skipped' : `${uploadedPDFs.length} PDFs Added`}
                            </h4>
                            <p className="text-gray-400 text-sm">
                              {pdfsSkipped ? 'You can add PDF documents later if needed' : 'PDF documents ready for video creation'}
                            </p>
                          </div>
                        </div>
                        {!pdfsSkipped && (
                          <button
                            onClick={() => setEditingPDFs(true)}
                            disabled={isCreating}
                            className="text-gray-400 hover:text-white text-sm underline-offset-2 hover:underline transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            Edit
                          </button>
                        )}
                        {pdfsSkipped && (
                          <button
                            onClick={() => setPdfsSkipped(false)}
                            disabled={isCreating}
                            className="text-gray-400 hover:text-white text-sm underline-offset-2 hover:underline transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                          >
                            Add PDFs
                          </button>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Step 3: Category Selection - Shows when PDFs are uploaded */}
            <div className={`progressive-section ${canShowCategory ? 'visible' : 'hidden'}`}>
              {canShowCategory && (
                <div className="animate-slideDown hover-lift">
                  <div className="bg-arcade-terminal/40 backdrop-blur-sm rounded-xl p-6 border border-gray-800 shadow-xl">
                    <div className="mb-4">
                      <h3 className="text-white text-lg font-semibold mb-2 flex items-center">
                        <span className="text-2xl mr-2">🎯</span>
                        Choose Video Category
                      </h3>
                      <p className="text-gray-400 text-sm">Select the type of video you want to create</p>
                    </div>
                    
                    <div className="flex flex-wrap gap-3 justify-center">
                      {categoryOptions.map((opt) => (
                        <button
                          key={opt.id}
                          onClick={() => setSelectedCategory(opt.id)}
                          disabled={isCreating}
                          className={`flex items-center space-x-2 px-4 py-3 rounded-xl border transition-all hover-lift disabled:opacity-50 disabled:cursor-not-allowed ${
                            selectedCategory === opt.id
                              ? 'bg-arcade-purple/20 border-arcade-purple text-white transform scale-105'
                              : 'bg-arcade-terminal/40 border-gray-700 text-gray-300 hover:bg-arcade-terminal/60 hover:border-gray-600'
                          }`}
                        >
                          {opt.icon ? <span>{opt.icon}</span> : null}
                          <span>{opt.label}</span>
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Next Steps Indicator */}
            {!canShowCategory && !isCreating && (
              <div className="text-center py-8">
                <div className="flex items-center justify-center space-x-2 text-gray-500 text-sm">
                  {!hasVideoIdea && (
                    <>
                      <span className="opacity-70">Enter your video idea above to continue</span>
                      <ChevronDown className="animate-gentle-bounce text-arcade-purple/60" size={16} />
                    </>
                  )}
                  {hasVideoIdea && !imageStepCompleted && (
                    <>
                      <span className="opacity-70">Upload an image or skip to continue</span>
                      <ChevronDown className="animate-gentle-bounce text-arcade-purple/60" size={16} />
                    </>
                  )}
                  {hasVideoIdea && imageStepCompleted && !pdfStepCompleted && (
                    <>
                      <span className="opacity-70">Upload PDF documents or skip to continue</span>
                      <ChevronDown className="animate-gentle-bounce text-arcade-purple/60" size={16} />
                    </>
                  )}
                </div>
              </div>
            )}
          </div>
          
          {/* Create Button - Only shown when all components are satisfied */}
          {canCreate && (
            <div className="max-w-4xl mx-auto mt-8 mb-16">
              <div className="flex justify-center">
                <button 
                  onClick={handleCreate}
                  disabled={isCreating}
                  className="bg-arcade-purple hover:bg-opacity-90 text-white rounded-lg px-8 py-3 flex items-center font-medium text-lg disabled:opacity-70 disabled:cursor-not-allowed shadow-xl transform hover:scale-105 transition-all"
                >
                  {isCreating ? (
                    <>
                      <Loader2 size={20} className="mr-3 animate-spin" />
                      Creating Video...
                    </>
                  ) : (
                    <>
                      <Sparkles size={20} className="mr-3" />
                      Create Video
                    </>
                  )}
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
};

export default CreateVideo;
