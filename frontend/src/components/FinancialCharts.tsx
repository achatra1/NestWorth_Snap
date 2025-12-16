import { useState } from 'react';
import { FiveYearProjection } from '@/types/financial';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  ChartLegend,
  ChartLegendContent,
} from '@/components/ui/chart';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
} from 'recharts';
import { TrendingUp, BarChart3, PieChartIcon } from 'lucide-react';

interface FinancialChartsProps {
  projection: FiveYearProjection;
}

export default function FinancialCharts({ projection }: FinancialChartsProps) {
  const [selectedYear, setSelectedYear] = useState<number>(0); // 0 = all years, 1-5 = specific year
  const [comparisonYear, setComparisonYear] = useState<number>(1);
  const [pieChartYear, setPieChartYear] = useState<number>(1); // For expense breakdown pie chart

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  // Prepare data for yearly overview charts
  const yearlyData = projection.yearlyProjections.map((year) => ({
    year: `Year ${year.year}`,
    yearNum: year.year,
    income: year.totalIncome,
    expenses: year.totalExpenses,
    netCashflow: year.netCashflow,
    savings: year.endingSavings,
    childcare: year.expenseBreakdown.childcare,
    housing: year.expenseBreakdown.housing,
    diapers: year.expenseBreakdown.diapers,
    food: year.expenseBreakdown.food,
    oneTime: year.expenseBreakdown.oneTime,
    miscellaneous: year.expenseBreakdown.miscellaneous,
    creditCard: year.expenseBreakdown.creditCard,
  }));

  // Prepare data for monthly view (filtered by selected year)
  const getMonthlyData = (year: number) => {
    if (year === 0) return []; // No monthly view for "all years"
    
    return projection.monthlyProjections
      .filter((m) => m.year === year)
      .map((month) => ({
        month: `M${month.monthOfYear}`,
        monthNum: month.monthOfYear,
        income: month.income.total,
        expenses: month.expenses.total,
        netCashflow: month.netCashflow,
        savings: month.cumulativeSavings,
        childcare: month.expenses.childcare,
        housing: month.expenses.housing,
      }));
  };

  // Prepare data for year-over-year comparison
  const getComparisonData = () => {
    const year1 = projection.yearlyProjections.find((y) => y.year === comparisonYear);
    const year2 = projection.yearlyProjections.find((y) => y.year === comparisonYear + 1);
    
    if (!year1 || !year2) return [];

    return [
      {
        category: 'Income',
        [`Year ${year1.year}`]: year1.totalIncome,
        [`Year ${year2.year}`]: year2.totalIncome,
      },
      {
        category: 'Expenses',
        [`Year ${year1.year}`]: year1.totalExpenses,
        [`Year ${year2.year}`]: year2.totalExpenses,
      },
      {
        category: 'Childcare',
        [`Year ${year1.year}`]: year1.expenseBreakdown.childcare,
        [`Year ${year2.year}`]: year2.expenseBreakdown.childcare,
      },
      {
        category: 'Housing',
        [`Year ${year1.year}`]: year1.expenseBreakdown.housing,
        [`Year ${year2.year}`]: year2.expenseBreakdown.housing,
      },
      {
        category: 'Net Cashflow',
        [`Year ${year1.year}`]: year1.netCashflow,
        [`Year ${year2.year}`]: year2.netCashflow,
      },
    ];
  };

  // Chart configurations
  const overviewConfig = {
    income: {
      label: 'Income',
      color: 'hsl(217, 91%, 35%)', // Dark blue
    },
    expenses: {
      label: 'Expenses',
      color: 'hsl(217, 91%, 70%)', // Light blue
    },
    savings: {
      label: 'Net Worth',
      color: 'hsl(262, 83%, 58%)', // Purple for net worth line
    },
  };

  const budgetBreakdownConfig = {
    housing: {
      label: 'Housing',
      color: 'hsl(200, 70%, 50%)',
    },
    childcare: {
      label: 'Childcare',
      color: 'hsl(280, 65%, 60%)',
    },
    food: {
      label: 'Food',
      color: 'hsl(120, 60%, 50%)',
    },
    savings: {
      label: 'Savings',
      color: 'hsl(142, 76%, 36%)',
    },
    other: {
      label: 'Other Expenses',
      color: 'hsl(30, 80%, 55%)',
    },
  };

  // Prepare budget breakdown data showing percentage of total budget
  const budgetBreakdownData = projection.yearlyProjections.map((year) => {
    const totalBudget = year.totalIncome; // Use income as total budget
    const savings = year.netCashflow > 0 ? year.netCashflow : 0;
    const otherExpenses =
      year.expenseBreakdown.diapers +
      year.expenseBreakdown.oneTime +
      year.expenseBreakdown.miscellaneous +
      year.expenseBreakdown.creditCard;

    return {
      year: `Year ${year.year}`,
      housing: ((year.expenseBreakdown.housing / totalBudget) * 100).toFixed(1),
      childcare: ((year.expenseBreakdown.childcare / totalBudget) * 100).toFixed(1),
      food: ((year.expenseBreakdown.food / totalBudget) * 100).toFixed(1),
      savings: ((savings / totalBudget) * 100).toFixed(1),
      other: ((otherExpenses / totalBudget) * 100).toFixed(1),
      // Store raw values for tooltip
      housingRaw: year.expenseBreakdown.housing,
      childcareRaw: year.expenseBreakdown.childcare,
      foodRaw: year.expenseBreakdown.food,
      savingsRaw: savings,
      otherRaw: otherExpenses,
    };
  });

  const expenseBreakdownConfig = {
    childcare: {
      label: 'Childcare',
      color: 'hsl(280, 65%, 60%)',
    },
    housing: {
      label: 'Housing',
      color: 'hsl(200, 70%, 50%)',
    },
    diapers: {
      label: 'Diapers',
      color: 'hsl(45, 93%, 47%)',
    },
    food: {
      label: 'Food',
      color: 'hsl(120, 60%, 50%)',
    },
    miscellaneous: {
      label: 'Miscellaneous',
      color: 'hsl(30, 80%, 55%)',
    },
    creditCard: {
      label: 'Credit Card',
      color: 'hsl(0, 70%, 50%)',
    },
  };

  // Prepare pie chart data for selected year
  const getPieChartData = (year: number) => {
    const yearData = projection.yearlyProjections.find((y) => y.year === year);
    if (!yearData) return [];

    const totalExpenses = yearData.totalExpenses;
    const data = [];

    if (yearData.expenseBreakdown.housing > 0) {
      data.push({
        name: 'Housing',
        value: yearData.expenseBreakdown.housing,
        percentage: ((yearData.expenseBreakdown.housing / totalExpenses) * 100).toFixed(1),
        color: expenseBreakdownConfig.housing.color,
      });
    }
    if (yearData.expenseBreakdown.childcare > 0) {
      data.push({
        name: 'Childcare',
        value: yearData.expenseBreakdown.childcare,
        percentage: ((yearData.expenseBreakdown.childcare / totalExpenses) * 100).toFixed(1),
        color: expenseBreakdownConfig.childcare.color,
      });
    }
    if (yearData.expenseBreakdown.diapers > 0) {
      data.push({
        name: 'Diapers',
        value: yearData.expenseBreakdown.diapers,
        percentage: ((yearData.expenseBreakdown.diapers / totalExpenses) * 100).toFixed(1),
        color: expenseBreakdownConfig.diapers.color,
      });
    }
    if (yearData.expenseBreakdown.food > 0) {
      data.push({
        name: 'Food',
        value: yearData.expenseBreakdown.food,
        percentage: ((yearData.expenseBreakdown.food / totalExpenses) * 100).toFixed(1),
        color: expenseBreakdownConfig.food.color,
      });
    }
    if (yearData.expenseBreakdown.miscellaneous > 0) {
      data.push({
        name: 'Miscellaneous',
        value: yearData.expenseBreakdown.miscellaneous,
        percentage: ((yearData.expenseBreakdown.miscellaneous / totalExpenses) * 100).toFixed(1),
        color: expenseBreakdownConfig.miscellaneous.color,
      });
    }
    if (yearData.expenseBreakdown.creditCard > 0) {
      data.push({
        name: 'Credit Card',
        value: yearData.expenseBreakdown.creditCard,
        percentage: ((yearData.expenseBreakdown.creditCard / totalExpenses) * 100).toFixed(1),
        color: expenseBreakdownConfig.creditCard.color,
      });
    }

    return data;
  };

  const monthlyData = selectedYear > 0 ? getMonthlyData(selectedYear) : [];
  const comparisonData = getComparisonData();

  return (
    <div className="space-y-6">
      {/* Year Selector */}
      <div className="flex items-center gap-4">
        <label className="text-sm font-medium">View:</label>
        <Select
          value={selectedYear.toString()}
          onValueChange={(value) => setSelectedYear(parseInt(value))}
        >
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="Select view" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="0">5-Year Overview</SelectItem>
            <SelectItem value="1">Year 1 (Monthly)</SelectItem>
            <SelectItem value="2">Year 2 (Monthly)</SelectItem>
            <SelectItem value="3">Year 3 (Monthly)</SelectItem>
            <SelectItem value="4">Year 4 (Monthly)</SelectItem>
            <SelectItem value="5">Year 5 (Monthly)</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="expenses">Expense Breakdown</TabsTrigger>
          <TabsTrigger value="budget">Budget Breakdown</TabsTrigger>
          <TabsTrigger value="comparison">Year Comparison</TabsTrigger>
        </TabsList>

        {/* Overview Tab - Net Worth with Income/Expense Bars */}
        <TabsContent value="overview">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                {selectedYear === 0 ? 'Net Worth Growth & Cash Flow' : `Year ${selectedYear} Monthly Net Worth & Cash Flow`}
              </CardTitle>
              <CardDescription>
                {selectedYear === 0
                  ? 'Track your net worth growth with income and expense trends over 5 years'
                  : `Monthly net worth progression with income and expenses for Year ${selectedYear}`}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ChartContainer config={overviewConfig} className="h-[133px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={selectedYear === 0 ? yearlyData : monthlyData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey={selectedYear === 0 ? 'year' : 'month'}
                      tickLine={false}
                      axisLine={false}
                    />
                    <YAxis
                      tickLine={false}
                      axisLine={false}
                      tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
                    />
                    <ChartTooltip
                      content={
                        <ChartTooltipContent
                          formatter={(value) => formatCurrency(value as number)}
                        />
                      }
                    />
                    <ChartLegend content={<ChartLegendContent />} />
                    <Bar dataKey="income" fill="var(--color-income)" />
                    <Bar dataKey="expenses" fill="var(--color-expenses)" />
                    <Line
                      type="monotone"
                      dataKey="savings"
                      stroke="var(--color-savings)"
                      strokeWidth={3}
                      dot={{ r: 5 }}
                    />
                  </BarChart>
                </ResponsiveContainer>
              </ChartContainer>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Expense Breakdown Tab - Pie Chart */}
        <TabsContent value="expenses">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <PieChartIcon className="w-5 h-5" />
                Budget Allocation by Category
              </CardTitle>
              <CardDescription>
                Your expense breakdown showing percentage allocation for each category
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="mb-4">
                <label className="text-sm font-medium mr-2">Select Year:</label>
                <Select
                  value={pieChartYear.toString()}
                  onValueChange={(value) => setPieChartYear(parseInt(value))}
                >
                  <SelectTrigger className="w-[200px] inline-flex">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">Year 1</SelectItem>
                    <SelectItem value="2">Year 2</SelectItem>
                    <SelectItem value="3">Year 3</SelectItem>
                    <SelectItem value="4">Year 4</SelectItem>
                    <SelectItem value="5">Year 5</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="flex items-center gap-8">
                <div className="flex-1">
                  <ResponsiveContainer width="100%" height={133}>
                    <PieChart>
                      <Pie
                        data={getPieChartData(pieChartYear)}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ name, percentage }) => `${name}: ${percentage}%`}
                        outerRadius={50}
                        fill="#8884d8"
                        dataKey="value"
                      >
                        {getPieChartData(pieChartYear).map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <ChartTooltip
                        content={({ active, payload }) => {
                          if (active && payload && payload.length) {
                            const data = payload[0].payload;
                            return (
                              <div className="bg-white p-2 border rounded shadow-sm">
                                <p className="font-semibold">{data.name}</p>
                                <p className="text-sm">{formatCurrency(data.value)}</p>
                                <p className="text-sm text-gray-600">{data.percentage}% of total</p>
                              </div>
                            );
                          }
                          return null;
                        }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
                <div className="flex-1 space-y-2">
                  <h4 className="font-semibold text-sm mb-3">Budget Allocation</h4>
                  {getPieChartData(pieChartYear).map((item, index) => (
                    <div key={index} className="flex items-center justify-between text-sm">
                      <div className="flex items-center gap-2">
                        <div
                          className="w-3 h-3 rounded-full"
                          style={{ backgroundColor: item.color }}
                        />
                        <span>{item.name}</span>
                      </div>
                      <div className="text-right">
                        <span className="font-medium">{item.percentage}%</span>
                        <span className="text-gray-500 ml-2 text-xs">
                          {formatCurrency(item.value)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Budget Breakdown Tab - Stacked Bar Chart */}
        <TabsContent value="budget">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5" />
                Budget Breakdown Over Time
              </CardTitle>
              <CardDescription>
                How your spending categories change as a percentage of total income each year
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ChartContainer config={budgetBreakdownConfig} className="h-[133px]">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={budgetBreakdownData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="year"
                      tickLine={false}
                      axisLine={false}
                    />
                    <YAxis
                      tickLine={false}
                      axisLine={false}
                      tickFormatter={(value) => `${value}%`}
                    />
                    <ChartTooltip
                      content={({ active, payload }) => {
                        if (active && payload && payload.length) {
                          const data = payload[0].payload;
                          return (
                            <div className="bg-white p-3 border rounded shadow-sm">
                              <p className="font-semibold mb-2">{data.year}</p>
                              {payload.map((entry: any, index: number) => (
                                <div key={index} className="flex justify-between gap-4 text-sm">
                                  <span style={{ color: entry.color }}>{entry.name}:</span>
                                  <span className="font-medium">
                                    {entry.value}% ({formatCurrency(data[`${entry.dataKey}Raw`])})
                                  </span>
                                </div>
                              ))}
                            </div>
                          );
                        }
                        return null;
                      }}
                    />
                    <ChartLegend content={<ChartLegendContent />} />
                    <Bar dataKey="housing" stackId="a" fill="var(--color-housing)" />
                    <Bar dataKey="childcare" stackId="a" fill="var(--color-childcare)" />
                    <Bar dataKey="food" stackId="a" fill="var(--color-food)" />
                    <Bar dataKey="other" stackId="a" fill="var(--color-other)" />
                    <Bar dataKey="savings" stackId="a" fill="var(--color-savings)" />
                  </BarChart>
                </ResponsiveContainer>
              </ChartContainer>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Year-over-Year Comparison Tab */}
        <TabsContent value="comparison">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5" />
                Year-over-Year Comparison
              </CardTitle>
              <CardDescription>
                Compare financial metrics between consecutive years
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="mb-4">
                <label className="text-sm font-medium mr-2">Compare:</label>
                <Select
                  value={comparisonYear.toString()}
                  onValueChange={(value) => setComparisonYear(parseInt(value))}
                >
                  <SelectTrigger className="w-[200px] inline-flex">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="1">Year 1 vs Year 2</SelectItem>
                    <SelectItem value="2">Year 2 vs Year 3</SelectItem>
                    <SelectItem value="3">Year 3 vs Year 4</SelectItem>
                    <SelectItem value="4">Year 4 vs Year 5</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <ChartContainer
                config={{
                  [`Year ${comparisonYear}`]: {
                    label: `Year ${comparisonYear}`,
                    color: 'hsl(217, 91%, 60%)',
                  },
                  [`Year ${comparisonYear + 1}`]: {
                    label: `Year ${comparisonYear + 1}`,
                    color: 'hsl(142, 76%, 36%)',
                  },
                }}
                className="h-[133px]"
              >
                <BarChart data={comparisonData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="category" tickLine={false} axisLine={false} />
                  <YAxis
                    tickLine={false}
                    axisLine={false}
                    tickFormatter={(value) => `$${(value / 1000).toFixed(0)}k`}
                  />
                  <ChartTooltip
                    content={
                      <ChartTooltipContent
                        formatter={(value) => formatCurrency(value as number)}
                      />
                    }
                  />
                  <ChartLegend content={<ChartLegendContent />} />
                  <Bar
                    dataKey={`Year ${comparisonYear}`}
                    fill={`var(--color-Year ${comparisonYear})`}
                  />
                  <Bar
                    dataKey={`Year ${comparisonYear + 1}`}
                    fill={`var(--color-Year ${comparisonYear + 1})`}
                  />
                </BarChart>
              </ChartContainer>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}