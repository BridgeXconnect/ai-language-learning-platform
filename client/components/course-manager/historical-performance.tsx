"use client"
import { useState, useEffect } from "react"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/enhanced-card"
import { useAuth } from "@/contexts/auth-context"

interface HistoricalData {
  name: string;
  successRate: number;
  processingTime: number;
}

const initialData: HistoricalData[] = [
  { name: 'Jan', successRate: 90, processingTime: 15 },
  { name: 'Feb', successRate: 92, processingTime: 14 },
  { name: 'Mar', successRate: 88, processingTime: 16 },
  { name: 'Apr', successRate: 93, processingTime: 13 },
  { name: 'May', successRate: 95, processingTime: 12 },
  { name: 'Jun', successRate: 94, processingTime: 12 },
];

export function HistoricalPerformance() {
  const [data, setData] = useState<HistoricalData[]>(initialData);
  const { fetchWithAuth } = useAuth()

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetchWithAuth('/api/dashboard/historical');
        if (response.ok) {
          const apiData = await response.json();
          setData(apiData);
        }
      } catch (error) {
        console.error("Failed to fetch historical data:", error);
      }
    };

    fetchData();
  }, [fetchWithAuth]);

  return (
    <Card variant="elevated">
      <CardHeader>
        <CardTitle>Historical Performance</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="successRate" name="Success Rate (%)" stroke="#8884d8" />
            <Line type="monotone" dataKey="processingTime" name="Processing Time (min)" stroke="#82ca9d" />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}