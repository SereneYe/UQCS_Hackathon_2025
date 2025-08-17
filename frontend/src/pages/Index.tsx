
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '@/components/Header';
import Terminal from '@/components/Terminal';
import EmailForm from '@/components/EmailForm';
import FeatureCard from '@/components/FeatureCard';
import { MessageSquare, Code, Play, User, Video, FileText, Sparkles } from 'lucide-react';
import { getCurrentUserIdFromStorage } from '@/services/videoSessionService';

const Index = () => {
  const [loaded, setLoaded] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    // Add small delay before starting animations
    const timer = setTimeout(() => {
      setLoaded(true);
    }, 100);

    return () => clearTimeout(timer);
  }, []);

  const handleUserAvatarClick = () => {
    const userId = getCurrentUserIdFromStorage();
    if (userId) {
      navigate('/my-videos');
    } else {
      // If no user ID, could navigate to create account or show a toast
      // For now, navigate to create-video as suggested in issue
      navigate('/create-video');
    }
  };

  const userId = getCurrentUserIdFromStorage();

  return (
    <div className="min-h-screen flex flex-col overflow-hidden bg-arcade-dark">
      <div className="flex-1 container mx-auto px-4 py-8 max-w-6xl">
        {/* User Avatar Button */}
        <div className="absolute top-6 right-6">
          <button
            onClick={handleUserAvatarClick}
            className={`p-3 rounded-full transition-all duration-300 ${
              userId 
                ? ' hover:bg-arcade-purple/80 hover:scale-120 text-white'
                : 'bg-gray-600 text-gray-400 cursor-not-allowed'
            } backdrop-blur-sm border border-gray-800 shadow-lg`}
            disabled={!userId}
            title={userId ? 'My Videos' : 'Please create an account first'}
          >
            <User size={25} />
          </button>
        </div>

        <Header />
        
        <div className={`mt-16 mb-12 text-center transition-opacity duration-700 ${loaded ? 'opacity-100' : 'opacity-0'}`}>
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6">
            <span className="gradient-text">Create Videos With Just a Prompt</span>
          </h2>
          <p className="text-lg text-gray-300 max-w-2xl mx-auto">
            ✨ Type a prompt, get your stunning video instantly ✨
          </p>
        </div>
        
        <Terminal />
        
        <EmailForm />
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto mt-16 mb-16">
          <FeatureCard
              icon={<Sparkles size={28} />}
              title="AI-Powered Generation"
              description="Advanced AI analyzes your content and generates professional video"
              delay="delay-100"
          />
          
          <FeatureCard
              icon={<FileText size={28} />}
              title="Multi-Format Support"
              description="Upload multimodal documents to enhance your video creation"
              delay="delay-300"
          />
          
          <FeatureCard
              icon={<Video size={28} />}
              title="Professional Videos"
              description="Create cinematic videos for various scenarios"
              delay="delay-500"
          />
        </div>
      </div>
      
      <footer className="py-6 border-t border-gray-800 text-center text-sm text-gray-500">
        <p>© UQCS Hackathon 2025 - Team Names Are Cringe</p>
      </footer>
    </div>
  );
};

export default Index;
