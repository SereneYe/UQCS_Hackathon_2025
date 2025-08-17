import { useEffect, useState, useRef } from 'react';

const Terminal = () => {
  const [terminalText, setTerminalText] = useState('');
  const [cursorVisible, setCursorVisible] = useState(true);
  const [animationComplete, setAnimationComplete] = useState(false);
  const terminalRef = useRef<HTMLDivElement>(null);
  
  // Terminal animation sequence
  useEffect(() => {
    const lines = [
      { text: "$ team --name", delay: 80, finalDelay: 400 },
      { text: "\n> Team Names Are Cringe", delay: 40, finalDelay: 500 },
      { text: "\n$ launch StoryAlchemy --prompt \"Make a neon space promo with cinematic vibe\"", delay: 30, finalDelay: 700 },
      { text: "\n✨ Alchemizing your story into video...", delay: 35, finalDelay: 600 },
      { text: "\n⚡ Rendering cinematic frames...", delay: 35, finalDelay: 600 },
      { text: "\n🔧 Optimizing for web delivery...", delay: 35, finalDelay: 700 },
      { text: "\n🎬 Video ready!", delay: 25, finalDelay: 0 },
    ];
    
    let currentText = '';
    let timeoutId: NodeJS.Timeout;
    let currentLineIndex = 0;
    let currentCharIndex = 0;
    
    const typeNextChar = () => {
      if (currentLineIndex >= lines.length) {
        setAnimationComplete(true);
        return;
      }
      
      const currentLine = lines[currentLineIndex];
      
      if (currentCharIndex < currentLine.text.length) {
        currentText += currentLine.text[currentCharIndex];
        setTerminalText(currentText);
        currentCharIndex++;
        
        timeoutId = setTimeout(typeNextChar, currentLine.delay);
      } else {
        currentLineIndex++;
        currentCharIndex = 0;
        timeoutId = setTimeout(typeNextChar, currentLine.finalDelay || 0);
      }
      
      // Ensure terminal scrolls to bottom as text is added
      if (terminalRef.current) {
        terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
      }
    };
    
    timeoutId = setTimeout(typeNextChar, 1000);
    
    return () => clearTimeout(timeoutId);
  }, []);
  
  // Cursor blink effect
  useEffect(() => {
    if (animationComplete) {
      const blinkInterval = setInterval(() => {
        setCursorVisible(prev => !prev);
      }, 500);
      
      return () => clearInterval(blinkInterval);
    }
  }, [animationComplete]);
  
  return (
      <div className="terminal max-w-2xl mx-auto my-6 opacity-0 animate-fade-in delay-200">
        <div className="terminal-header flex items-center bg-gray-800 px-2 py-1 rounded-t">
          <div className="terminal-button close-button bg-red-500 w-3 h-3 rounded-full mr-1"></div>
          <div className="terminal-button minimize-button bg-yellow-500 w-3 h-3 rounded-full mr-1"></div>
          <div className="terminal-button maximize-button bg-green-500 w-3 h-3 rounded-full"></div>
          <div className="ml-auto text-xs text-gray-400">uqcs-hackathon-2025-terminal</div>
        </div>
        <div
            ref={terminalRef}
            className="terminal-content text-sm md:text-base text-green-400 font-mono mt-2 h-56 overflow-auto bg-black p-3 rounded-b whitespace-pre-wrap"
        >
          {terminalText}
          <span className={`cursor border-r-2 border-green-400 ${cursorVisible ? 'opacity-100' : 'opacity-0'}`}></span>
        </div>
      </div>
  );
};

export default Terminal;