import { useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { MessageCircle, X, Send, Loader2, FileText } from "lucide-react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Textarea } from "@/components/ui/textarea";
import { useChatbot } from "@/contexts/ChatbotContext";
import ReactMarkdown from "react-markdown";

const ChatbotButton = () => {
  const { 
    isOpen, 
    setIsOpen, 
    messages, 
    inputText, 
    setInputText, 
    handleSendMessage,
    isLoading
  } = useChatbot();
  
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  
  // Auto-scroll to bottom when new messages are added
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  // Focus input when chat opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-40">
      {isOpen && (
        <div className="bg-white rounded-lg shadow-lg mb-4 w-[350px] sm:w-[380px] md:w-[420px] flex flex-col">
          <div className="bg-primary rounded-t-lg p-4 flex items-center justify-between">
            <h3 className="text-white font-medium">Legal Assistant</h3>
            <Button 
              variant="ghost" 
              size="icon"
              className="h-8 w-8 text-white hover:bg-primary-foreground/10"
              onClick={() => setIsOpen(false)}
            >
              <X className="h-4 w-4" />
              <span className="sr-only">Close</span>
            </Button>
          </div>
          
          <ScrollArea className="h-96 p-4 overflow-y-auto border-b" ref={scrollAreaRef}>
            <div className="space-y-4">
              {messages.map((message) => (
                <div key={message.id}>
                <div 
                  className={`${message.isUser 
                    ? "bg-accent/20 ml-auto mr-0" 
                    : "bg-[#F2FCE2] mr-auto ml-0"} 
                    rounded-lg p-3 max-w-[80%]`}
                >
                    {message.isUser ? (
                      <p className="text-sm whitespace-pre-line">{message.text}</p>
                    ) : (
                      <div className="text-sm whitespace-pre-line">
                        <ReactMarkdown>{message.text}</ReactMarkdown>
                      </div>
                    )}
                  </div>
                  
                  {/* Show sources if available */}
                  {!message.isUser && message.sources && message.sources.length > 0 && (
                    <div className="mt-2 ml-2 text-xs text-gray-500">
                      <div className="flex items-center gap-1 mb-1">
                        <FileText className="h-3 w-3" />
                        <span>Sources:</span>
                      </div>
                      {message.sources.map((source, index) => (
                        <div key={index} className="ml-4">
                          {source.source} (Page {source.page})
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
              
              {/* Loading indicator */}
              {isLoading && (
                <div className="flex items-center gap-2 text-sm text-gray-500">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Thinking...</span>
                </div>
              )}
            </div>
          </ScrollArea>
          
          <div className="p-4">
            <div className="flex gap-2 items-end">
              <Textarea
                ref={inputRef}
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask about any legal matter..."
                className="flex-1 text-sm min-h-[70px] max-h-[120px] focus:ring-primary focus:border-primary border-gray-200"
                rows={3}
                disabled={isLoading}
              />
              <Button 
                onClick={handleSendMessage}
                className="bg-primary hover:bg-primary/90 h-10 px-3"
                disabled={inputText.trim() === "" || isLoading}
              >
                {isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                <Send className="h-4 w-4" />
                )}
                <span className="sr-only">Send</span>
              </Button>
            </div>
          </div>
        </div>
      )}
      
      <Button
        onClick={() => setIsOpen(!isOpen)}
        className="h-16 w-16 rounded-full bg-accent hover:bg-accent/90 shadow-lg"
      >
        <MessageCircle className="h-7 w-7 text-olive" />
        <span className="sr-only">Open chatbot</span>
      </Button>
    </div>
  );
};

export default ChatbotButton;
