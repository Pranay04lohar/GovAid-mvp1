
import { ReactNode } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import { useNavigate } from "react-router-dom";

interface CategoryCardProps {
  title: string;
  description: string;
  icon: ReactNode;
  color: string;
}

const CategoryCard = ({ title, description, icon, color }: CategoryCardProps) => {
  const navigate = useNavigate();

  const handleExplore = () => {
    if (title === "Government Schemes") {
      navigate("/schemes");
    } else if (title === "Legal Help") {
      navigate("/legal-help");
    } else if (title === "Documentation Assistance") {
      navigate("/documentation-assistance");
    } else {
      // Handle other categories as needed
      console.log(`Exploring ${title}`);
    }
  };

  return (
    <Card className="bg-white shadow-medium hover:shadow-lg transition-shadow border-t-4 h-full flex flex-col" style={{ borderTopColor: color }}>
      <CardHeader className="pt-6">
        <div className="flex items-center gap-4">
          <div 
            className="w-12 h-12 rounded-full flex items-center justify-center"
            style={{ backgroundColor: `${color}20` }}
          >
            {icon}
          </div>
          <h3 className="text-xl font-semibold text-olive">{title}</h3>
        </div>
      </CardHeader>
      <CardContent className="flex-grow">
        <p className="text-olive/80">{description}</p>
      </CardContent>
      <CardFooter className="pt-2 pb-6">
        <Button 
          className="w-full"
          style={{ backgroundColor: color, color: '#FDFCFB' }}
          variant="default"
          onClick={handleExplore}
        >
          Explore {title}
        </Button>
      </CardFooter>
    </Card>
  );
};

export default CategoryCard;
