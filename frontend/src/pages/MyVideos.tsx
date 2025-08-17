import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToast } from "@/hooks/use-toast";
import { ArrowLeft, Play, Calendar, User, ExternalLink } from 'lucide-react';
import { apiClient } from '@/services/api';

interface VideoSession {
  id: number;
  user_id: number;
  session_name?: string;
  user_prompt?: string;
  category?: string;
  status: string;
  created_at: string;
  updated_at?: string;
  video_url?: string;
  output_video_path?: string;
}

interface VideoSessionList {
  sessions: VideoSession[];
  total: number;
  page: number;
  per_page: number;
}

const categoryLabelMap: Record<string, string> = {
  congratulation_video: 'Congratulations Video',
  event_propagation_video: 'Event Propagation Video',
  company_introduction_video: 'Company Introduction Video',
  general_video: 'General Video',
};

const statusColorMap: Record<string, string> = {
  completed: 'bg-green-500',
  processing: 'bg-yellow-500',
  failed: 'bg-red-500',
  pending: 'bg-gray-500',
};

const MyVideos = () => {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [sessions, setSessions] = useState<VideoSession[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchUserVideos();
  }, []);

  const fetchUserVideos = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const userId = localStorage.getItem('currentUserId');
      if (!userId) {
        setError('No user found. Please sign in first.');
        return;
      }

      const response = await apiClient.get<VideoSessionList>(
        `/video-sessions/?user_id=${encodeURIComponent(userId)}`
      );

      setSessions(response.sessions || []);
    } catch (err) {
      console.error('Failed to fetch user videos:', err);
      setError('Failed to load your videos. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleVideoClick = (session: VideoSession) => {
    if (!session.video_url) {
      toast({
        title: 'Video not ready',
        description: 'This video is still processing or has no URL available.',
        variant: 'destructive',
      });
      return;
    }

    // Open video URL in new tab/window for full-screen viewing
    window.open(session.video_url, '_blank', 'noopener,noreferrer');
  };

  const handleRetry = () => {
    fetchUserVideos();
  };

  const goBack = () => {
    navigate('/');
  };

  const goToCreateVideo = () => {
    navigate('/create-video');
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-arcade-dark">
        <div className="container mx-auto px-4 py-8 max-w-6xl">
          {/* Header */}
          <div className="flex items-center mb-8">
            <button 
              onClick={goBack}
              className="flex items-center text-gray-400 hover:text-white mr-6 transition-colors"
            >
              <ArrowLeft size={20} className="mr-2" />
              <span>Back to home</span>
            </button>
            <h1 className="text-3xl font-bold text-white">My Videos</h1>
          </div>

          {/* Loading skeleton */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, index) => (
              <div key={index} className="bg-arcade-terminal/40 backdrop-blur-sm rounded-xl border border-gray-800 overflow-hidden">
                <div className="aspect-video bg-gray-700 animate-pulse"></div>
                <div className="p-4 space-y-2">
                  <div className="h-4 bg-gray-700 rounded animate-pulse"></div>
                  <div className="h-3 bg-gray-700 rounded w-2/3 animate-pulse"></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="min-h-screen bg-arcade-dark">
        <div className="container mx-auto px-4 py-8 max-w-6xl">
          {/* Header */}
          <div className="flex items-center mb-8">
            <button 
              onClick={goBack}
              className="flex items-center text-gray-400 hover:text-white mr-6 transition-colors"
            >
              <ArrowLeft size={20} className="mr-2" />
              <span>Back to home</span>
            </button>
            <h1 className="text-3xl font-bold text-white">My Videos</h1>
          </div>

          {/* Error message */}
          <div className="flex flex-col items-center justify-center min-h-[400px] text-center">
            <div className="text-red-400 text-lg mb-4">{error}</div>
            <button
              onClick={handleRetry}
              className="bg-arcade-purple hover:bg-opacity-90 text-white rounded-lg px-6 py-3 font-medium transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-arcade-dark">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center">
            <button 
              onClick={goBack}
              className="flex items-center text-gray-400 hover:text-white mr-6 transition-colors"
            >
              <ArrowLeft size={20} className="mr-2" />
              <span>Back to home</span>
            </button>
            <h1 className="text-3xl font-bold text-white">My Videos</h1>
            <span className="text-gray-400 text-sm ml-4">({sessions.length} videos)</span>
          </div>
          
          <button
            onClick={goToCreateVideo}
            className="bg-arcade-purple hover:bg-opacity-90 text-white rounded-lg px-4 py-2 font-medium transition-colors"
          >
            Create New Video
          </button>
        </div>

        {/* Empty state */}
        {sessions.length === 0 ? (
          <div className="flex flex-col items-center justify-center min-h-[400px] text-center">
            <div className="w-24 h-24 rounded-full bg-arcade-terminal flex items-center justify-center mb-6">
              <span className="text-4xl">🎬</span>
            </div>
            <h2 className="text-2xl font-bold text-white mb-4">No videos yet</h2>
            <p className="text-gray-400 mb-6 max-w-md">
              You haven't created any videos yet. Start by creating your first video!
            </p>
            <button
              onClick={goToCreateVideo}
              className="bg-arcade-purple hover:bg-opacity-90 text-white rounded-lg px-6 py-3 font-medium transition-colors"
            >
              Create Your First Video
            </button>
          </div>
        ) : (
          /* Video Grid */
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sessions.map((session) => (
              <div
                key={session.id}
                className="bg-arcade-terminal/40 backdrop-blur-sm rounded-xl border border-gray-800 overflow-hidden hover:scale-105 hover:shadow-xl transition-all duration-300 cursor-pointer group"
                onClick={() => handleVideoClick(session)}
              >
                {/* Video Preview */}
                <div className="aspect-video bg-black relative overflow-hidden">
                  {session.video_url ? (
                    <>
                      <video
                        src={session.video_url}
                        className="w-full h-full object-cover"
                        muted
                        preload="metadata"
                      />
                      {/* Play overlay */}
                      <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-center justify-center">
                        <div className="bg-arcade-purple rounded-full p-4">
                          <ExternalLink size={24} className="text-white" />
                        </div>
                      </div>
                      {/* Status indicator */}
                      <div className="absolute top-2 right-2">
                        <div className={`w-3 h-3 rounded-full ${statusColorMap[session.status] || statusColorMap.pending}`}></div>
                      </div>
                    </>
                  ) : (
                    /* No video placeholder */
                    <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-gray-800 to-gray-900">
                      <div className="text-center">
                        <Play size={32} className="text-gray-500 mx-auto mb-2" />
                        <p className="text-gray-500 text-sm">
                          {session.status === 'processing' ? 'Processing...' : 'No video available'}
                        </p>
                      </div>
                    </div>
                  )}
                </div>

                {/* Card Content */}
                <div className="p-4">
                  {/* Title */}
                  <h3 className="text-white font-semibold mb-2 line-clamp-2">
                    {session.session_name || session.user_prompt || 'Untitled Video'}
                  </h3>

                  {/* Category */}
                  {session.category && (
                    <div className="mb-2">
                      <span className="text-xs bg-arcade-purple/20 text-arcade-purple px-2 py-1 rounded-full">
                        {categoryLabelMap[session.category] || session.category}
                      </span>
                    </div>
                  )}

                  {/* Meta info */}
                  <div className="flex items-center justify-between text-gray-400 text-sm">
                    <div className="flex items-center">
                      <Calendar size={14} className="mr-1" />
                      <span>{new Date(session.created_at).toLocaleDateString()}</span>
                    </div>
                    <div className="flex items-center">
                      <div className={`w-2 h-2 rounded-full mr-2 ${statusColorMap[session.status] || statusColorMap.pending}`}></div>
                      <span className="capitalize">{session.status}</span>
                    </div>
                  </div>

                  {/* User prompt preview */}
                  {session.user_prompt && (
                    <p className="text-gray-500 text-xs mt-2 line-clamp-2">
                      {session.user_prompt}
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default MyVideos;