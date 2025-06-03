import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, ExternalLink } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import apiService, { Scheme } from '@/services/api';

const SchemeDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [scheme, setScheme] = useState<Scheme | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSchemeDetails = async () => {
      try {
        setLoading(true);
        const data = await apiService.getSchemeDetails(Number(id));
        setScheme(data);
      } catch (err) {
        setError('Failed to load scheme details. Please try again later.');
        console.error('Error fetching scheme details:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchSchemeDetails();
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-cream">
        <div className="container mx-auto py-16 px-4 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-olive">Loading scheme details...</p>
        </div>
      </div>
    );
  }

  if (error || !scheme) {
    return (
      <div className="min-h-screen bg-cream">
        <div className="container mx-auto py-16 px-4 text-center">
          <p className="text-red-500">{error || 'Scheme not found'}</p>
          <Button 
            variant="outline" 
            className="mt-4"
            onClick={() => navigate(-1)}
          >
            Go Back
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-cream">
      {/* Header */}
      <div className="bg-primary/5 py-8">
        <div className="container mx-auto px-4">
          <Button 
            variant="ghost" 
            className="mb-4"
            onClick={() => navigate(-1)}
          >
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          
          <h1 className="text-3xl md:text-4xl font-bold text-olive mb-4">
            {scheme.title}
          </h1>
          
          <div className="flex flex-wrap gap-2 mb-4">
            <Badge variant="secondary" className="text-sm">
              {scheme.scheme_type === 'central' ? 'Central Scheme' : 'State Scheme'}
            </Badge>
            <Badge variant="outline" className="text-sm">
              {scheme.ministry}
            </Badge>
          </div>
          
          {scheme.website && (
            <a 
              href={scheme.website} 
              target="_blank" 
              rel="noopener noreferrer"
              className="inline-flex items-center text-primary hover:underline"
            >
              <ExternalLink className="h-4 w-4 mr-2" />
              Official Website
            </a>
          )}
        </div>
      </div>

      {/* Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2">
            <Card className="mb-8">
              <CardHeader>
                <h2 className="text-2xl font-semibold text-olive">Overview</h2>
              </CardHeader>
              <CardContent>
                <p className="text-olive/80 leading-relaxed">
                  {scheme.description}
                </p>
              </CardContent>
            </Card>

            <Tabs defaultValue="eligibility" className="mb-8">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="eligibility">Eligibility</TabsTrigger>
                <TabsTrigger value="benefits">Benefits</TabsTrigger>
                <TabsTrigger value="documents">Documents</TabsTrigger>
              </TabsList>
              
              <TabsContent value="eligibility">
                <Card>
                  <CardContent className="pt-6">
                    <div className="prose prose-olive max-w-none">
                      {scheme.eligibility.split('\n').map((item, index) => (
                        <p key={index} className="mb-2">{item}</p>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
              
              <TabsContent value="benefits">
                <Card>
                  <CardContent className="pt-6">
                    <div className="prose prose-olive max-w-none">
                      {scheme.benefits.split('\n').map((item, index) => (
                        <p key={index} className="mb-2">{item}</p>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
              
              <TabsContent value="documents">
                <Card>
                  <CardContent className="pt-6">
                    <div className="prose prose-olive max-w-none">
                      {scheme.documents_required.split('\n').map((item, index) => (
                        <p key={index} className="mb-2">{item}</p>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>

            {scheme.application_process && (
              <Card className="mb-8">
                <CardHeader>
                  <h2 className="text-2xl font-semibold text-olive">Application Process</h2>
                </CardHeader>
                <CardContent>
                  <div className="prose prose-olive max-w-none">
                    {scheme.application_process.split('\n').map((item, index) => (
                      <p key={index} className="mb-2">{item}</p>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            <Card className="sticky top-8">
              <CardHeader>
                <h2 className="text-xl font-semibold text-olive">Quick Info</h2>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {scheme.helpline && (
                    <div>
                      <h3 className="text-sm font-medium text-olive/60 mb-1">Helpline</h3>
                      <p className="text-olive">{scheme.helpline}</p>
                    </div>
                  )}
                  
                  <div>
                    <h3 className="text-sm font-medium text-olive/60 mb-1">Tags</h3>
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
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SchemeDetail;
