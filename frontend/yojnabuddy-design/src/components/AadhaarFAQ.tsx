
import { ArrowLeft, ChevronDown, ChevronUp } from 'lucide-react';
import { useState } from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import Navbar from "@/components/Navbar";

const AadhaarFAQ = ({ onBack }: { onBack: () => void }) => {
  const [openFAQ, setOpenFAQ] = useState<number | null>(null);

  const faqs = [
    {
      question: "Who is eligible to apply for an Aadhaar card?",
      answer: "Any resident of India, including infants and elderly, can apply for Aadhaar. NRIs are eligible if they have resided in India for 182 days or more in the past 12 months."
    },
    {
      question: "What documents are required for Aadhaar enrolment?",
      answer: "Proof of identity and proof of address are needed. Biometric data (fingerprints, iris scan, and photograph) are also collected."
    },
    {
      question: "How can I update or correct details in my Aadhaar card?",
      answer: "Visit an Aadhaar Enrolment/Update Centre with supporting documents for the change. You can also update your address online through the UIDAI portal."
    },
    {
      question: "Is it safe to share my Aadhaar number?",
      answer: "Only share your Aadhaar details when necessary, as advised by UIDAI, to prevent misuse."
    },
    {
      question: "How can I download my e-Aadhaar?",
      answer: "You can download it from the UIDAI website using your enrolment ID or Aadhaar number and OTP verification."
    }
  ];

  const toggleFAQ = (index: number) => {
    setOpenFAQ(openFAQ === index ? null : index);
  };

  return (
    <div className="min-h-screen bg-cream">
      <Navbar />
      
      {/* Header Section */}
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
              Aadhaar Card - Frequently Asked Questions
            </h1>
            <p className="text-olive/80 max-w-2xl mx-auto">
              Find answers to the most common questions about Aadhaar card application, updates, and usage.
            </p>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
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

      {/* Help Section */}
      <section className="py-16 px-4">
        <div className="container mx-auto">
          <div className="bg-accent/20 rounded-xl p-6 md:p-10 text-center max-w-3xl mx-auto">
            <h2 className="text-2xl md:text-3xl font-bold text-olive mb-4">
              Need More Help?
            </h2>
            <p className="text-olive/80 mb-8">
              If you couldn't find the answer you're looking for, our support team is here to help you with your Aadhaar-related queries.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button className="bg-primary text-white px-8 py-3 hover:bg-primary/90">
                Contact Support
              </Button>
              <Button variant="outline" className="border-primary text-primary px-8 py-3 hover:bg-primary/5">
                Visit UIDAI Website
              </Button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default AadhaarFAQ;
