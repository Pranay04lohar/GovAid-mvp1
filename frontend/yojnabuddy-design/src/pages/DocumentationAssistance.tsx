
import { FileText, Upload, Download, CheckCircle, Clock, Users } from 'lucide-react';
import Navbar from "@/components/Navbar";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

const DocumentationAssistance = () => {
  const documentServices = [
    {
      id: "application-filing",
      title: "Application Filing",
      description: "Help with completing and filing government applications, permits, and licenses.",
      icon: <FileText className="h-8 w-8" />,
      color: "#2F855A"
    },
    {
      id: "document-preparation",
      title: "Document Preparation",
      description: "Assistance with preparing required documents and ensuring all paperwork is complete.",
      icon: <Upload className="h-8 w-8" />,
      color: "#3B82F6"
    },
    {
      id: "status-tracking",
      title: "Application Status Tracking",
      description: "Track the progress of your submitted applications and get real-time updates.",
      icon: <Clock className="h-8 w-8" />,
      color: "#F59E0B"
    },
    {
      id: "document-verification",
      title: "Document Verification",
      description: "Verify the authenticity and completeness of your official documents.",
      icon: <CheckCircle className="h-8 w-8" />,
      color: "#10B981"
    }
  ];

  const commonDocuments = [
    {
      category: "Identity Documents",
      documents: ["Birth Certificate", "Passport", "Driver's License", "Social Security Card"]
    },
    {
      category: "Financial Documents",
      documents: ["Tax Returns", "Bank Statements", "Income Certificates", "Property Documents"]
    },
    {
      category: "Educational Documents",
      documents: ["Degree Certificates", "Transcripts", "Diploma Verification", "Student ID"]
    },
    {
      category: "Legal Documents",
      documents: ["Court Orders", "Legal Notices", "Affidavits", "Power of Attorney"]
    }
  ];

  const steps = [
    {
      step: 1,
      title: "Submit Request",
      description: "Fill out the documentation assistance request form with your requirements."
    },
    {
      step: 2,
      title: "Document Review",
      description: "Our experts review your existing documents and identify missing items."
    },
    {
      step: 3,
      title: "Preparation Support",
      description: "Get guided assistance in preparing and organizing all required documents."
    },
    {
      step: 4,
      title: "Filing & Submission",
      description: "Complete the filing process with proper submission to relevant authorities."
    }
  ];

  return (
    <div className="min-h-screen bg-cream">
      <Navbar />
      
      {/* Header Section */}
      <section className="py-16 px-4 bg-primary/5 mt-8">
        <div className="container mx-auto text-center">
          <h1 className="text-3xl md:text-4xl font-bold text-olive mb-4">
            Documentation Assistance
          </h1>
          <p className="text-olive/80 max-w-2xl mx-auto">
            Get expert help with preparing, filing, and tracking your important government documents and applications. We simplify the paperwork process for you.
          </p>
        </div>
      </section>

      {/* Services Section */}
      <section className="py-16 px-4">
        <div className="container mx-auto">
          <h2 className="text-2xl md:text-3xl font-bold text-olive text-center mb-12">
            Our Documentation Services
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {documentServices.map((service) => (
              <Card key={service.id} className="bg-white shadow-soft hover:shadow-medium transition-shadow border-t-4" style={{ borderTopColor: service.color }}>
                <CardHeader className="pt-6">
                  <div className="flex items-center gap-4">
                    <div 
                      className="w-12 h-12 rounded-full flex items-center justify-center"
                      style={{ backgroundColor: `${service.color}20` }}
                    >
                      <div style={{ color: service.color }}>
                        {service.icon}
                      </div>
                    </div>
                    <h3 className="text-xl font-semibold text-olive">{service.title}</h3>
                  </div>
                </CardHeader>
                <CardContent>
                  <p className="text-olive/80 mb-4">{service.description}</p>
                  <Button 
                    className="w-full"
                    style={{ backgroundColor: service.color, color: '#FDFCFB' }}
                  >
                    Get Assistance
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Common Documents Section */}
      <section className="py-16 px-4 bg-gray-50">
        <div className="container mx-auto">
          <h2 className="text-2xl md:text-3xl font-bold text-olive text-center mb-12">
            Common Documents We Help With
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {commonDocuments.map((category, index) => (
              <Card key={index} className="bg-white shadow-soft">
                <CardContent className="p-6">
                  <h3 className="text-lg font-semibold text-olive mb-4">{category.category}</h3>
                  <ul className="space-y-2">
                    {category.documents.map((doc, docIndex) => (
                      <li key={docIndex} className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-primary rounded-full"></div>
                        <span className="text-olive/80 text-sm">{doc}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Process Steps Section */}
      <section className="py-16 px-4">
        <div className="container mx-auto">
          <h2 className="text-2xl md:text-3xl font-bold text-olive text-center mb-12">
            How It Works
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {steps.map((step) => (
              <div key={step.step} className="text-center">
                <div className="w-16 h-16 bg-primary rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-white font-bold text-xl">{step.step}</span>
                </div>
                <h3 className="text-lg font-semibold text-olive mb-2">{step.title}</h3>
                <p className="text-olive/80 text-sm">{step.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Call to Action Section */}
      <section className="py-16 px-4">
        <div className="container mx-auto">
          <div className="bg-accent/20 rounded-xl p-6 md:p-10 text-center">
            <h2 className="text-2xl md:text-3xl font-bold text-olive mb-4">
              Ready to Get Started?
            </h2>
            <p className="text-olive/80 mb-8 max-w-2xl mx-auto">
              Don't let paperwork hold you back. Our documentation experts are here to guide you through every step of the process.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button className="bg-primary text-white px-8 py-3">
                Start Documentation Process
              </Button>
              <Button variant="outline" className="px-8 py-3">
                Download Checklist
              </Button>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default DocumentationAssistance;
