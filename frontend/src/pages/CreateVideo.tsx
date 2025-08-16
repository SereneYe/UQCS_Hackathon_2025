
import { useState } from 'react';
import { Share2, Download, Lock, Sparkles, ArrowLeft } from 'lucide-react';
import { useToast } from "@/hooks/use-toast";
import { useNavigate } from 'react-router-dom';
import FileUploader from '../components/uploader/FileUploader';
import type { PreparedFile } from '../types/upload';

const videoCategories = [
  { id: 'rpg', name: 'RPG Adventure', icon: <span className="text-lg">🗡️</span> },
  { id: 'strategy', name: 'Strategy', icon: <span className="text-lg">🎯</span> },
  { id: 'puzzle', name: 'Puzzle video', icon: <span className="text-lg">🧩</span> },
  { id: 'open-world', name: 'Open World', icon: <span className="text-lg">🌎</span> },
  { id: 'action', name: 'Action', icon: <span className="text-lg">⚡</span> },
];

const CreateVideo = () => {
  const [videoIdea, setVideoIdea] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [uploadedFiles, setUploadedFiles] = useState<PreparedFile[]>([]);
  const { toast } = useToast();
  const navigate = useNavigate();

  const handleCreate = () => {
    if (!videoIdea.trim()) {
      toast({
        title: "Please describe your video idea",
        variant: "destructive",
      });
      return;
    }
    
    setIsCreating(true);
    
    // Simulate creation and redirect to workspace
    setTimeout(() => {
      toast({
        title: "Success!",
        description: "Your video is being generated.",
      });
      setIsCreating(false);
      navigate('/workspace');
    }, 1500);
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
            <div className="text-3xl">🎮</div>
          </div>
        </div>
        
        {/* Main heading */}
        <h1 className="text-4xl md:text-6xl font-bold text-white text-center mb-16 tracking-tight">
          Idea to video in seconds.
        </h1>
        
        {/* Video creation area */}
        <div className="bg-arcade-terminal/40 backdrop-blur-sm rounded-xl p-6 border border-gray-800 shadow-xl max-w-4xl mx-auto mb-8">
          <textarea
            value={videoIdea}
            onChange={(e) => setVideoIdea(e.target.value)}
            placeholder="Describe your video idea..."
            className="w-full bg-arcade-terminal border border-gray-700 rounded-lg p-4 min-h-24 text-white focus:outline-none focus:ring-2 focus:ring-arcade-purple resize-none"
          />
          
          <div className="flex flex-wrap items-center justify-between mt-4">
            <div className="flex space-x-3">
              <button className="p-2 text-gray-400 hover:text-white">
                <Share2 size={20} />
              </button>
              <button className="p-2 text-gray-400 hover:text-white">
                <Download size={20} />
              </button>
            </div>
            
            <div className="flex items-center space-x-3">
              <div className="flex items-center px-3 py-1.5 text-sm border border-gray-700 rounded-lg bg-arcade-terminal/80">
                <Lock size={16} className="mr-2 text-gray-400" />
                <span className="text-gray-300">Public</span>
              </div>
              
              <button 
                onClick={handleCreate}
                disabled={isCreating}
                className="bg-arcade-purple hover:bg-opacity-90 text-white rounded-lg px-6 py-2 flex items-center font-medium disabled:opacity-70"
              >
                <Sparkles size={18} className="mr-2" />
                Create
              </button>
            </div>
          </div>
        </div>
        
        {/* File Upload Section */}
        <div className="max-w-4xl mx-auto mb-8">
          <FileUploader
            maxFiles={10}
            maxFileSizeMB={10}
            onChange={(files) => {
              setUploadedFiles(files);
              // Optional: Log uploaded files for debugging
              console.log('Ready files:', files);
            }}
          />
        </div>
        
        {/* video categories */}
        <div className="flex flex-wrap justify-center gap-3 max-w-4xl mx-auto">
          {videoCategories.map((category) => (
            <button
              key={category.id}
              onClick={() => setSelectedCategory(category.id)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-full border ${
                selectedCategory === category.id 
                  ? 'bg-arcade-purple/20 border-arcade-purple text-white' 
                  : 'bg-arcade-terminal/40 border-gray-700 text-gray-300 hover:bg-arcade-terminal/60'
              }`}
            >
              <span>{category.icon}</span>
              <span>{category.name}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default CreateVideo;
