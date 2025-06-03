
import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import NotFound from "./pages/NotFound";
import SchemeDetail from "./pages/SchemeDetail";
import Schemes from "./pages/Schemes";
import CategorySchemes from "./pages/CategorySchemes";
import LegalHelp from "./pages/LegalHelp";
import DocumentationAssistance from "./pages/DocumentationAssistance";
import { ChatbotProvider } from "@/contexts/ChatbotContext";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <ChatbotProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Index />} />
            <Route path="/schemes" element={<Schemes />} />
            <Route path="/schemes/category/:categoryId" element={<CategorySchemes />} />
            <Route path="/schemes/:id" element={<SchemeDetail />} />
            <Route path="/legal-help" element={<LegalHelp />} />
            <Route path="/documentation-assistance" element={<DocumentationAssistance />} />
            <Route path="/search" element={<NotFound />} />
            {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </ChatbotProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
