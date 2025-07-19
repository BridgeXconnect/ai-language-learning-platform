"use client"
import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/enhanced-card"
import { Button } from "@/components/ui/enhanced-button"
import { 
  ShieldCheck,
  SlidersHorizontal,
  BarChart3,
  GitBranch,
  CheckCircle,
  XCircle,
  AlertTriangle,
  Clock
} from "lucide-react"
import { useAuth } from "@/contexts/auth-context"

interface QualityGate {
  id: string;
  name: string;
  description: string;
  metric: string;
  threshold: number;
  enabled: boolean;
}

interface QualityPipeline {
  id: string;
  name: string;
  description: string;
  gates: QualityGate[];
}

export function QualityControlPipeline() {
  const [pipelines, setPipelines] = useState<QualityPipeline[]>([]);
  const { fetchWithAuth } = useAuth();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetchWithAuth('/api/quality/pipelines');
        if (response.ok) {
          const apiData = await response.json();
          setPipelines(apiData);
        }
      } catch (error) {
        console.error("Failed to fetch quality pipelines:", error);
      }
    };

    fetchData();
  }, [fetchWithAuth]);

  return (
    <Card variant="elevated">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <ShieldCheck className="h-5 w-5" />
          Quality Control Pipeline
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {pipelines.map((pipeline) => (
          <div key={pipeline.id} className="border rounded-lg p-4">
            <h4 className="font-semibold text-lg">{pipeline.name}</h4>
            <p className="text-sm text-muted-foreground mb-3">{pipeline.description}</p>
            <div className="space-y-2">
              {pipeline.gates.map((gate) => (
                <div key={gate.id} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                  <div className="flex items-center gap-2">
                    {gate.enabled ? <CheckCircle className="h-4 w-4 text-green-600" /> : <XCircle className="h-4 w-4 text-red-600" />}
                    <span className="font-medium text-sm">{gate.name}</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-muted-foreground">
                    <span>Threshold: {gate.threshold}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}