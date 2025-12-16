import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';

export default function Index() {
  const navigate = useNavigate();
  const { isAuthenticated, profile } = useAuth();

  useEffect(() => {
    if (isAuthenticated) {
      if (profile) {
        navigate('/results');
      } else {
        navigate('/onboarding');
      }
    } else {
      navigate('/');
    }
  }, [isAuthenticated, profile, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="text-center">
        <p className="text-lg text-gray-600">Loading...</p>
      </div>
    </div>
  );
}