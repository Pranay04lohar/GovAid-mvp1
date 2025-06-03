
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";

interface SchemeCardProps {
  title: string;
  description: string;
  category: string;
  id: string;
}

const SchemeCard = ({ title, description, category, id }: SchemeCardProps) => {
  return (
    <Card className="bg-white shadow-soft hover:shadow-medium transition-shadow h-full flex flex-col">
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <h3 className="text-lg font-semibold text-olive">{title}</h3>
          <span className="text-xs font-medium px-2 py-1 bg-accent/20 text-accent-foreground rounded-full">
            {category}
          </span>
        </div>
      </CardHeader>
      <CardContent className="flex-grow">
        <p className="text-olive/80 text-sm">{description}</p>
      </CardContent>
      <CardFooter className="pt-2">
        <Link to={`/schemes/${id}`} className="w-full">
          <Button 
            variant="outline" 
            className="w-full border-primary text-primary hover:bg-primary/5"
          >
            View Details
          </Button>
        </Link>
      </CardFooter>
    </Card>
  );
};

export default SchemeCard;
