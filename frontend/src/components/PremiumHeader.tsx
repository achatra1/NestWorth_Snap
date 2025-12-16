import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Crown } from 'lucide-react';

export default function PremiumHeader() {
  const navigate = useNavigate();

  return (
    <div className="fixed top-20 right-4 z-40 print:hidden">
      <Button
        onClick={() => navigate('/premium')}
        className="bg-gradient-to-r from-yellow-500 to-amber-600 hover:from-yellow-600 hover:to-amber-700 text-white shadow-lg"
        size="sm"
      >
        <Crown className="w-4 h-4 mr-2" />
        Upgrade to Premium
      </Button>
    </div>
  );
}