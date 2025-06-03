
import { Button } from "@/components/ui/button";

const Hero = () => {
  return (
    <section className="bg-gradient-to-b from-cream to-cream/70 pt-24 pb-16 md:pt-32 md:pb-24">
      <div className="container mx-auto px-4">
        <div className="max-w-3xl mx-auto text-center">
          <h1 className="text-3xl md:text-5xl font-bold text-olive leading-tight mb-6">
            Get Help From Government Schemes and Legal Aid
          </h1>
          <p className="text-lg md:text-xl text-olive/80 mb-8 max-w-2xl mx-auto">
            Find and access the government services and legal assistance you need, all in one place.
            We simplify the process to help you get the support you deserve.
          </p>
          <div className="flex flex-col sm:flex-row justify-center items-center gap-4">
            <Button className="bg-primary hover:bg-primary/90 text-white py-2 px-6 w-full sm:w-auto">
              Find Services
            </Button>
            <Button variant="outline" className="border-primary text-primary hover:bg-primary/5 py-2 px-6 w-full sm:w-auto">
              How It Works
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
