import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import CreateVideo from "./pages/CreateVideo.tsx";
import VideoWorkspace from "./pages/VideoWorkspace.tsx";
import MyVideos from "./pages/MyVideos.tsx";
import NotFound from "./pages/NotFound";
// Only import testing pages in development environment
import Testing from "./pages/Testing";

const queryClient = new QueryClient();

const App = () => (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/create-video" element={<CreateVideo />} />
            <Route path="/my-videos" element={<MyVideos />} />
            <Route path="/workspace/:slug" element={<VideoWorkspace />} />
            {import.meta.env.DEV && (
              <Route path="/testing" element={<Testing />} />
            )}
            {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
);

export default App;
