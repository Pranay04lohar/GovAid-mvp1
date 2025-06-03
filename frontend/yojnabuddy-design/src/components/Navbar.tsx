
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Menu, X, Search } from "lucide-react";
import { useChatbot } from "@/contexts/ChatbotContext";

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { setIsOpen } = useChatbot();

  const handleChatbotOpen = () => {
    setIsOpen(true);
    
    // Close mobile menu when opening chatbot
    if (isMenuOpen) {
      setIsMenuOpen(false);
    }
  };

  return (
    <header className="fixed top-0 left-0 w-full bg-white shadow-soft z-50">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between">
        {/* Logo */}
        <a href="/" className="flex items-center">
          <div className="w-10 h-10 rounded-md bg-primary flex items-center justify-center mr-2">
            <span className="text-white font-bold text-xl">G</span>
          </div>
          <span className="text-primary font-bold text-xl hidden sm:inline-block">GovAid</span>
        </a>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center space-x-6">
          <a href="/" className="text-olive hover:text-primary font-medium transition-colors">
            Home
          </a>
          <a href="/schemes" className="text-olive hover:text-primary font-medium transition-colors">
            Schemes
          </a>
          <a href="/legal-help" className="text-olive hover:text-primary font-medium transition-colors">
            Legal Help
          </a>
          <div className="relative">
            <Button variant="outline" size="icon" className="rounded-full">
              <Search className="h-5 w-5" />
              <span className="sr-only">Search</span>
            </Button>
          </div>
          <Button 
            className="bg-accent text-olive hover:bg-accent/90"
            onClick={handleChatbotOpen}
          >
            Chatbot
          </Button>
        </nav>

        {/* Mobile Menu Button */}
        <button
          onClick={() => setIsMenuOpen(!isMenuOpen)}
          className="md:hidden text-olive hover:text-primary"
          aria-label="Toggle menu"
        >
          {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile Menu */}
      {isMenuOpen && (
        <div className="md:hidden bg-white border-t border-gray-100">
          <div className="container mx-auto px-4 py-3">
            <div className="flex flex-col space-y-3">
              <a
                href="/"
                className="text-olive hover:text-primary font-medium py-2 px-3 rounded-md hover:bg-gray-50 transition-colors"
              >
                Home
              </a>
              <a
                href="/schemes"
                className="text-olive hover:text-primary font-medium py-2 px-3 rounded-md hover:bg-gray-50 transition-colors"
              >
                Schemes
              </a>
              <a
                href="/legal-help"
                className="text-olive hover:text-primary font-medium py-2 px-3 rounded-md hover:bg-gray-50 transition-colors"
              >
                Legal Help
              </a>
              <div className="flex items-center space-x-2 py-2 px-3">
                <Search className="h-5 w-5 text-olive" />
                <input
                  type="search"
                  placeholder="Search"
                  className="w-full bg-gray-50 border border-gray-200 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/20"
                />
              </div>
              <Button 
                className="bg-accent text-olive hover:bg-accent/90 w-full"
                onClick={handleChatbotOpen}
              >
                Chatbot
              </Button>
            </div>
          </div>
        </div>
      )}
    </header>
  );
};

export default Navbar;
