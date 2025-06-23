import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  CheckCircle, 
  Clock, 
  AlertCircle, 
  BookOpen,
  FileText,
  Brain,
  Zap,
  Loader2,
  Wifi,
  WifiOff
} from 'lucide-react';
import { aiAPI } from '../../services/api';
import { useGenerationStatus } from '../../services/websocket';

const GenerationProgress = ({ job, onComplete }) => {
  const [currentStage, setCurrentStage] = useState(0);
  const [fallbackPolling, setFallbackPolling] = useState(false);
  
  // Use WebSocket for real-time updates
  const { 
    status: wsStatus, 
    progress: wsProgress, 
    logs: wsLogs 
  } = useGenerationStatus(job?.job_id);
  
  // Fallback state for polling
  const [fallbackStatus, setFallbackStatus] = useState(null);
  const [fallbackProgress, setFallbackProgress] = useState(0);
  const [fallbackLogs, setFallbackLogs] = useState([]);

  const stages = [
    { 
      id: 'analyzing', 
      name: 'Analyzing Documents', 
      icon: FileText,
      description: 'Processing uploaded documents and extracting key information'
    },
    { 
      id: 'structuring', 
      name: 'Structuring Curriculum', 
      icon: BookOpen,
      description: 'Creating course structure based on requirements and content'
    },
    { 
      id: 'generating', 
      name: 'Generating Content', 
      icon: Brain,
      description: 'Creating lessons, exercises, and assessments using AI'
    },
    { 
      id: 'optimizing', 
      name: 'Optimizing Course', 
      icon: Zap,
      description: 'Fine-tuning content for learning effectiveness'
    }
  ];

  // Use WebSocket data if available, otherwise fallback to polling
  const status = wsStatus || fallbackStatus;
  const progress = wsProgress || fallbackProgress;
  const logs = wsLogs.length > 0 ? wsLogs : fallbackLogs;

  useEffect(() => {
    if (job?.job_id) {
      // Start fallback polling after 5 seconds if no WebSocket updates
      const fallbackTimer = setTimeout(() => {
        if (!wsStatus && !wsProgress) {
          setFallbackPolling(true);
          pollStatus();
        }
      }, 5000);

      return () => clearTimeout(fallbackTimer);
    }
  }, [job?.job_id, wsStatus, wsProgress]);

  // Handle completion
  useEffect(() => {
    if (status === 'completed') {
      handleCompletion();
    }
  }, [status]);

  const handleCompletion = async () => {
    try {
      const resultResponse = await aiAPI.getGenerationResult(job.job_id);
      onComplete(resultResponse.data);
    } catch (error) {
      console.error('Error fetching generation result:', error);
    }
  };

  const pollStatus = async () => {
    if (!job?.job_id || !fallbackPolling) return;

    const interval = setInterval(async () => {
      try {
        const response = await aiAPI.getGenerationStatus(job.job_id);
        const statusData = response.data;
        
        setFallbackStatus(statusData.status);
        setFallbackProgress(statusData.progress || 0);
        
        // Update current stage based on progress
        const stageIndex = Math.min(
          Math.floor((statusData.progress || 0) / 25), 
          stages.length - 1
        );
        setCurrentStage(stageIndex);
        
        // Add to logs if there's a new message
        if (statusData.message && !fallbackLogs.some(log => log.message === statusData.message)) {
          setFallbackLogs(prev => [...prev, {
            timestamp: new Date().toLocaleTimeString(),
            message: statusData.message,
            stage: stages[stageIndex]?.name || 'Processing'
          }]);
        }

        if (statusData.status === 'completed' || statusData.status === 'failed') {
          clearInterval(interval);
          setFallbackPolling(false);
        }
      } catch (error) {
        console.error('Status polling error:', error);
      }
    }, 3000);

    // Cleanup after 10 minutes
    setTimeout(() => {
      clearInterval(interval);
      setFallbackPolling(false);
    }, 600000);

    return () => clearInterval(interval);
  };

  const getStageStatus = (stageIndex) => {
    if (stageIndex < currentStage) return 'completed';
    if (stageIndex === currentStage) return 'active';
    return 'pending';
  };

  const getStageIcon = (stage, stageStatus) => {
    const Icon = stage.icon;
    
    if (stageStatus === 'completed') {
      return <CheckCircle className="w-6 h-6 text-green-500" />;
    } else if (stageStatus === 'active') {
      return <Loader2 className="w-6 h-6 text-blue-500 animate-spin" />;
    } else {
      return <Icon className="w-6 h-6 text-gray-400" />;
    }
  };

  return (
    <div className="space-y-8">
      {/* Overall Progress */}
      <div className="text-center">
        <h3 className="text-lg font-medium text-gray-900 mb-4">
          Generating Your AI-Powered Course
        </h3>
        
        <div className="w-full bg-gray-200 rounded-full h-3 mb-4">
          <motion.div
            className="bg-blue-600 h-3 rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.5, ease: "easeOut" }}
          />
        </div>
        
        <p className="text-sm text-gray-600">
          {progress}% Complete • Estimated time remaining: {Math.max(1, Math.ceil((100 - progress) / 10))} minutes
        </p>
      </div>

      {/* Stage Progress */}
      <div className="space-y-4">
        {stages.map((stage, index) => {
          const stageStatus = getStageStatus(index);
          
          return (
            <motion.div
              key={stage.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1 }}
              className={`flex items-start space-x-4 p-4 rounded-lg border ${
                stageStatus === 'active' 
                  ? 'bg-blue-50 border-blue-200' 
                  : stageStatus === 'completed'
                  ? 'bg-green-50 border-green-200'
                  : 'bg-gray-50 border-gray-200'
              }`}
            >
              <div className="flex-shrink-0 mt-1">
                {getStageIcon(stage, stageStatus)}
              </div>
              
              <div className="flex-1 min-w-0">
                <h4 className={`font-medium ${
                  stageStatus === 'active' 
                    ? 'text-blue-900' 
                    : stageStatus === 'completed'
                    ? 'text-green-900'
                    : 'text-gray-500'
                }`}>
                  {stage.name}
                </h4>
                
                <p className={`text-sm mt-1 ${
                  stageStatus === 'active' 
                    ? 'text-blue-700' 
                    : stageStatus === 'completed'
                    ? 'text-green-700'
                    : 'text-gray-500'
                }`}>
                  {stage.description}
                </p>
                
                {stageStatus === 'active' && (
                  <div className="mt-2">
                    <div className="flex items-center space-x-2">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{animationDelay: '0ms'}} />
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{animationDelay: '150ms'}} />
                        <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{animationDelay: '300ms'}} />
                      </div>
                      <span className="text-xs text-blue-600">Processing...</span>
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Activity Log */}
      {logs.length > 0 && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-3 flex items-center">
            <Clock className="w-4 h-4 mr-2" />
            Activity Log
          </h4>
          
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {logs.map((log, index) => (
              <div
                key={index}
                className={`text-sm p-2 rounded ${
                  log.isError 
                    ? 'bg-red-100 text-red-800' 
                    : 'bg-white text-gray-700'
                }`}
              >
                <div className="flex items-center justify-between">
                  <span className="font-medium">{log.stage}</span>
                  <span className="text-xs text-gray-500">{log.timestamp}</span>
                </div>
                <p className="mt-1">{log.message}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Generation Details */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <Brain className="w-5 h-5 text-blue-400" />
          </div>
          <div className="ml-3">
            <h4 className="text-sm font-medium text-blue-800">
              AI Generation Process
            </h4>
            <div className="mt-1 text-sm text-blue-700">
              <p>
                Our AI is analyzing your uploaded documents and course requirements to create 
                a personalized English learning experience. This includes:
              </p>
              <ul className="mt-2 list-disc list-inside space-y-1">
                <li>Industry-specific vocabulary and terminology</li>
                <li>Contextual exercises based on your SOPs</li>
                <li>Progressive difficulty levels</li>
                <li>Interactive assessments and feedback</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Connection & Status Indicator */}
      <div className="text-center space-y-2">
        {/* Connection Status */}
        <div className="inline-flex items-center text-xs text-gray-500">
          {fallbackPolling ? (
            <>
              <WifiOff className="w-3 h-3 mr-1" />
              Using fallback polling
            </>
          ) : (
            <>
              <Wifi className="w-3 h-3 mr-1" />
              Real-time updates active
            </>
          )}
        </div>

        {/* Generation Status */}
        {status && (
          <div>
            {status === 'failed' ? (
              <div className="inline-flex items-center px-4 py-2 bg-red-100 text-red-800 rounded-full">
                <AlertCircle className="w-4 h-4 mr-2" />
                Generation Failed
              </div>
            ) : status === 'completed' ? (
              <div className="inline-flex items-center px-4 py-2 bg-green-100 text-green-800 rounded-full">
                <CheckCircle className="w-4 h-4 mr-2" />
                Generation Complete
              </div>
            ) : (
              <div className="inline-flex items-center px-4 py-2 bg-blue-100 text-blue-800 rounded-full">
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Generating Course...
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default GenerationProgress;