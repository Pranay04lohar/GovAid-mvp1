import { MessageCircle, Scale, FileText, Shield, Clock } from 'lucide-react';
import Navbar from "@/components/Navbar";
import { Button } from "@/components/ui/button";
import { useChatbot } from "@/contexts/ChatbotContext";
import { useEffect } from "react";
import ChatbotButton from "@/components/ChatbotButton";

const LegalHelp = () => {
  const { setIsOpen, setMessages } = useChatbot();

  // Initialize chatbot with legal-specific welcome message
  useEffect(() => {
    setMessages([
      {
        id: 1,
        text: "Hello! I'm your legal assistance AI. I can help you with:\n\n• Understanding your legal rights\n• Basic legal advice and guidance\n• Document preparation assistance\n• Referrals to legal services\n\nWhat legal matter can I help you with today?",
        isUser: false
      }
    ]);
  }, [setMessages]);

  const handleExploreLegalHelp = () => {
    setIsOpen(true);
  };

  const legalTopics = [
    {
      title: "Civil Matters",
      description: "Property disputes, contracts, family law, and more",
      icon: <Scale className="h-6 w-6 text-primary" />
    },
    {
      title: "Documentation",
      description: "Legal documents, contracts, wills, and applications",
      icon: <FileText className="h-6 w-6 text-primary" />
    },
    {
      title: "Legal Rights",
      description: "Understanding your rights and available options",
      icon: <Shield className="h-6 w-6 text-primary" />
    },
    {
      title: "Urgent Matters",
      description: "Immediate legal assistance and emergency support",
      icon: <Clock className="h-6 w-6 text-primary" />
    }
  ];

  return (
    <div className="min-h-screen bg-cream">
      <Navbar />
      
      {/* Header Section */}
      <section className="py-16 px-4 bg-primary/5 mt-8">
        <div className="container mx-auto text-center">
          <h1 className="text-3xl md:text-4xl font-bold text-olive mb-4">
            Legal Help & Assistance
          </h1>
          <p className="text-olive/80 max-w-2xl mx-auto">
            Get instant legal guidance and support for various legal matters. Our AI assistant is here to help you understand your legal rights and available options.
          </p>
        </div>
      </section>

      {/* Main Content Section */}
      <section className="py-16 px-4">
        <div className="container mx-auto max-w-4xl">
          <div className="bg-white rounded-xl shadow-soft p-8 md:p-12">
            <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-6">
              <MessageCircle className="h-10 w-10 text-primary" />
            </div>
            
            <h2 className="text-2xl md:text-3xl font-bold text-olive mb-4 text-center">
              AI-Powered Legal Assistance
            </h2>
            
            <p className="text-olive/80 mb-8 max-w-2xl mx-auto text-center">
              Our advanced AI assistant can help you with various legal matters. 
              Get instant guidance, understand your rights, and learn about available options.
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              {legalTopics.map((topic, index) => (
                <div 
                  key={index}
                  className="bg-gray-50 rounded-lg p-6 hover:bg-primary/5 transition-colors cursor-pointer"
                  onClick={handleExploreLegalHelp}
                >
                  <div className="flex items-start gap-4">
                    <div className="bg-primary/10 p-3 rounded-lg">
                      {topic.icon}
                    </div>
                    <div>
                      <h3 className="font-semibold text-olive mb-2">{topic.title}</h3>
                      <p className="text-sm text-olive/70">{topic.description}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="text-center">
              <Button 
                onClick={handleExploreLegalHelp}
                className="bg-primary text-white px-8 py-3 text-lg hover:bg-primary/90"
              >
                <MessageCircle className="mr-2 h-5 w-5" />
                Start Legal Consultation
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Emergency Contact Section */}
      <section className="py-16 px-4 bg-gray-50">
        <div className="container mx-auto">
          <div className="bg-primary/10 rounded-xl p-6 md:p-10 text-center">
            <h2 className="text-2xl md:text-3xl font-bold text-primary mb-4">
              Need Immediate Legal Help?
            </h2>
            <p className="text-olive/80 mb-8 max-w-2xl mx-auto">
              If you're facing an urgent legal situation or need immediate assistance, 
              our AI assistant can help guide you through emergency procedures or connect you with legal professionals.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button 
                onClick={handleExploreLegalHelp}
                className="bg-primary text-white px-8 py-3"
              >
                Start Emergency Consultation
              </Button>
              <Button 
                variant="outline" 
                className="px-8 py-3"
                onClick={() => window.location.href = 'tel:+911234567890'}
              >
                Call Emergency Helpline
              </Button>
            </div>
          </div>
        </div>
      </section>

      <ChatbotButton />
    </div>
  );
};

export default LegalHelp;
