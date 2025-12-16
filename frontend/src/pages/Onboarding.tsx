import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { UserFinancialProfile } from '@/types/financial';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Progress } from '@/components/ui/progress';
import { Baby, DollarSign, MapPin, Calendar, Briefcase } from 'lucide-react';
import PremiumHeader from '@/components/PremiumHeader';

export default function Onboarding() {
  const navigate = useNavigate();
  const { user, profile, saveProfile } = useAuth();
  const [step, setStep] = useState(1);
  const totalSteps = 3;

  const [formData, setFormData] = useState({
    partner1Income: '',
    partner2Income: '',
    zipCode: '',
    dueDate: '',
    currentSavings: '',
    numberOfChildren: '',
    childcarePreference: 'daycare' as 'daycare' | 'nanny' | 'stay-at-home',
    partner1LeaveDuration: '',
    partner1LeavePercent: '',
    partner2LeaveDuration: '',
    partner2LeavePercent: '',
    monthlyHousingCost: '',
    monthlyCreditCardExpenses: '',
  });

  // Prepopulate form with existing profile data when component mounts or profile changes
  useEffect(() => {
    if (profile) {
      // Convert date string to YYYY-MM-DD format for input field
      const formatDateForInput = (dateString: string) => {
        try {
          const date = new Date(dateString);
          return date.toISOString().split('T')[0];
        } catch {
          return '';
        }
      };

      setFormData({
        partner1Income: profile.partner1Income?.toString() || '',
        partner2Income: profile.partner2Income?.toString() || '',
        zipCode: profile.zipCode || '',
        dueDate: formatDateForInput(profile.dueDate) || '',
        currentSavings: profile.currentSavings?.toString() || '',
        numberOfChildren: profile.numberOfChildren?.toString() || '',
        childcarePreference: profile.childcarePreference || 'daycare',
        partner1LeaveDuration: profile.partner1Leave?.durationWeeks?.toString() || '',
        partner1LeavePercent: profile.partner1Leave?.percentPaid?.toString() || '',
        partner2LeaveDuration: profile.partner2Leave?.durationWeeks?.toString() || '',
        partner2LeavePercent: profile.partner2Leave?.percentPaid?.toString() || '',
        monthlyHousingCost: profile.monthlyHousingCost?.toString() || '',
        monthlyCreditCardExpenses: profile.monthlyCreditCardExpenses?.toString() || '',
      });
    }
  }, [profile]);

  const updateField = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleNext = () => {
    if (step < totalSteps) {
      setStep(step + 1);
    }
  };

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validate all fields are filled
    if (!formData.partner1Income || !formData.partner2Income || !formData.zipCode ||
        !formData.dueDate || !formData.currentSavings || !formData.numberOfChildren ||
        !formData.partner1LeaveDuration || !formData.partner1LeavePercent ||
        !formData.partner2LeaveDuration || !formData.partner2LeavePercent ||
        !formData.monthlyHousingCost || !formData.monthlyCreditCardExpenses) {
      alert('Please fill in all fields');
      return;
    }

    // Check if user is authenticated
    if (!user) {
      alert('You must be logged in to save your profile. Please log in and try again.');
      navigate('/login');
      return;
    }

    // Create profile without userId - backend will add it from auth token
    const profileData = {
      partner1Income: parseFloat(formData.partner1Income),
      partner2Income: parseFloat(formData.partner2Income),
      zipCode: formData.zipCode,
      dueDate: formData.dueDate,
      currentSavings: parseFloat(formData.currentSavings),
      numberOfChildren: parseInt(formData.numberOfChildren),
      childcarePreference: formData.childcarePreference,
      partner1Leave: {
        durationWeeks: parseInt(formData.partner1LeaveDuration),
        percentPaid: parseInt(formData.partner1LeavePercent),
      },
      partner2Leave: {
        durationWeeks: parseInt(formData.partner2LeaveDuration),
        percentPaid: parseInt(formData.partner2LeavePercent),
      },
      monthlyHousingCost: parseFloat(formData.monthlyHousingCost),
      monthlyCreditCardExpenses: parseFloat(formData.monthlyCreditCardExpenses),
    };

    console.log('Submitting profile:', profileData);
    console.log('User:', user);

    const success = await saveProfile(profileData as UserFinancialProfile);
    if (success) {
      // Redirect to dashboard after saving profile
      navigate('/dashboard');
    } else {
      alert('Failed to save profile. Please check the browser console for details and try again.');
    }
  };

  const progress = (step / totalSteps) * 100;

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4 py-8">
      <PremiumHeader />
      <div className="max-w-2xl mx-auto">
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <Link to="/dashboard">
              <img
                src="/nestworth-logo.png"
                alt="NestWorth Logo"
                className="h-32 w-auto cursor-pointer hover:opacity-80 transition-opacity"
              />
            </Link>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Let's Build Your Baby Budget</h1>
          <p className="text-gray-600">Answer a few questions to get your personalized 5-year financial plan</p>
        </div>

        <div className="mb-6">
          <Progress value={progress} className="h-2" />
          <p className="text-sm text-gray-600 mt-2 text-center">Step {step} of {totalSteps}</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>
              {step === 1 && 'Income & Savings'}
              {step === 2 && 'Baby Details & Childcare'}
              {step === 3 && 'Parental Leave'}
            </CardTitle>
            <CardDescription>
              {step === 1 && 'Tell us about your household income and current financial situation'}
              {step === 2 && 'When is baby due and what are your childcare plans?'}
              {step === 3 && 'How much parental leave will each partner take?'}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {step === 1 && (
                <>
                  <div className="space-y-2">
                    <Label htmlFor="partner1Income" className="flex items-center gap-2">
                      <DollarSign className="w-4 h-4" />
                      Partner 1 Monthly Take-Home Income
                    </Label>
                    <Input
                      id="partner1Income"
                      type="number"
                      placeholder="5000"
                      value={formData.partner1Income}
                      onChange={(e) => updateField('partner1Income', e.target.value)}
                      required
                      min="0"
                      step="0.01"
                    />
                    <p className="text-sm text-gray-500">After taxes and insurance</p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="partner2Income" className="flex items-center gap-2">
                      <DollarSign className="w-4 h-4" />
                      Partner 2 Monthly Take-Home Income
                    </Label>
                    <Input
                      id="partner2Income"
                      type="number"
                      placeholder="4500"
                      value={formData.partner2Income}
                      onChange={(e) => updateField('partner2Income', e.target.value)}
                      required
                      min="0"
                      step="0.01"
                    />
                    <p className="text-sm text-gray-500">After taxes and insurance (enter 0 if single income)</p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="currentSavings" className="flex items-center gap-2">
                      <DollarSign className="w-4 h-4" />
                      Current Savings
                    </Label>
                    <Input
                      id="currentSavings"
                      type="number"
                      placeholder="10000"
                      value={formData.currentSavings}
                      onChange={(e) => updateField('currentSavings', e.target.value)}
                      required
                      min="0"
                      step="0.01"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="numberOfChildren" className="flex items-center gap-2">
                      <Baby className="w-4 h-4" />
                      How many children are you planning for in this blueprint?
                    </Label>
                    <Input
                      id="numberOfChildren"
                      type="number"
                      placeholder="1"
                      value={formData.numberOfChildren}
                      onChange={(e) => updateField('numberOfChildren', e.target.value)}
                      required
                      min="1"
                      max="10"
                    />
                    <p className="text-sm text-gray-500">Enter the number of children you're planning for</p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="monthlyHousingCost" className="flex items-center gap-2">
                      <DollarSign className="w-4 h-4" />
                      Monthly Housing Cost (Rent/Mortgage)
                    </Label>
                    <Input
                      id="monthlyHousingCost"
                      type="number"
                      placeholder="2000"
                      value={formData.monthlyHousingCost}
                      onChange={(e) => updateField('monthlyHousingCost', e.target.value)}
                      required
                      min="0"
                      step="0.01"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="monthlyCreditCardExpenses" className="flex items-center gap-2">
                      <DollarSign className="w-4 h-4" />
                      Average Monthly Credit Card Expenses
                    </Label>
                    <Input
                      id="monthlyCreditCardExpenses"
                      type="number"
                      placeholder="500"
                      value={formData.monthlyCreditCardExpenses}
                      onChange={(e) => updateField('monthlyCreditCardExpenses', e.target.value)}
                      required
                      min="0"
                      step="0.01"
                    />
                    <p className="text-sm text-gray-500">Your typical monthly credit card spending</p>
                  </div>
                </>
              )}

              {step === 2 && (
                <>
                  <div className="space-y-2">
                    <Label htmlFor="zipCode" className="flex items-center gap-2">
                      <MapPin className="w-4 h-4" />
                      ZIP Code
                    </Label>
                    <Input
                      id="zipCode"
                      type="text"
                      placeholder="10001"
                      value={formData.zipCode}
                      onChange={(e) => updateField('zipCode', e.target.value)}
                      required
                      pattern="[0-9]{5}"
                      maxLength={5}
                    />
                    <p className="text-sm text-gray-500">Used to estimate regional costs</p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="dueDate" className="flex items-center gap-2">
                      <Calendar className="w-4 h-4" />
                      Due Date / Baby's Birth Date
                    </Label>
                    <Input
                      id="dueDate"
                      type="date"
                      value={formData.dueDate}
                      onChange={(e) => updateField('dueDate', e.target.value)}
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="childcarePreference" className="flex items-center gap-2">
                      <Briefcase className="w-4 h-4" />
                      Childcare Preference
                    </Label>
                    <Select
                      value={formData.childcarePreference}
                      onValueChange={(value) => updateField('childcarePreference', value)}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="daycare">Daycare</SelectItem>
                        <SelectItem value="nanny">Nanny</SelectItem>
                        <SelectItem value="stay-at-home">Stay-at-Home Parent</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </>
              )}

              {step === 3 && (
                <>
                  <div className="space-y-4">
                    <h3 className="font-medium text-lg">Partner 1 Parental Leave</h3>
                    
                    <div className="space-y-2">
                      <Label htmlFor="partner1LeaveDuration">Duration (weeks)</Label>
                      <Input
                        id="partner1LeaveDuration"
                        type="number"
                        placeholder="12"
                        value={formData.partner1LeaveDuration}
                        onChange={(e) => updateField('partner1LeaveDuration', e.target.value)}
                        required
                        min="0"
                        max="52"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="partner1LeavePercent">Percent Paid (%)</Label>
                      <Input
                        id="partner1LeavePercent"
                        type="number"
                        placeholder="100"
                        value={formData.partner1LeavePercent}
                        onChange={(e) => updateField('partner1LeavePercent', e.target.value)}
                        required
                        min="0"
                        max="100"
                      />
                      <p className="text-sm text-gray-500">0% = unpaid, 100% = fully paid</p>
                    </div>
                  </div>

                  <div className="space-y-4 pt-4 border-t">
                    <h3 className="font-medium text-lg">Partner 2 Parental Leave</h3>
                    
                    <div className="space-y-2">
                      <Label htmlFor="partner2LeaveDuration">Duration (weeks)</Label>
                      <Input
                        id="partner2LeaveDuration"
                        type="number"
                        placeholder="12"
                        value={formData.partner2LeaveDuration}
                        onChange={(e) => updateField('partner2LeaveDuration', e.target.value)}
                        required
                        min="0"
                        max="52"
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="partner2LeavePercent">Percent Paid (%)</Label>
                      <Input
                        id="partner2LeavePercent"
                        type="number"
                        placeholder="60"
                        value={formData.partner2LeavePercent}
                        onChange={(e) => updateField('partner2LeavePercent', e.target.value)}
                        required
                        min="0"
                        max="100"
                      />
                      <p className="text-sm text-gray-500">0% = unpaid, 100% = fully paid</p>
                    </div>
                  </div>
                </>
              )}

              <div className="flex gap-4 pt-4">
                {step > 1 && (
                  <Button type="button" variant="outline" onClick={handleBack} className="flex-1">
                    Back
                  </Button>
                )}
                
                {step < totalSteps ? (
                  <Button type="button" onClick={handleNext} className="flex-1">
                    Next
                  </Button>
                ) : (
                  <Button type="submit" className="flex-1">
                    Generate My Plan
                  </Button>
                )}
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}