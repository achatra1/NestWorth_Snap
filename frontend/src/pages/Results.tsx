import { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '@/contexts/AuthContext';
import { FiveYearProjection } from '@/types/financial';
import { getAssumptionExplanations } from '@/utils/expenseAssumptions';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { Download, Edit, AlertTriangle, Info, AlertCircle, Baby, TrendingUp, DollarSign, ChevronDown, ChevronRight, Home, Crown } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

export default function Results() {
  const navigate = useNavigate();
  const { profile, user, logout } = useAuth();
  const [projection, setProjection] = useState<FiveYearProjection | null>(null);
  const [aiSummary, setAiSummary] = useState<string>('');
  const [assumptionsSummary, setAssumptionsSummary] = useState<string>('');
  const [loading, setLoading] = useState(true);
  const [summaryLoading, setSummaryLoading] = useState(false);
  const [assumptionsLoading, setAssumptionsLoading] = useState(false);
  const [pdfLoading, setPdfLoading] = useState(false);
  const [expandedYears, setExpandedYears] = useState<Set<number>>(new Set());

  useEffect(() => {
    if (!profile) {
      navigate('/onboarding');
      return;
    }

    const fetchProjection = async () => {
      try {
        setLoading(true);
        
        // Call backend API to calculate projection
        const token = localStorage.getItem('nestworth_token');
        const response = await fetch('http://localhost:8000/api/v1/projections/calculate', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({}), // Use current user's profile
        });

        if (!response.ok) {
          throw new Error('Failed to calculate projection');
        }

        const calculatedProjection = await response.json();
        setProjection(calculatedProjection);

        // Generate AI summary from backend
        setSummaryLoading(true);
        try {
          const summaryResponse = await fetch('http://localhost:8000/api/v1/summaries/generate', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify({ projection: calculatedProjection }),
          });

          if (summaryResponse.ok) {
            const summaryData = await summaryResponse.json();
            setAiSummary(summaryData.summary);
          } else {
            console.error('Failed to generate AI summary');
            setAiSummary('*AI summary generation failed. Please try again later.*');
          }
        } catch (summaryError) {
          console.error('Error generating AI summary:', summaryError);
          setAiSummary('*AI summary generation failed. Please try again later.*');
        } finally {
          setSummaryLoading(false);
        }

        // Generate AI assumptions summary from backend
        setAssumptionsLoading(true);
        try {
          const assumptionsResponse = await fetch('http://localhost:8000/api/v1/summaries/generate-assumptions', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify({ assumptions: calculatedProjection.assumptions }),
          });

          if (assumptionsResponse.ok) {
            const assumptionsData = await assumptionsResponse.json();
            setAssumptionsSummary(assumptionsData.summary);
          } else {
            console.error('Failed to generate AI assumptions summary');
            setAssumptionsSummary('*Assumptions summary generation failed. Please try again later.*');
          }
        } catch (assumptionsError) {
          console.error('Error generating AI assumptions summary:', assumptionsError);
          setAssumptionsSummary('*Assumptions summary generation failed. Please try again later.*');
        } finally {
          setAssumptionsLoading(false);
        }
      } catch (error) {
        console.error('Error calculating projection:', error);
        // Fallback to showing error or redirecting
      } finally {
        setLoading(false);
      }
    };

    fetchProjection();
  }, [profile, navigate]);

  const handleDownloadPDF = async () => {
    if (!projection || !aiSummary) {
      console.error('Projection or AI summary not available');
      return;
    }

    try {
      setPdfLoading(true);
      const token = localStorage.getItem('nestworth_token');
      
      const response = await fetch('http://localhost:8000/api/v1/exports/pdf', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          projection: projection,
          summary: aiSummary,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate PDF');
      }

      // Get the PDF blob
      const blob = await response.blob();
      
      // Create a download link and trigger it
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `nestworth-plan-${new Date().toISOString().split('T')[0]}.pdf`;
      document.body.appendChild(a);
      a.click();
      
      // Cleanup
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error downloading PDF:', error);
      alert('Failed to generate PDF. Please try again.');
    } finally {
      setPdfLoading(false);
    }
  };

  const handleEditInputs = () => {
    navigate('/onboarding');
  };

  const toggleYear = (year: number) => {
    setExpandedYears(prev => {
      const newSet = new Set(prev);
      if (newSet.has(year)) {
        newSet.delete(year);
      } else {
        newSet.add(year);
      }
      return newSet;
    });
  };

  if (loading || !projection) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <Baby className="w-16 h-16 text-blue-600 animate-pulse mx-auto mb-4" />
          <p className="text-lg text-gray-600">Calculating your 5-year projection...</p>
        </div>
      </div>
    );
  }

  const renderSummaryContent = () => {
    if (summaryLoading) {
      return (
        <div className="flex items-center justify-center py-8">
          <div className="text-center">
            <Baby className="w-12 h-12 text-blue-600 animate-pulse mx-auto mb-3" />
            <p className="text-gray-600">Generating your personalized AI summary...</p>
          </div>
        </div>
      );
    }

    if (!aiSummary) {
      return (
        <div className="text-center py-8 text-gray-500">
          <p>AI summary not available</p>
        </div>
      );
    }

    return (
      <ReactMarkdown
        components={{
          table: ({ node, ...props }) => (
            <div className="overflow-x-auto my-4">
              <table className="min-w-full divide-y divide-gray-200 border" {...props} />
            </div>
          ),
          th: ({ node, ...props }) => (
            <th className="px-4 py-2 bg-gray-50 text-left text-xs font-medium text-gray-700 uppercase tracking-wider border" {...props} />
          ),
          td: ({ node, ...props }) => (
            <td className="px-4 py-2 text-sm text-gray-900 border" {...props} />
          ),
        }}
      >
        {aiSummary}
      </ReactMarkdown>
    );
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const criticalWarnings = projection.warnings.filter(w => w.severity === 'critical');
  const importantWarnings = projection.warnings.filter(w => w.severity === 'important');
  const infoWarnings = projection.warnings.filter(w => w.severity === 'informational');

  // All calculations are done in the backend - we just display the data
  // Total childcare includes: daycare/nanny + diapers + food + one-time + miscellaneous
  const totalChildcare = projection.yearlyProjections.reduce((sum, y) =>
    sum + y.expenseBreakdown.childcare + y.expenseBreakdown.diapers +
    y.expenseBreakdown.food + y.expenseBreakdown.oneTime +
    y.expenseBreakdown.miscellaneous, 0);

  // Helper function to get income breakdown for a year from backend data
  const getYearIncomeBreakdown = (year: number) => {
    const yearMonths = projection.monthlyProjections.filter(m => m.year === year);
    const partner1Total = yearMonths.reduce((sum, m) => sum + m.income.partner1, 0);
    const partner2Total = yearMonths.reduce((sum, m) => sum + m.income.partner2, 0);
    
    return {
      partner1: partner1Total,
      partner2: partner2Total,
      total: partner1Total + partner2Total,
    };
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <div className="bg-white border-b print:hidden">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Link to="/dashboard">
              <img
                src="/nestworth-logo.png"
                alt="NestWorth Logo"
                className="h-24 w-auto cursor-pointer hover:opacity-80 transition-opacity"
              />
            </Link>
            <div>
              <h1 className="text-xl font-bold text-gray-900">NestWorth</h1>
              <p className="text-sm text-gray-600">Welcome, {user?.name}</p>
            </div>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={handleEditInputs}>
              <Edit className="w-4 h-4 mr-2" />
              Edit Inputs
            </Button>
            <Button onClick={handleDownloadPDF} disabled={pdfLoading || !aiSummary}>
              <Download className="w-4 h-4 mr-2" />
              {pdfLoading ? 'Generating PDF...' : 'Download PDF'}
            </Button>
            <Button
              onClick={() => navigate('/premium')}
              className="bg-gradient-to-r from-yellow-500 to-amber-600 hover:from-yellow-600 hover:to-amber-700 text-white"
            >
              <Crown className="w-4 h-4 mr-2" />
              Upgrade to Premium
            </Button>
            <Button variant="ghost" onClick={logout}>
              Logout
            </Button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8 space-y-6">
        {/* Page Title */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            A 5-Year Financial Blueprint for Life With a New Baby
          </h1>
          <p className="text-lg text-gray-600">
            More freedom for the moments that matter
          </p>
        </div>

        {/* Executive Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-600">5-Year Total</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <DollarSign className="w-5 h-5 text-blue-600" />
                <p className="text-2xl font-bold">{formatCurrency(totalChildcare)}</p>
              </div>
              <p className="text-xs text-gray-500 mt-1">All childcare expenses</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-600">Monthly Average</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-green-600" />
                <p className="text-2xl font-bold">{formatCurrency(totalChildcare / 60)}</p>
              </div>
              <p className="text-xs text-gray-500 mt-1">Childcare costs over 60 months</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-600">Debt-to-Income Ratio</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-purple-600" />
                <p className="text-2xl font-bold">
                  {((projection.yearlyProjections.reduce((sum, y) => sum + y.totalExpenses, 0) /
                    projection.yearlyProjections.reduce((sum, y) => sum + y.totalIncome, 0)) * 100).toFixed(1)}%
                </p>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Total expenses vs. income over 5 years
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-gray-600">Household Networth over 5 years</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2">
                <DollarSign className="w-5 h-5 text-indigo-600" />
                <p className="text-2xl font-bold">
                  {formatCurrency(projection.yearlyProjections[4].endingSavings)}
                </p>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Increased from original savings buffer of {formatCurrency(profile.currentSavings)}
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Premium Upsell Banner */}
        <Alert className="border-blue-500 bg-gradient-to-r from-blue-50 to-indigo-50">
          <Info className="h-5 w-5 text-blue-600" />
          <AlertTitle className="text-blue-900 text-lg font-semibold">Your Baby Blueprint</AlertTitle>
          <AlertDescription className="text-blue-800">
            <p className="mb-3">
              Below is your Baby Blueprint — a first look at the financial impact of welcoming a child for the first 5 years of their life.
            </p>
            <p className="font-medium">
              Go Premium to unlock tailored planning recommendations, smart ways to save, and insights into financial support options available to your family.
            </p>
          </AlertDescription>
        </Alert>

        {/* Tabs */}
        <Tabs defaultValue="summary" className="space-y-4">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="summary">Financial Blueprint</TabsTrigger>
            <TabsTrigger value="breakdown">Detailed Breakdown</TabsTrigger>
            <TabsTrigger value="assumptions">Assumptions</TabsTrigger>
          </TabsList>

          <TabsContent value="summary">
            <Card>
              <CardHeader>
                <CardTitle>Your 5-Year Baby Budget Blueprint</CardTitle>
                <CardDescription>
                  A structured, realistic financial plan for your growing family
                </CardDescription>
              </CardHeader>
              <CardContent className="prose prose-sm max-w-none">
                {renderSummaryContent()}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="breakdown">
            <Card>
              <CardHeader>
                <CardTitle>Year-by-Year Financial Breakdown</CardTitle>
                <CardDescription>
                  Click any row to see detailed income and expense breakdown
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {projection.yearlyProjections.map((year) => {
                    const isExpanded = expandedYears.has(year.year);
                    const incomeBreakdown = getYearIncomeBreakdown(year.year);
                    
                    // Calculate expense categories
                    const householdExpenses = year.expenseBreakdown.housing;
                    const childcareExpenses =
                      year.expenseBreakdown.childcare +
                      year.expenseBreakdown.diapers +
                      year.expenseBreakdown.food +
                      year.expenseBreakdown.oneTime +
                      year.expenseBreakdown.miscellaneous;
                    
                    return (
                      <Collapsible key={year.year} open={isExpanded} onOpenChange={() => toggleYear(year.year)}>
                        <div className="border rounded-lg overflow-hidden">
                          <CollapsibleTrigger className="w-full">
                            <div className="flex items-center justify-between p-4 hover:bg-gray-50 cursor-pointer">
                              <div className="flex items-center gap-3">
                                {isExpanded ? (
                                  <ChevronDown className="w-5 h-5 text-gray-500" />
                                ) : (
                                  <ChevronRight className="w-5 h-5 text-gray-500" />
                                )}
                                <span className="font-semibold text-lg">Year {year.year}</span>
                              </div>
                              <div className="flex gap-8 text-sm">
                                <div className="text-right">
                                  <p className="text-gray-600">Income</p>
                                  <p className="font-semibold">{formatCurrency(year.totalIncome)}</p>
                                </div>
                                <div className="text-right">
                                  <p className="text-gray-600">Expenses</p>
                                  <p className="font-semibold">{formatCurrency(year.totalExpenses)}</p>
                                </div>
                                <div className="text-right">
                                  <p className="text-gray-600">Net Cashflow</p>
                                  <p className={`font-semibold ${year.netCashflow < 0 ? 'text-red-600' : 'text-green-600'}`}>
                                    {formatCurrency(year.netCashflow)}
                                  </p>
                                </div>
                                <div className="text-right">
                                  <p className="text-gray-600">Ending Savings</p>
                                  <p className="font-semibold">{formatCurrency(year.endingSavings)}</p>
                                </div>
                              </div>
                            </div>
                          </CollapsibleTrigger>
                          
                          <CollapsibleContent>
                            <div className="border-t bg-gray-50 p-6">
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                {/* Income Breakdown */}
                                <div>
                                  <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                                    <TrendingUp className="w-4 h-4 text-green-600" />
                                    Income Breakdown
                                  </h4>
                                  <div className="space-y-2 bg-white rounded-lg p-4 border">
                                    <div className="flex justify-between items-center">
                                      <span className="text-gray-600">Partner 1 Income</span>
                                      <span className="font-medium">{formatCurrency(incomeBreakdown.partner1)}</span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                      <span className="text-gray-600">Partner 2 Income</span>
                                      <span className="font-medium">{formatCurrency(incomeBreakdown.partner2)}</span>
                                    </div>
                                    <div className="pt-2 border-t flex justify-between items-center">
                                      <span className="font-semibold text-gray-900">Total Income</span>
                                      <span className="font-bold text-green-600">{formatCurrency(incomeBreakdown.total)}</span>
                                    </div>
                                    <p className="text-xs text-gray-500 mt-2">
                                      Monthly average: {formatCurrency(incomeBreakdown.total / 12)}
                                    </p>
                                  </div>
                                </div>

                                {/* Expense Breakdown */}
                                <div>
                                  <h4 className="font-semibold text-gray-900 mb-3 flex items-center gap-2">
                                    <DollarSign className="w-4 h-4 text-blue-600" />
                                    Expense Breakdown
                                  </h4>
                                  <div className="space-y-3 bg-white rounded-lg p-4 border">
                                    {/* Household Expenses */}
                                    <div>
                                      <div className="flex justify-between items-center mb-2">
                                        <span className="font-medium text-gray-900 flex items-center gap-2">
                                          <Home className="w-4 h-4 text-gray-600" />
                                          Household Expenses
                                        </span>
                                        <span className="font-semibold text-gray-900">{formatCurrency(householdExpenses)}</span>
                                      </div>
                                      <div className="pl-6 space-y-1">
                                        <div className="flex justify-between items-center text-sm">
                                          <span className="text-gray-600">Housing (Rent/Mortgage)</span>
                                          <span className="text-gray-700">{formatCurrency(year.expenseBreakdown.housing)}</span>
                                        </div>
                                        {year.expenseBreakdown.creditCard > 0 && (
                                          <div className="flex justify-between items-center text-sm">
                                            <span className="text-gray-600">Credit Card Payments</span>
                                            <span className="text-gray-700">{formatCurrency(year.expenseBreakdown.creditCard)}</span>
                                          </div>
                                        )}
                                      </div>
                                    </div>

                                    {/* Childcare Expenses */}
                                    <div className="pt-2 border-t">
                                      <div className="flex justify-between items-center mb-2">
                                        <span className="font-medium text-gray-900 flex items-center gap-2">
                                          <Baby className="w-4 h-4 text-purple-600" />
                                          Childcare Expenses
                                        </span>
                                        <span className="font-semibold text-gray-900">{formatCurrency(childcareExpenses)}</span>
                                      </div>
                                      <div className="pl-6 space-y-1">
                                        {year.expenseBreakdown.childcare > 0 && (
                                          <div className="space-y-0.5">
                                            <div className="flex justify-between items-center text-sm">
                                              <span className="text-gray-600">Childcare ({profile.childcarePreference})</span>
                                              <span className="text-gray-700">{formatCurrency(year.expenseBreakdown.childcare)}</span>
                                            </div>
                                            <div className="flex justify-between items-center text-xs text-gray-500 pl-4">
                                              <span>{formatCurrency(year.expenseBreakdown.childcare / 12)}/month × 12 months</span>
                                            </div>
                                          </div>
                                        )}
                                        {year.expenseBreakdown.diapers > 0 && (
                                          <div className="space-y-0.5">
                                            <div className="flex justify-between items-center text-sm">
                                              <span className="text-gray-600">Diapers & Wipes</span>
                                              <span className="text-gray-700">{formatCurrency(year.expenseBreakdown.diapers)}</span>
                                            </div>
                                            <div className="flex justify-between items-center text-xs text-gray-500 pl-4">
                                              <span>{formatCurrency(year.expenseBreakdown.diapers / 12)}/month × 12 months</span>
                                            </div>
                                          </div>
                                        )}
                                        {year.expenseBreakdown.food > 0 && (
                                          <div className="space-y-0.5">
                                            <div className="flex justify-between items-center text-sm">
                                              <span className="text-gray-600">Food (Formula/Baby Food)</span>
                                              <span className="text-gray-700">{formatCurrency(year.expenseBreakdown.food)}</span>
                                            </div>
                                            <div className="flex justify-between items-center text-xs text-gray-500 pl-4">
                                              <span>{formatCurrency(year.expenseBreakdown.food / 12)}/month × 12 months</span>
                                            </div>
                                          </div>
                                        )}
                                        {year.expenseBreakdown.oneTime > 0 && (
                                          <div className="flex justify-between items-center text-sm">
                                            <span className="text-gray-600">One-Time Items (Crib, Stroller, etc.)</span>
                                            <span className="text-gray-700">{formatCurrency(year.expenseBreakdown.oneTime)}</span>
                                          </div>
                                        )}
                                        {year.expenseBreakdown.miscellaneous > 0 && (
                                          <div className="space-y-0.5">
                                            <div className="flex justify-between items-center text-sm">
                                              <span className="text-gray-600">Miscellaneous (Toys, Books, etc.)</span>
                                              <span className="text-gray-700">{formatCurrency(year.expenseBreakdown.miscellaneous)}</span>
                                            </div>
                                            <div className="flex justify-between items-center text-xs text-gray-500 pl-4">
                                              <span>{formatCurrency(year.expenseBreakdown.miscellaneous / 12)}/month × 12 months</span>
                                            </div>
                                          </div>
                                        )}
                                      </div>
                                    </div>

                                    <div className="pt-2 border-t flex justify-between items-center">
                                      <span className="font-semibold text-gray-900">Total Expenses</span>
                                      <span className="font-bold text-blue-600">{formatCurrency(year.totalExpenses)}</span>
                                    </div>
                                    <p className="text-xs text-gray-500 mt-2">
                                      Monthly average: {formatCurrency(year.totalExpenses / 12)}
                                    </p>
                                  </div>
                                </div>
                              </div>

                              {/* Summary Stats */}
                              <div className="mt-4 grid grid-cols-3 gap-4">
                                <div className="bg-white rounded-lg p-4 border text-center">
                                  <p className="text-sm text-gray-600 mb-1">Net Cashflow</p>
                                  <p className={`text-xl font-bold ${year.netCashflow < 0 ? 'text-red-600' : 'text-green-600'}`}>
                                    {formatCurrency(year.netCashflow)}
                                  </p>
                                  <p className="text-xs text-gray-500 mt-1">
                                    {formatCurrency(year.netCashflow / 12)}/month
                                  </p>
                                </div>
                                <div className="bg-white rounded-lg p-4 border text-center">
                                  <p className="text-sm text-gray-600 mb-1">Savings Rate</p>
                                  <p className="text-xl font-bold text-indigo-600">
                                    {((year.netCashflow / year.totalIncome) * 100).toFixed(1)}%
                                  </p>
                                  <p className="text-xs text-gray-500 mt-1">
                                    of income saved
                                  </p>
                                </div>
                                <div className="bg-white rounded-lg p-4 border text-center">
                                  <p className="text-sm text-gray-600 mb-1">Ending Savings</p>
                                  <p className="text-xl font-bold text-purple-600">
                                    {formatCurrency(year.endingSavings)}
                                  </p>
                                  <p className="text-xs text-gray-500 mt-1">
                                    cumulative balance
                                  </p>
                                </div>
                              </div>
                            </div>
                          </CollapsibleContent>
                        </div>
                      </Collapsible>
                    );
                  })}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="assumptions">
            <Card>
              <CardHeader>
                <CardTitle>Our Assumptions</CardTitle>
                <CardDescription>
                  Transparency into how we calculated your projections
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Alert className="mb-6 border-indigo-500 bg-indigo-50">
                  <Info className="h-4 w-4 text-indigo-600" />
                  <AlertDescription className="text-indigo-900">
                    This blueprint is grounded in your selected assumptions during onboarding, location-specific cost data by ZIP code, and public government datasets that reflect real-world childcare costs. To customize or override assumptions and to conduct a scenario analysis, get personalized recommendations, subscribe to Premium.
                  </AlertDescription>
                </Alert>
              </CardContent>
              <CardHeader className="pt-0">
              </CardHeader>
              <CardContent className="space-y-4 pt-0">
                {assumptionsLoading ? (
                  <div className="flex items-center justify-center py-8">
                    <div className="text-center">
                      <Baby className="w-12 h-12 text-blue-600 animate-pulse mx-auto mb-3" />
                      <p className="text-gray-600">Generating assumptions summary...</p>
                    </div>
                  </div>
                ) : assumptionsSummary ? (
                  <div className="prose prose-sm max-w-none">
                    <ReactMarkdown>{assumptionsSummary}</ReactMarkdown>
                  </div>
                ) : (
                  <div className="text-center py-8 text-gray-500">
                    <p>Assumptions summary not available</p>
                  </div>
                )}

                <Alert className="mt-6">
                  <AlertTriangle className="h-4 w-4" />
                  <AlertTitle>Important Disclaimer</AlertTitle>
                  <AlertDescription>
                    These projections are estimates based on general assumptions and your inputs. 
                    This is not financial advice. Actual costs may vary significantly based on your 
                    specific circumstances, location, and choices. Please consult a financial advisor 
                    for personalized guidance.
                  </AlertDescription>
                </Alert>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}