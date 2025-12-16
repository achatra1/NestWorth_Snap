import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';

export default function Premium() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-4xl">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Premium Features
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            {/* New Features loading, stay tuned */}
            New Features loading, stay tuned
          </p>
          <Button
            onClick={() => navigate('/dashboard')}
            variant="outline"
            className="gap-2"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Dashboard
          </Button>
        </div>
      </div>
    </div>
  );
}