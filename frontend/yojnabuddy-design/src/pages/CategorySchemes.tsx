import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Navbar from "@/components/Navbar";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Pagination, PaginationContent, PaginationItem, PaginationLink, PaginationNext, PaginationPrevious } from "@/components/ui/pagination";
import apiService, { Scheme, Category } from '@/services/api';

const CategorySchemes = () => {
  const { categoryId } = useParams();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState("all");
  const [sortBy, setSortBy] = useState("relevance");
  const [currentPage, setCurrentPage] = useState(1);
  const [schemes, setSchemes] = useState<Scheme[]>([]);
  const [totalSchemes, setTotalSchemes] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [category, setCategory] = useState<Category | null>(null);

  const fetchSchemes = async () => {
    try {
      setLoading(true);
      let response;
      
      if (activeTab === "all") {
        response = await apiService.getSchemesByCategory(Number(categoryId), currentPage, 10, sortBy);
      } else {
        response = await apiService.getSchemesByType(Number(categoryId), activeTab as 'state' | 'central', currentPage, 10);
      }
      
      console.log("API Response in fetchSchemes:", response);
      setSchemes(response.data);
      setTotalSchemes(response.total);
    } catch (err) {
      setError('Failed to load schemes. Please try again later.');
      console.error('Error fetching schemes:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchCategory = async () => {
    try {
      const categories = await apiService.getCategories();
      const category = categories.find(c => c.id === Number(categoryId));
      if (category) {
        setCategory(category);
      }
    } catch (err) {
      console.error('Error fetching category:', err);
    }
  };

  useEffect(() => {
    fetchCategory();
  }, [categoryId]);

  useEffect(() => {
    fetchSchemes();
  }, [categoryId, activeTab, sortBy, currentPage]);

  const handleSchemeClick = (schemeId: number) => {
    console.log("Navigating to scheme with ID:", schemeId, "Type:", typeof schemeId);
    navigate(`/schemes/${schemeId}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-cream">
        <Navbar />
        <div className="container mx-auto py-16 px-4 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-olive">Loading schemes...</p>
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
        <div className="container mx-auto">
          <h1 className="text-3xl md:text-4xl font-bold text-olive mb-4">
            {category?.name || "Loading..."}
          </h1>
          <p className="text-olive/80">
            {category?.description || "Explore government schemes in this category"}
          </p>
        </div>
      </section>

      {/* Content Section */}
      <section className="py-8 px-4">
        <div className="container mx-auto">
          {/* Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="mb-6">
            <TabsList className="grid w-full grid-cols-3 max-w-md">
              <TabsTrigger value="all">All Schemes</TabsTrigger>
              <TabsTrigger value="state">State Schemes</TabsTrigger>
              <TabsTrigger value="central">Central Schemes</TabsTrigger>
            </TabsList>
          </Tabs>

          {/* Results Header */}
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6 gap-4">
            <p className="text-olive/70">
              We found <span className="font-semibold text-primary">{totalSchemes}</span> schemes based on your preferences
            </p>
            
            <div className="flex items-center gap-2">
              <span className="text-sm text-olive/70">Sort :</span>
              <Select value={sortBy} onValueChange={setSortBy}>
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="relevance">Relevance</SelectItem>
                  <SelectItem value="newest">Newest</SelectItem>
                  <SelectItem value="alphabetical">A-Z</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {/* Schemes List */}
          <div className="space-y-6">
            {schemes.map((scheme) => (
              <div 
                key={scheme.id} 
                className="bg-white rounded-lg shadow-soft p-6 border border-gray-100 cursor-pointer hover:shadow-medium transition-shadow"
                onClick={() => handleSchemeClick(scheme.id)}
              >
                <div className="space-y-4">
                  <div>
                    <h3 className="text-xl font-semibold text-olive mb-2 hover:text-primary transition-colors">
                      {scheme.title}
                    </h3>
                    <p className="text-primary font-medium text-sm">
                      {scheme.ministry}
                    </p>
                  </div>
                  
                  <p className="text-olive/80 text-sm leading-relaxed">
                    {scheme.description}
                  </p>
                  
                  <div className="flex flex-wrap gap-2">
                    {scheme.tags.map((tag, index) => (
                      <Badge 
                        key={index} 
                        variant="outline" 
                        className="text-xs border-primary/30 text-primary"
                      >
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          {totalSchemes > 10 && (
            <div className="mt-8">
              <Pagination>
                <PaginationContent>
                  <PaginationItem>
                    <PaginationPrevious 
                      href="#" 
                      onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                    />
                  </PaginationItem>
                  {Array.from({ length: Math.ceil(totalSchemes / 10) }, (_, i) => i + 1)
                    .slice(0, 7)
                    .map((page) => (
                      <PaginationItem key={page}>
                        <PaginationLink 
                          href="#" 
                          isActive={page === currentPage}
                          onClick={() => setCurrentPage(page)}
                        >
                          {page}
                        </PaginationLink>
                      </PaginationItem>
                    ))}
                  {Math.ceil(totalSchemes / 10) > 7 && (
                    <>
                      <PaginationItem>
                        <span className="px-2">...</span>
                      </PaginationItem>
                      <PaginationItem>
                        <PaginationLink 
                          href="#" 
                          onClick={() => setCurrentPage(Math.ceil(totalSchemes / 10))}
                        >
                          {Math.ceil(totalSchemes / 10)}
                        </PaginationLink>
                      </PaginationItem>
                    </>
                  )}
                  <PaginationItem>
                    <PaginationNext 
                      href="#" 
                      onClick={() => setCurrentPage(prev => Math.min(Math.ceil(totalSchemes / 10), prev + 1))}
                    />
                  </PaginationItem>
                </PaginationContent>
              </Pagination>
            </div>
          )}
        </div>
      </section>
    </div>
  );
};

export default CategorySchemes;
