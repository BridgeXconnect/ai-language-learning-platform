"use client"
import { useState, useEffect } from "react"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/enhanced-card"
import { useAuth } from "@/contexts/auth-context"

interface FunnelData {
  name: string;
  value: number;
  fill: string;
}

const initialData: FunnelData[] = [
  { name: 'Submitted', value: 100, fill: '#8884d8' },
  { name: 'Under Review', value: 80, fill: '#83a6ed' },
  { name: 'Generation', value: 60, fill: '#8dd1e1' },
  { name: 'Approved', value: 40, fill: '#82ca9d' },
  { name: 'Completed', value: 30, fill: '#a4de6c' },
];

export function CourseCreationFunnel() {
  const [data, setData] = useState<FunnelData[]>(initialData);
  const { fetchWithAuth } = useAuth()

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetchWithAuth('/api/dashboard/funnel');
        if (response.ok) {
          const apiData = await response.json();
          setData(apiData);
        }
      } catch (error) {
        console.error("Failed to fetch funnel data:", error);
      }
    };

    fetchData();
  }, [fetchWithAuth]);

  return (
    <Card variant="elevated">
      <CardHeader>
        <CardTitle>Course Creation Funnel</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart
            data={data}
            layout="vertical"
            margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" />
            <YAxis dataKey="name" type="category" />
            <Tooltip />
            <Legend />
            <Bar dataKey="value" name="Requests">
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.fill} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}