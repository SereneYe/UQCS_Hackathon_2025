import { useState, useMemo } from 'react';
import { Share2, Download, Lock, Sparkles, ArrowLeft, ChevronDown } from 'lucide-react';
import { useToast } from "@/hooks/use-toast";
import { useNavigate } from 'react-router-dom';
import { apiClient } from '@/services/api';
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

const CreateVideo = () => {
  const [videoIdea, setVideoIdea] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<VideoCategory>(VideoCategory.CONGRATULATION_VIDEO);
  const [uploadedImages, setUploadedImages] = useState<PreparedFile[]>([]);
  const [uploadedPDFs, setUploadedPDFs] = useState<PreparedFile[]>([]);
  const [imagesSkipped, setImagesSkipped] = useState(false);
  const [pdfsSkipped, setPdfsSkipped] = useState(false);
  const [editingImages, setEditingImages] = useState(false);
  const [editingPDFs, setEditingPDFs] = useState(false);
  const { toast } = useToast();
  const navigate = useNavigate();

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
    return !!videoIdea.trim() && !!selectedCategory && imageStepCompleted && pdfStepCompleted && !isCreating;
  }, [videoIdea, selectedCategory, imageStepCompleted, pdfStepCompleted, isCreating]);

  // Handler functions for skip actions
  const handleSkipImages = () => {
    setImagesSkipped(true);
    toast({
      title: "Images Skipped",
      description: "Proceeding without images. You can add them later if needed.",
      duration: 2000,
    });
  };

  const handleSkipPDFs = () => {
    setPdfsSkipped(true);
    toast({
      title: "PDFs Skipped", 
      description: "Proceeding without PDF documents. You can add them later if needed.",
      duration: 2000,
    });
  };

  // Reset skip states when files are added and exit editing mode
  const handleImageChange = (files: PreparedFile[]) => {
    const previousCount = uploadedImages.length;
    setUploadedImages(files);
    if (files.length > 0 && imagesSkipped) {
      setImagesSkipped(false);
    }
    // Don't auto-exit editing mode - let user manually close with "Done" button
    console.log('Ready image files:', files);
  };

  const handlePDFChange = (files: PreparedFile[]) => {
    setUploadedPDFs(files);
    if (files.length > 0 && pdfsSkipped) {
      setPdfsSkipped(false);
    }
    // Don't auto-exit editing mode - let user manually close with "Done" button
    console.log('Ready PDF files:', files);
  };

  const startVideoSession = async () => {
    const sessionId = window.localStorage.getItem(SESSION_ID_KEY);
    if (!sessionId) {
      toast({
        title: 'Session ID Missing',
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

      // Use apiClient.request directly to send FormData
      await apiClient.request(`/video-sessions/${encodeURIComponent(sessionId)}/start-processing`, {
        method: 'POST',
        body: formData,
        headers: {
        },
      });

      toast({
        title: 'Success',
        description: 'Video session processing has started.',
        duration: 3000, // Auto-dismiss after 3 seconds
      });

      // Optional: navigate to workspace or stay on current page
      // navigate('/workspace');

    } catch (err: unknown) {
      const message =
        (err instanceof Error ? err.message : null) ||
        'Request failed, please try again later.';
      toast({
        title: 'Start Failed',
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
        title: "Please enter your video idea",
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

  return (
    <div className="min-h-screen flex flex-col overflow-hidden bg-arcade-dark">
      <div className="flex-1 container mx-auto px-4 py-8 max-w-6xl">
        {/* Back button */}
        <button 
          onClick={goBack}
          className="flex items-center text-gray-400 hover:text-white mb-6 transition-colors"
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
                              className="text-gray-400 hover:text-white text-sm underline-offset-2 hover:underline transition-colors"
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
                                onClick={() => setEditingImages(false)}
                                className="text-gray-400 hover:text-white text-sm underline-offset-2 hover:underline transition-colors"
                              >
                                Cancel
                              </button>
                              {uploadedImages.length > 0 && (
                                <button
                                  onClick={() => setEditingImages(false)}
                                  className="bg-arcade-purple hover:bg-opacity-90 text-white rounded px-3 py-1.5 text-sm font-medium transition-colors"
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
                          className="text-gray-400 hover:text-white text-sm underline-offset-2 hover:underline transition-colors"
                        >
                          Edit
                        </button>
                      )}
                      {imagesSkipped && (
                        <button
                          onClick={() => setImagesSkipped(false)}
                          className="text-gray-400 hover:text-white text-sm underline-offset-2 hover:underline transition-colors"
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
                              className="text-gray-400 hover:text-white text-sm underline-offset-2 hover:underline transition-colors"
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
                                onClick={() => setEditingPDFs(false)}
                                className="text-gray-400 hover:text-white text-sm underline-offset-2 hover:underline transition-colors"
                              >
                                Cancel
                              </button>
                              {uploadedPDFs.length > 0 && (
                                <button
                                  onClick={() => setEditingPDFs(false)}
                                  className="bg-arcade-purple hover:bg-opacity-90 text-white rounded px-3 py-1.5 text-sm font-medium transition-colors"
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
                          className="text-gray-400 hover:text-white text-sm underline-offset-2 hover:underline transition-colors"
                        >
                          Edit
                        </button>
                      )}
                      {pdfsSkipped && (
                        <button
                          onClick={() => setPdfsSkipped(false)}
                          className="text-gray-400 hover:text-white text-sm underline-offset-2 hover:underline transition-colors"
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
                        className={`flex items-center space-x-2 px-4 py-3 rounded-xl border transition-all hover-lift ${
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
          {!canShowCategory && (
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
                className="bg-arcade-purple hover:bg-opacity-90 text-white rounded-lg px-8 py-3 flex items-center font-medium text-lg disabled:opacity-70 shadow-xl transform hover:scale-105 transition-all"
              >
                <Sparkles size={20} className="mr-3" />
                {isCreating ? 'Creating Video...' : 'Create Video'}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CreateVideo;
