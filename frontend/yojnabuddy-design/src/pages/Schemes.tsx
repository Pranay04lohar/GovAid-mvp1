import { useEffect, useState } from 'react';
import { Sprout, Building2, Handshake, GraduationCap, Heart, Home, Scale, Atom, TrendingUp, Users, Trophy, Bus, MapPin, Wrench, Baby } from 'lucide-react';
import Navbar from "@/components/Navbar";
import CategorySchemeCard from "@/components/CategorySchemeCard";
import apiService, { Category } from '@/services/api';

const iconMap: { [key: string]: any } = {
  tractor: Sprout,
  banknote: Building2,
  building: Handshake,
  "book-open": GraduationCap,
  "heart-pulse": Heart,
  home: Home,
  shield: Scale,
  cpu: Atom,
  briefcase: TrendingUp,
  heart: Users,
  trophy: Trophy,
  road: Bus,
  plane: MapPin,
  droplet: Wrench,
  users: Baby
};

const Schemes = () => {
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const data = await apiService.getCategories();
        setCategories(data);
      } catch (err) {
        setError('Failed to load categories. Please try again later.');
        console.error('Error fetching categories:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchCategories();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-cream">
        <Navbar />
        <div className="container mx-auto py-16 px-4 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-olive">Loading categories...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-cream">
        <Navbar />
        <div className="container mx-auto py-16 px-4 text-center">
          <p className="text-red-500">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-cream">
      <Navbar />
      
      {/* Header Section */}
      <section className="py-16 px-4 bg-primary/5 mt-8">
        <div className="container mx-auto text-center">
          <h1 className="text-3xl md:text-4xl font-bold text-olive mb-4">
            Government Schemes
          </h1>
          <p className="text-olive/80 max-w-2xl mx-auto">
            Explore comprehensive government schemes across various categories to find the right assistance for your needs.
          </p>
        </div>
      </section>

      {/* Find Schemes Section */}
      <section className="py-16 px-4">
        <div className="container mx-auto">
          <h2 className="text-2xl md:text-3xl font-bold text-olive text-center mb-12">
            Find schemes based on categories
          </h2>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-6">
            {categories.map((category) => {
              const IconComponent = iconMap[category.icon] || Sprout;
              return (
              <CategorySchemeCard
                key={category.id}
                  id={category.id.toString()}
                  title={category.name}
                  schemeCount={category.scheme_count || 0}
                  icon={<IconComponent className="h-8 w-8" />}
                color={category.color}
              />
              );
            })}
          </div>
        </div>
      </section>
    </div>
  );
};

export default Schemes;
