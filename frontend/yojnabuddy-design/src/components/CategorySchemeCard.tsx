
import { ReactNode } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { useNavigate } from "react-router-dom";

interface CategorySchemeCardProps {
  id: string;
  title: string;
  schemeCount: number;
  icon: ReactNode;
  color: string;
}

const CategorySchemeCard = ({ id, title, schemeCount, icon, color }: CategorySchemeCardProps) => {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate(`/schemes/category/${id}`);
  };

  return (
    <Card 
      className="bg-white shadow-soft hover:shadow-medium transition-all duration-300 cursor-pointer transform hover:-translate-y-1 border-0"
      onClick={handleClick}
    >
      <CardContent className="p-6 text-center">
        <div 
          className="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4"
          style={{ backgroundColor: `${color}20` }}
        >
          <div style={{ color: color }}>
            {icon}
          </div>
        </div>
        
        <div className="mb-2">
          <span className="text-primary font-semibold text-lg">
            {schemeCount}
          </span>
          <span className="text-olive/60 text-sm ml-1">Schemes</span>
        </div>
        
        <h3 className="text-olive font-medium text-sm leading-tight">
          {title}
        </h3>
      </CardContent>
    </Card>
  );
};

export default CategorySchemeCard;
