"use client";

import React, { useState, useEffect } from 'react';
import { V0PreviewPanel } from '@/components/dev/v0-preview-panel';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { 
  Code2, 
  Eye, 
  FileText, 
  GitBranch, 
  Play, 
  Zap,
  Clock,
  CheckCircle 
} from 'lucide-react';

interface Story {
  id: string;
  title: string;
  status: 'draft' | 'approved' | 'in_progress' | 'done';
  content: string;
  assignedComponents?: string[];
}

interface V0Session {
  storyId: string;
  generationId: string;
  status: 'active' | 'completed' | 'deployed';
  componentName: string;
  previewUrl?: string;
}

export default function DevDashboard() {
  const [activeStory, setActiveStory] = useState<Story | null>(null);
  const [stories, setStories] = useState<Story[]>([]);
  const [v0Sessions, setV0Sessions] = useState<V0Session[]>([]);
  const [selectedPrompt, setSelectedPrompt] = useState('');

  // Mock data - in real app, this would come from your API
  useEffect(() => {
    setStories([
      {
        id: 'story-1-1',
        title: 'Client Information Capture Form',
        status: 'approved',
        content: `# Story 1.1: Client Information Capture

**Status:** Approved

## User Story
**As a** sales representative  
**I want to** input comprehensive client information including company details, industry, and contact information  
**So that** the course generation system has all necessary context for customization  

## Acceptance Criteria
- [ ] Form includes fields for company name, industry, size, primary contact
- [ ] Input validation ensures required fields are completed
- [ ] Data is stored securely and associated with the request
- [ ] Form follows the design system (blue/indigo theme)
- [ ] Responsive design for mobile and desktop
- [ ] Loading states and error handling

## Technical Notes
- Use shadcn/ui form components
- Implement proper form validation with zod
- Connect to sales API endpoints
- Follow WCAG accessibility guidelines`,
        assignedComponents: ['ClientInfoForm']
      },
      {
        id: 'story-2-1',
        title: 'AI Course Generation Wizard',
        status: 'in_progress',
        content: `# Story 2.1: AI-Powered Curriculum Design

**Status:** InProgress

## User Story
**As a** Course Manager  
**I want** the system to automatically generate structured curricula based on client requirements  
**So that** I can review and approve courses without manual curriculum development  

## Acceptance Criteria
- [ ] Multi-step wizard interface
- [ ] Integration with V0 for UI generation
- [ ] Real-time progress indicators
- [ ] WebSocket updates for generation status
- [ ] CEFR level configuration options

## Technical Notes
- Use V0 API for component generation
- Implement WebSocket for real-time updates
- Connect to AI service endpoints`,
        assignedComponents: ['CourseGenerationWizard', 'ProgressTracker']
      }
    ]);
  }, []);

  const handleStorySelect = (story: Story) => {
    setActiveStory(story);
    // Generate a V0 prompt based on the story content
    const prompt = generateV0PromptFromStory(story);
    setSelectedPrompt(prompt);
  };

  const generateV0PromptFromStory = (story: Story): string => {
    // Extract key information from story
    const userStoryMatch = story.content.match(/\*\*As a\*\* (.+?)\s+\*\*I want\*\* (.+?)\s+\*\*So that\*\* ([\s\S]+?)(?:\n\n|\*\*|$)/);
    
    if (!userStoryMatch) {
      return `Create a React component for: ${story.title}`;
    }

    const [, asA, iWant, soThat] = userStoryMatch;
    
    return `Create a modern ${story.title} component for a ${asA} in an AI language learning platform.

Requirements:
- ${iWant}
- ${soThat}
- Use Next.js 14+ with TypeScript
- Use Tailwind CSS and shadcn/ui components
- Follow blue/indigo design system
- Include proper loading states and error handling
- Make it responsive and accessible
- Include form validation where applicable

The component should be professional, modern, and suitable for an enterprise SaaS platform.`;
  };

  const handleV0Deploy = (filePath: string) => {
    // Handle successful deployment
    console.log('Component deployed to:', filePath);
    // Update story status, etc.
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft': return 'bg-gray-500';
      case 'approved': return 'bg-blue-500';
      case 'in_progress': return 'bg-yellow-500';
      case 'done': return 'bg-green-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <div className="border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="flex h-16 items-center px-6">
          <div className="flex items-center space-x-4">
            <Code2 className="h-6 w-6" />
            <div>
              <h1 className="text-lg font-semibold">Dev Dashboard</h1>
              <p className="text-sm text-muted-foreground">
                BMAD + V0 Integration
              </p>
            </div>
          </div>
          <div className="ml-auto flex items-center space-x-4">
            <Badge variant="outline" className="flex items-center gap-1">
              <Zap className="h-3 w-3" />
              V0 Enabled
            </Badge>
          </div>
        </div>
      </div>

      <div className="flex-1 flex">
        {/* Left Sidebar - Stories */}
        <div className="w-80 border-r bg-muted/30">
          <div className="p-4 border-b">
            <h2 className="font-semibold text-sm">Active Stories</h2>
            <p className="text-xs text-muted-foreground mt-1">
              Select a story to start development
            </p>
          </div>
          
          <div className="p-2 space-y-2">
            {stories.map((story) => (
              <Card 
                key={story.id} 
                className={`cursor-pointer transition-colors hover:bg-accent ${
                  activeStory?.id === story.id ? 'ring-2 ring-primary' : ''
                }`}
                onClick={() => handleStorySelect(story)}
              >
                <CardContent className="p-3">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-sm font-medium line-clamp-2">
                        {story.title}
                      </h3>
                      <p className="text-xs text-muted-foreground mt-1">
                        {story.id}
                      </p>
                    </div>
                    <Badge 
                      variant="secondary" 
                      className={`ml-2 ${getStatusColor(story.status)} text-white`}
                    >
                      {story.status}
                    </Badge>
                  </div>
                  
                  {story.assignedComponents && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      {story.assignedComponents.map((component) => (
                        <Badge key={component} variant="outline" className="text-xs">
                          {component}
                        </Badge>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            ))}
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 flex flex-col">
          {activeStory ? (
            <Tabs defaultValue="develop" className="flex-1 flex flex-col">
              <TabsList className="mx-4 mt-4">
                <TabsTrigger value="story">
                  <FileText className="w-4 h-4 mr-2" />
                  Story
                </TabsTrigger>
                <TabsTrigger value="develop">
                  <Code2 className="w-4 h-4 mr-2" />
                  Develop
                </TabsTrigger>
                <TabsTrigger value="preview">
                  <Eye className="w-4 h-4 mr-2" />
                  V0 Preview
                </TabsTrigger>
              </TabsList>

              <TabsContent value="story" className="flex-1 p-4">
                <Card className="h-full">
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      {activeStory.title}
                      <Badge className={getStatusColor(activeStory.status)}>
                        {activeStory.status}
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <pre className="whitespace-pre-wrap text-sm">
                      {activeStory.content}
                    </pre>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="develop" className="flex-1 p-4">
                <div className="h-full space-y-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base">Development Actions</CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <Button className="justify-start" onClick={() => {
                          // Switch to V0 Preview tab
                          const previewTab = document.querySelector('[value="preview"]') as HTMLButtonElement;
                          previewTab?.click();
                        }}>
                          <Zap className="w-4 h-4 mr-2" />
                          Generate with V0
                        </Button>
                        <Button variant="outline" className="justify-start">
                          <GitBranch className="w-4 h-4 mr-2" />
                          Create Branch
                        </Button>
                        <Button variant="outline" className="justify-start">
                          <Play className="w-4 h-4 mr-2" />
                          Run Tests
                        </Button>
                        <Button variant="outline" className="justify-start">
                          <CheckCircle className="w-4 h-4 mr-2" />
                          Mark Complete
                        </Button>
                      </div>
                      
                      <div>
                        <label className="text-sm font-medium">Custom V0 Prompt</label>
                        <Textarea
                          value={selectedPrompt}
                          onChange={(e) => setSelectedPrompt(e.target.value)}
                          className="mt-2"
                          rows={6}
                          placeholder="Modify the auto-generated prompt or write your own..."
                        />
                      </div>
                    </CardContent>
                  </Card>
                </div>
              </TabsContent>

              <TabsContent value="preview" className="flex-1">
                <V0PreviewPanel
                  initialPrompt={selectedPrompt}
                  userRole="developer"
                  onDeploy={handleV0Deploy}
                />
              </TabsContent>
            </Tabs>
          ) : (
            <div className="flex-1 flex items-center justify-center text-muted-foreground">
              <div className="text-center">
                <Code2 className="w-16 h-16 mx-auto mb-4 opacity-20" />
                <h3 className="text-lg font-medium mb-2">No Story Selected</h3>
                <p>Select a story from the sidebar to start development</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}