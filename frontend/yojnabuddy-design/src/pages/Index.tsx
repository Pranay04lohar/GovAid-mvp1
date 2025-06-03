import { Home, Scale, BookOpen } from 'lucide-react';
import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import CategoryCard from "@/components/CategoryCard";
import SchemeCard from "@/components/SchemeCard";
import ChatbotButton from "@/components/ChatbotButton";
import { useChatbot } from "@/contexts/ChatbotContext";

const Index = () => {
  const { setIsOpen } = useChatbot();
  
  const categories = [
    {
      title: "Legal Help",
      description: "Access free legal consultation, advice, and representation for civil and criminal matters.",
      icon: <Scale className="h-6 w-6 text-primary" />,
      color: "#2F855A" // primary color
    },
    {
      title: "Government Schemes",
      description: "Find and apply for government welfare schemes, subsidies, and financial assistance programs.",
      icon: <Home className="h-6 w-6 text-accent" />,
      color: "#ECC94B" // accent color
    },
    {
      title: "Documentation Assistance",
      description: "Get help with preparing, filing, and tracking important government documents and applications.",
      icon: <BookOpen className="h-6 w-6 text-olive" />,
      color: "#2D3748" // olive color
    },
  ];

  const schemes = [
    {
      id: "housing-assistance",
      title: "Housing Assistance Program",
      description: "Financial support for low-income families to secure affordable housing with subsidized rent payments.",
      category: "Housing"
    },
    {
      id: "legal-aid",
      title: "Free Legal Aid Service",
      description: "Pro bono legal representation and advice for qualifying individuals in civil and criminal cases.",
      category: "Legal"
    },
    {
      id: "healthcare-subsidy",
      title: "Healthcare Subsidy Scheme",
      description: "Reduced healthcare costs for essential medical procedures and prescription medications.",
      category: "Healthcare"
    },
    {
      id: "education-grant",
      title: "Education Grant Program",
      description: "Financial assistance for students pursuing higher education with focus on underprivileged backgrounds.",
      category: "Education"
    },
  ];

  const handleChatbotOpen = () => {
    setIsOpen(true);
  };

  return (
    <div className="min-h-screen bg-cream">
      <Navbar />
      <Hero />

      {/* Categories Section */}
      <section className="py-16 px-4">
        <div className="container mx-auto">
          <h2 className="text-2xl md:text-3xl font-bold text-olive text-center mb-10">
            Our Services
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {categories.map((category) => (
              <CategoryCard
                key={category.title}
                title={category.title}
                description={category.description}
                icon={category.icon}
                color={category.color}
              />
            ))}
          </div>
        </div>
      </section>

      {/* Schemes Section */}
      <section className="py-16 px-4 bg-gray-50">
        <div className="container mx-auto">
          <div className="flex justify-between items-center mb-10">
            <h2 className="text-2xl md:text-3xl font-bold text-olive">
              Popular Schemes
            </h2>
            <a href="/schemes" className="text-primary font-medium hover:underline">
              View all schemes
            </a>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {schemes.map((scheme) => (
              <SchemeCard
                key={scheme.id}
                id={scheme.id}
                title={scheme.title}
                description={scheme.description}
                category={scheme.category}
              />
            ))}
          </div>
        </div>
      </section>

      {/* Featured Section */}
      <section className="py-16 px-4">
        <div className="container mx-auto">
          <div className="bg-primary/10 rounded-xl p-6 md:p-10 text-center">
            <h2 className="text-2xl md:text-3xl font-bold text-primary mb-4">
              Need Help Finding the Right Service?
            </h2>
            <p className="text-olive/80 mb-8 max-w-2xl mx-auto">
              Our chatbot assistant can help you navigate through available services and find the most suitable options based on your specific needs.
            </p>
            <div 
              className="inline-block bg-accent text-olive font-semibold px-6 py-3 rounded-lg hover:bg-accent/90 transition-colors cursor-pointer"
              onClick={handleChatbotOpen}
            >
              Chat With Our Assistant
            </div>
          </div>
        </div>
      </section>

      {/* Footer Section */}
      <footer className="bg-olive text-cream py-10">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-lg font-semibold mb-4">GovAid</h3>
              <p className="text-cream/80 text-sm">
                Making government services and legal aid accessible to everyone.
              </p>
            </div>
            <div>
              <h4 className="font-medium mb-3">Services</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="text-cream/80 hover:text-cream">Legal Help</a></li>
                <li><a href="#" className="text-cream/80 hover:text-cream">Government Schemes</a></li>
                <li><a href="#" className="text-cream/80 hover:text-cream">Documentation</a></li>
                <li><a href="#" className="text-cream/80 hover:text-cream">Consultation</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium mb-3">Resources</h4>
              <ul className="space-y-2 text-sm">
                <li><a href="#" className="text-cream/80 hover:text-cream">FAQs</a></li>
                <li><a href="#" className="text-cream/80 hover:text-cream">Blog</a></li>
                <li><a href="#" className="text-cream/80 hover:text-cream">Guides</a></li>
                <li><a href="#" className="text-cream/80 hover:text-cream">Support</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-medium mb-3">Contact</h4>
              <ul className="space-y-2 text-sm">
                <li className="text-cream/80">contact@govaid.org</li>
                <li className="text-cream/80">+1 (555) 123-4567</li>
                <li className="text-cream/80">123 Government Ave, City</li>
              </ul>
            </div>
          </div>
          <div className="border-t border-cream/20 mt-8 pt-8 text-center text-sm text-cream/60">
            <p>© 2025 GovAid. All rights reserved.</p>
          </div>
        </div>
      </footer>

      <ChatbotButton />
    </div>
  );
};

export default Index;
