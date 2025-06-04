
import { ArrowLeft, ChevronDown, ChevronUp } from 'lucide-react';
import { useState } from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Navbar from "@/components/Navbar";

const BirthCertificateFAQ = ({ onBack }: { onBack: () => void }) => {
  const [openFAQ, setOpenFAQ] = useState<number | null>(null);

  const faqs = [
    {
      question: "Why is a birth certificate important?",
      answer: "It serves as legal proof of identity, age, and citizenship, and is required for school admission, passports, and other documents."
    },
    {
      question: "How do I apply for a birth certificate in India?",
      answer: "Register the birth at your local municipal office or online within 21 days of birth. Submit the required documents and application form."
    },
    {
      question: "What documents are needed for a birth certificate?",
      answer: "Hospital birth certificate, parents' ID proofs, and address proof are commonly required."
    },
    {
      question: "Can I apply for a birth certificate after 21 days?",
      answer: "Yes, but a late fee applies and additional affidavits or permissions may be needed."
    },
    {
      question: "How can I add a name or correct details in a birth certificate?",
      answer: "Submit an application with supporting documents to the issuing authority. Name inclusion and corrections can be done both online and offline."
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
              Birth Certificate - Frequently Asked Questions
            </h1>
            <p className="text-olive/80 max-w-2xl mx-auto">
              Find answers to the most common questions about birth certificate application and corrections.
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
              If you couldn't find the answer you're looking for, our support team is here to help you with your birth certificate-related queries.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button className="bg-primary text-white px-8 py-3 hover:bg-primary/90">
                Contact Support
              </Button>
              <Button variant="outline" className="border-primary text-primary px-8 py-3 hover:bg-primary/5">
                Visit Municipal Office
              </Button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default BirthCertificateFAQ;
