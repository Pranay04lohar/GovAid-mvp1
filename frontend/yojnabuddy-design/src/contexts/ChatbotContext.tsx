import { createContext, useContext, useState, ReactNode } from "react";

interface ChatbotContextType {
  isOpen: boolean;
  setIsOpen: (value: boolean) => void;
  messages: Message[];
  setMessages: (messages: Message[]) => void;
  inputText: string;
  setInputText: (text: string) => void;
  handleSendMessage: () => Promise<void>;
  isLoading: boolean;
}

export interface Message {
  id: number;
  text: string;
  isUser: boolean;
  sources?: Array<{
    source: string;
    page: string;
  }>;
}

const ChatbotContext = createContext<ChatbotContextType | undefined>(undefined);

export const ChatbotProvider = ({ children }: { children: ReactNode }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: "Hello! I'm your legal assistance AI. I can help you with:\n\n• Understanding your legal rights\n• Basic legal advice and guidance\n• Document preparation assistance\n• Referrals to legal services\n\nWhat legal matter can I help you with today?",
      isUser: false
    }
  ]);
  const [inputText, setInputText] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async () => {
    if (inputText.trim() === "") return;
    
    // Add user message
    const newUserMessage = {
      id: messages.length + 1,
      text: inputText,
      isUser: true
    };
    
    setMessages(prev => [...prev, newUserMessage]);
    setInputText("");
    setIsLoading(true);
    
    try {
      // Call the backend API
      const response = await fetch("http://localhost:8000/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: inputText }),
      });

      if (!response.ok) {
        throw new Error("Failed to get response from chatbot");
      }

      const data = await response.json();
      
      // Add bot response
      const botResponse = {
        id: messages.length + 2,
        text: data.answer,
        isUser: false,
        sources: data.sources
      };
      
      setMessages(prev => [...prev, botResponse]);
    } catch (error) {
      console.error("Error:", error);
      // Add error message
      const errorMessage = {
        id: messages.length + 2,
        text: "I apologize, but I'm having trouble connecting to my knowledge base. Please try again in a moment.",
        isUser: false
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <ChatbotContext.Provider value={{ 
      isOpen, 
      setIsOpen, 
      messages, 
      setMessages, 
      inputText, 
      setInputText,
      handleSendMessage,
      isLoading
    }}>
      {children}
    </ChatbotContext.Provider>
  );
};

export const useChatbot = () => {
  const context = useContext(ChatbotContext);
  if (context === undefined) {
    throw new Error("useChatbot must be used within a ChatbotProvider");
  }
  return context;
};
