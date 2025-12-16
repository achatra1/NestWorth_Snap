import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { FileText, UserCog } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';

export default function Dashboard() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const handleUpdateProfile = () => {
    navigate('/onboarding');
  };

  const handleReviewBlueprint = () => {
    navigate('/results');
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-4xl">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Welcome back, {user?.name || 'there'}!
          </h1>
          <p className="text-gray-600">
            What would you like to do today?
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6 mb-6">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={handleUpdateProfile}>
            <CardHeader>
              <div className="flex items-center justify-center w-16 h-16 bg-blue-100 rounded-full mb-4 mx-auto">
                <UserCog className="w-8 h-8 text-blue-600" />
              </div>
              <CardTitle className="text-center text-2xl">Update Profile</CardTitle>
              <CardDescription className="text-center">
                Modify your family information and financial details
              </CardDescription>
            </CardHeader>
            <CardContent className="text-center">
              <Button 
                onClick={handleUpdateProfile}
                className="w-full"
                size="lg"
              >
                Update Profile
              </Button>
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow cursor-pointer" onClick={handleReviewBlueprint}>
            <CardHeader>
              <div className="flex items-center justify-center w-16 h-16 bg-indigo-100 rounded-full mb-4 mx-auto">
                <FileText className="w-8 h-8 text-indigo-600" />
              </div>
              <CardTitle className="text-center text-2xl">Review Baby Blueprint</CardTitle>
              <CardDescription className="text-center">
                View your personalized 5-year financial projection
              </CardDescription>
            </CardHeader>
            <CardContent className="text-center">
              <Button 
                onClick={handleReviewBlueprint}
                className="w-full"
                size="lg"
                variant="secondary"
              >
                Review Blueprint
              </Button>
            </CardContent>
          </Card>
        </div>

        <div className="text-center">
          <Button 
            onClick={handleLogout}
            variant="outline"
            size="sm"
          >
            Logout
          </Button>
        </div>
      </div>
    </div>
  );
}