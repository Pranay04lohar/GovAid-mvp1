import { useState } from 'react';
import { IdCard, FileText, Car, Vote, CircleDot, Heart } from 'lucide-react';
import Navbar from "@/components/Navbar";
import { Card, CardContent } from "@/components/ui/card";
import AadhaarFAQ from "@/components/AadhaarFAQ";
import PANCardFAQ from "@/components/PANCardFAQ";
import BirthCertificateFAQ from "@/components/BirthCertificateFAQ";
import PassportFAQ from "@/components/PassportFAQ";
import DrivingLicenceFAQ from "@/components/DrivingLicenceFAQ";
import VoterIDFAQ from "@/components/VoterIDFAQ";
import RationCardFAQ from "@/components/RationCardFAQ";
import MarriageCertificateFAQ from "@/components/MarriageCertificateFAQ";

const DocumentationAssistance = () => {
  const [selectedDocument, setSelectedDocument] = useState<string | null>(null);

  const popularDocuments = [
    {
      id: "aadhaar-card",
      title: "Aadhaar Card",
      icon: <IdCard className="h-8 w-8" />,
      color: "#2F855A",
      bgColor: "#2F855A"
    },
    {
      id: "pan-card", 
      title: "PAN Card",
      icon: <FileText className="h-8 w-8" />,
      color: "#ECC94B",
      bgColor: "#ECC94B"
    },
    {
      id: "birth-certificate",
      title: "Birth Certificate", 
      icon: <FileText className="h-8 w-8" />,
      color: "#3B82F6",
      bgColor: "#3B82F6"
    },
    {
      id: "passport",
      title: "Passport",
      icon: <FileText className="h-8 w-8" />,
      color: "#10B981",
      bgColor: "#10B981"
    },
    {
      id: "driving-licence",
      title: "Driving Licence",
      icon: <Car className="h-8 w-8" />,
      color: "#F59E0B",
      bgColor: "#F59E0B"
    },
    {
      id: "voter-id-card",
      title: "Voter ID Card",
      icon: <Vote className="h-8 w-8" />,
      color: "#8B5CF6",
      bgColor: "#8B5CF6"
    },
    {
      id: "ration-card",
      title: "Ration Card",
      icon: <CircleDot className="h-8 w-8" />,
      color: "#EF4444",
      bgColor: "#EF4444"
    },
    {
      id: "marriage-certificate",
      title: "Marriage Certificate",
      icon: <Heart className="h-8 w-8" />,
      color: "#EC4899",
      bgColor: "#EC4899"
    }
  ];

  const handleDocumentClick = (documentId: string) => {
    setSelectedDocument(documentId);
  };

  const handleBackToDocuments = () => {
    setSelectedDocument(null);
  };

  // Show respective FAQ page based on selection
  if (selectedDocument === "aadhaar-card") {
    return <AadhaarFAQ onBack={handleBackToDocuments} />;
  }
  if (selectedDocument === "pan-card") {
    return <PANCardFAQ onBack={handleBackToDocuments} />;
  }
  if (selectedDocument === "birth-certificate") {
    return <BirthCertificateFAQ onBack={handleBackToDocuments} />;
  }
  if (selectedDocument === "passport") {
    return <PassportFAQ onBack={handleBackToDocuments} />;
  }
  if (selectedDocument === "driving-licence") {
    return <DrivingLicenceFAQ onBack={handleBackToDocuments} />;
  }
  if (selectedDocument === "voter-id-card") {
    return <VoterIDFAQ onBack={handleBackToDocuments} />;
  }
  if (selectedDocument === "ration-card") {
    return <RationCardFAQ onBack={handleBackToDocuments} />;
  }
  if (selectedDocument === "marriage-certificate") {
    return <MarriageCertificateFAQ onBack={handleBackToDocuments} />;
  }

  return (
    <div className="min-h-screen bg-cream">
      <Navbar />
      
      {/* Header Section */}
      <section className="py-16 px-4 bg-primary/5 mt-8">
        <div className="container mx-auto text-center">
          <h1 className="text-3xl md:text-4xl font-bold text-olive mb-4">
            Get assistance to your most popular documents
          </h1>
          <p className="text-olive/80 max-w-2xl mx-auto">
            Select the document you need help with and get step-by-step guidance for applications, renewals, and corrections.
          </p>
        </div>
      </section>

      {/* Documents Grid Section */}
      <section className="py-16 px-4">
        <div className="container mx-auto">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
            {popularDocuments.map((document) => (
              <Card 
                key={document.id} 
                onClick={() => handleDocumentClick(document.id)}
                className="bg-white/90 backdrop-blur-sm shadow-soft hover:shadow-medium transition-all duration-300 cursor-pointer group border-0 overflow-hidden"
                style={{ 
                  background: `linear-gradient(135deg, ${document.bgColor}15 0%, ${document.bgColor}08 100%)`,
                }}
              >
                <CardContent className="p-8 text-center h-48 flex flex-col items-center justify-center">
                  <div 
                    className="w-20 h-20 rounded-full flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300"
                    style={{ 
                      background: `linear-gradient(135deg, ${document.color}20 0%, ${document.color}10 100%)`,
                      border: `2px solid ${document.color}30`
                    }}
                  >
                    <div style={{ color: document.color }}>
                      {document.icon}
                    </div>
                  </div>
                  <h3 className="text-lg font-semibold text-olive group-hover:text-primary transition-colors duration-300">
                    {document.title}
                  </h3>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Call to Action Section */}
      <section className="py-16 px-4">
        <div className="container mx-auto">
          <div className="bg-accent/20 rounded-xl p-6 md:p-10 text-center max-w-4xl mx-auto">
            <h2 className="text-2xl md:text-3xl font-bold text-olive mb-4">
              Need Help with a Different Document?
            </h2>
            <p className="text-olive/80 mb-8">
              Our comprehensive documentation assistance covers hundreds of government documents and services. Get personalized help for any document you need.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="bg-primary text-white px-8 py-3 rounded-md hover:bg-primary/90 transition-colors">
                Browse All Documents
              </button>
              <button className="border border-primary text-primary px-8 py-3 rounded-md hover:bg-primary/5 transition-colors">
                Contact Support
              </button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default DocumentationAssistance;
