
import { ArrowLeft, ChevronDown, ChevronUp } from 'lucide-react';
import { useState } from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Navbar from "@/components/Navbar";

const DrivingLicenceFAQ = ({ onBack }: { onBack: () => void }) => {
  const [openFAQ, setOpenFAQ] = useState<number | null>(null);

  const faqs = [
    {
      question: "What is the minimum age to get a driving licence in India?",
      answer: "You must be at least 18 years old to apply for a permanent driving licence."
    },
    {
      question: "What is the process to get a driving licence?",
      answer: "First, obtain a learner's licence by passing a written test. After 30 days, apply for a permanent licence and pass the practical driving test."
    },
    {
      question: "Is training from a driving school mandatory?",
      answer: "While not always mandatory, it is recommended, especially for commercial licences."
    },
    {
      question: "How long is a driving licence valid?",
      answer: "Typically valid for 20 years or until the holder turns 50, whichever is earlier. Renewal is required thereafter."
    },
    {
      question: "Can I update my details or renew my driving licence online?",
      answer: "Yes, many states allow online renewal and updates via the Parivahan portal or state transport websites."
    }
  ];

  const toggleFAQ = (index: number) => {
    setOpenFAQ(openFAQ === index ? null : index);
  };

  return (
    <div className="min-h-screen bg-cream">
      <Navbar />
      
      <section className="py-16 px-4 bg-primary/5 mt-8">
        <div className="container mx-auto">
          <Button 
            onClick={onBack}
            variant="ghost" 
            className="mb-4 text-olive hover:text-primary"
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Documents
          </Button>
          
          <div className="text-center">
            <h1 className="text-3xl md:text-4xl font-bold text-olive mb-4">
              Driving Licence - Frequently Asked Questions
            </h1>
            <p className="text-olive/80 max-w-2xl mx-auto">
              Find answers to the most common questions about driving licence application and renewal.
            </p>
          </div>
        </div>
      </section>

      <section className="py-16 px-4">
        <div className="container mx-auto max-w-4xl">
          <div className="space-y-4">
            {faqs.map((faq, index) => (
              <Card key={index} className="bg-white/90 backdrop-blur-sm shadow-soft border-0">
                <CardContent className="p-0">
                  <button
                    onClick={() => toggleFAQ(index)}
                    className="w-full text-left p-6 flex items-center justify-between hover:bg-primary/5 transition-colors"
                  >
                    <h3 className="text-lg font-semibold text-olive pr-4">
                      {faq.question}
                    </h3>
                    {openFAQ === index ? (
                      <ChevronUp className="h-5 w-5 text-primary flex-shrink-0" />
                    ) : (
                      <ChevronDown className="h-5 w-5 text-primary flex-shrink-0" />
                    )}
                  </button>
                  
                  {openFAQ === index && (
                    <div className="px-6 pb-6">
                      <div className="bg-primary/5 rounded-lg p-4">
                        <p className="text-olive/80 leading-relaxed">
                          {faq.answer}
                        </p>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section className="py-16 px-4">
        <div className="container mx-auto">
          <div className="bg-accent/20 rounded-xl p-6 md:p-10 text-center max-w-3xl mx-auto">
            <h2 className="text-2xl md:text-3xl font-bold text-olive mb-4">
              Need More Help?
            </h2>
            <p className="text-olive/80 mb-8">
              If you couldn't find the answer you're looking for, our support team is here to help you with your driving licence-related queries.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button className="bg-primary text-white px-8 py-3 hover:bg-primary/90">
                Contact Support
              </Button>
              <Button variant="outline" className="border-primary text-primary px-8 py-3 hover:bg-primary/5">
                Visit Parivahan Portal
              </Button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default DrivingLicenceFAQ;
