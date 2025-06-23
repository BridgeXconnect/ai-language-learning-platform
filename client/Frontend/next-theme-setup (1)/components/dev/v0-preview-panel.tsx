"use client";

import React, { useState, useEffect, useRef } from 'react';
import { 
  previewManager, 
  PreviewSession, 
  PreviewUpdate 
} from '@/lib/preview-manager';
import { v0Api, V0GenerationResponse } from '@/lib/v0-api';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Play, 
  Pause, 
  RefreshCw, 
  Download, 
  Code, 
  Eye, 
  Smartphone, 
  Tablet, 
  Monitor,
  Loader2 
} from 'lucide-react';

interface V0PreviewPanelProps {
  initialPrompt?: string;
  userRole?: string;
  onDeploy?: (filePath: string) => void;
}

export function V0PreviewPanel({ 
  initialPrompt = '', 
  userRole = 'developer',
  onDeploy 
}: V0PreviewPanelProps) {
  const [prompt, setPrompt] = useState(initialPrompt);
  const [generation, setGeneration] = useState<V0GenerationResponse | null>(null);
  const [session, setSession] = useState<PreviewSession | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isDeploying, setIsDeploying] = useState(false);
  const [previewDevice, setPreviewDevice] = useState<'mobile' | 'tablet' | 'desktop'>('desktop');
  const [updates, setUpdates] = useState<PreviewUpdate[]>([]);
  const iframeRef = useRef<HTMLIFrameElement>(null);

  const handleGenerate = async () => {
    if (!prompt.trim()) return;

    setIsGenerating(true);
    setUpdates([]);

    try {
      const result = await previewManager.generateWithPreview(
        prompt,
        userRole,
        handlePreviewUpdate
      );

      setGeneration(result.generation);
      setSession(result.session);
    } catch (error) {
      console.error('Generation failed:', error);
      // Show error toast
    } finally {
      setIsGenerating(false);
    }
  };

  const handlePreviewUpdate = (update: PreviewUpdate) => {
    setUpdates(prev => [...prev, update]);
    
    if (update.type === 'preview_ready' && update.previewUrl) {
      // Refresh iframe with new preview URL
      if (iframeRef.current) {
        iframeRef.current.src = update.previewUrl;
      }
    }
  };

  const handleUpdate = async () => {
    if (!generation || !prompt.trim()) return;

    setIsGenerating(true);

    try {
      const updatedGeneration = await previewManager.updateAndPreview(
        generation.id,
        prompt,
        { user_role: userRole }
      );

      setGeneration(updatedGeneration);
    } catch (error) {
      console.error('Update failed:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDeploy = async () => {
    if (!generation) return;

    setIsDeploying(true);

    try {
      // For demo purposes, deploying to components directory
      const targetPath = `components/${userRole}/${generation.id}.tsx`;
      
      const result = await previewManager.deployPreviewedComponent(
        generation.id,
        targetPath,
        {
          backup_existing: true,
          run_tests: true,
        }
      );

      if (result.success && onDeploy) {
        onDeploy(result.file_path);
      }
    } catch (error) {
      console.error('Deployment failed:', error);
    } finally {
      setIsDeploying(false);
    }
  };

  const handleStopPreview = async () => {
    if (generation) {
      await previewManager.stopPreview(generation.id);
      setSession(null);
    }
  };

  const getDeviceClass = () => {
    switch (previewDevice) {
      case 'mobile':
        return 'w-[375px] h-[667px]';
      case 'tablet':
        return 'w-[768px] h-[1024px]';
      case 'desktop':
      default:
        return 'w-full h-full';
    }
  };

  useEffect(() => {
    return () => {
      // Cleanup on unmount
      if (generation) {
        previewManager.stopPreview(generation.id);
      }
    };
  }, [generation]);

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="border-b p-4">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">V0 Component Preview</h2>
          <div className="flex items-center gap-2">
            {session && (
              <Badge 
                variant={session.status === 'active' ? 'default' : 'secondary'}
              >
                {session.status}
              </Badge>
            )}
          </div>
        </div>
      </div>

      <div className="flex-1 flex">
        {/* Left Panel - Controls */}
        <div className="w-1/3 border-r flex flex-col">
          <div className="p-4 border-b">
            <label className="text-sm font-medium mb-2 block">
              Component Prompt
            </label>
            <Textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="Describe the component you want to generate..."
              className="min-h-[100px] mb-4"
            />

            <div className="flex gap-2">
              {!generation ? (
                <Button 
                  onClick={handleGenerate} 
                  disabled={isGenerating || !prompt.trim()}
                  className="flex-1"
                >
                  {isGenerating ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Generating...
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4 mr-2" />
                      Generate
                    </>
                  )}
                </Button>
              ) : (
                <>
                  <Button 
                    onClick={handleUpdate} 
                    disabled={isGenerating}
                    variant="outline"
                    size="sm"
                  >
                    {isGenerating ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <RefreshCw className="w-4 h-4" />
                    )}
                  </Button>
                  <Button 
                    onClick={handleDeploy} 
                    disabled={isDeploying}
                    size="sm"
                  >
                    {isDeploying ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Download className="w-4 h-4" />
                    )}
                  </Button>
                  <Button 
                    onClick={handleStopPreview} 
                    variant="outline"
                    size="sm"
                  >
                    <Pause className="w-4 h-4" />
                  </Button>
                </>
              )}
            </div>
          </div>

          {/* Device Controls */}
          {session && (
            <div className="p-4 border-b">
              <label className="text-sm font-medium mb-2 block">
                Preview Device
              </label>
              <div className="flex gap-1">
                <Button
                  variant={previewDevice === 'mobile' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setPreviewDevice('mobile')}
                >
                  <Smartphone className="w-4 h-4" />
                </Button>
                <Button
                  variant={previewDevice === 'tablet' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setPreviewDevice('tablet')}
                >
                  <Tablet className="w-4 h-4" />
                </Button>
                <Button
                  variant={previewDevice === 'desktop' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setPreviewDevice('desktop')}
                >
                  <Monitor className="w-4 h-4" />
                </Button>
              </div>
            </div>
          )}

          {/* Generation Info */}
          {generation && (
            <div className="p-4 border-b">
              <h3 className="text-sm font-medium mb-2">Generation Info</h3>
              <div className="text-xs space-y-1 text-muted-foreground">
                <div>ID: {generation.id}</div>
                <div>Status: {generation.status}</div>
                <div>Created: {new Date(generation.created_at).toLocaleTimeString()}</div>
              </div>
            </div>
          )}

          {/* Updates Log */}
          <div className="flex-1 p-4">
            <h3 className="text-sm font-medium mb-2">Live Updates</h3>
            <div className="space-y-2 max-h-[200px] overflow-y-auto">
              {updates.map((update, index) => (
                <div key={index} className="text-xs p-2 bg-muted rounded">
                  <div className="font-medium">{update.type}</div>
                  {update.error && (
                    <div className="text-destructive">{update.error}</div>
                  )}
                  <div className="text-muted-foreground">
                    {new Date().toLocaleTimeString()}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Panel - Preview */}
        <div className="flex-1 flex flex-col">
          {session ? (
            <Tabs defaultValue="preview" className="flex-1 flex flex-col">
              <TabsList className="mx-4 mt-4">
                <TabsTrigger value="preview">
                  <Eye className="w-4 h-4 mr-2" />
                  Preview
                </TabsTrigger>
                <TabsTrigger value="code">
                  <Code className="w-4 h-4 mr-2" />
                  Code
                </TabsTrigger>
              </TabsList>

              <TabsContent value="preview" className="flex-1 p-4">
                <div className="h-full flex items-center justify-center bg-muted/20">
                  <div className={`${getDeviceClass()} border rounded-lg bg-white shadow-lg overflow-hidden`}>
                    {session.previewUrl ? (
                      <iframe
                        ref={iframeRef}
                        src={session.previewUrl}
                        className="w-full h-full"
                        title="Component Preview"
                      />
                    ) : (
                      <div className="flex items-center justify-center h-full">
                        <Loader2 className="w-8 h-8 animate-spin" />
                      </div>
                    )}
                  </div>
                </div>
              </TabsContent>

              <TabsContent value="code" className="flex-1 p-4">
                <Card className="h-full">
                  <CardHeader>
                    <CardTitle className="text-sm">Generated Code</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {generation?.component_code ? (
                      <pre className="text-xs bg-muted p-4 rounded overflow-auto max-h-[400px]">
                        <code>{generation.component_code}</code>
                      </pre>
                    ) : (
                      <div className="flex items-center justify-center h-[200px] text-muted-foreground">
                        Code will appear here once generation is complete
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          ) : (
            <div className="flex-1 flex items-center justify-center text-muted-foreground">
              <div className="text-center">
                <Play className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>Enter a prompt and click Generate to start creating components</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}