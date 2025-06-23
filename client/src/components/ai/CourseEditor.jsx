import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Edit3, 
  Save, 
  Undo, 
  Redo,
  Wand2,
  RefreshCw,
  CheckCircle,
  AlertTriangle,
  Plus,
  Trash2,
  Eye,
  EyeOff,
  Lightbulb
} from 'lucide-react';
import { useForm } from 'react-hook-form';
import toast from 'react-hot-toast';
import { aiAPI } from '../../services/api';

const CourseEditor = ({ course, onSave, onClose }) => {
  const [editingSection, setEditingSection] = useState(null);
  const [isEnhancing, setIsEnhancing] = useState(false);
  const [unsavedChanges, setUnsavedChanges] = useState(false);
  const [previewMode, setPreviewMode] = useState(false);
  const [aiSuggestions, setAiSuggestions] = useState({});

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    getValues,
    formState: { errors, isDirty }
  } = useForm({
    defaultValues: {
      title: course?.title || '',
      description: course?.description || '',
      learning_objectives: course?.learning_objectives || [],
      modules: course?.modules || []
    }
  });

  const watchedData = watch();

  React.useEffect(() => {
    setUnsavedChanges(isDirty);
  }, [isDirty]);

  const handleSaveChanges = async (data) => {
    try {
      await onSave(data);
      setUnsavedChanges(false);
      toast.success('Course saved successfully');
    } catch (error) {
      toast.error('Failed to save course');
    }
  };

  const handleEnhanceContent = async (section, content) => {
    setIsEnhancing(true);
    try {
      const response = await aiAPI.enhanceContent(course.id, {
        section,
        content,
        enhancement_type: 'improve_clarity'
      });
      
      const enhanced = response.data.enhanced_content;
      
      // Update the form with enhanced content
      if (section === 'description') {
        setValue('description', enhanced);
      } else if (section.startsWith('module_')) {
        const moduleIndex = parseInt(section.split('_')[1]);
        const modules = getValues('modules');
        modules[moduleIndex].description = enhanced;
        setValue('modules', modules);
      }
      
      toast.success('Content enhanced successfully');
    } catch (error) {
      toast.error('Failed to enhance content');
    } finally {
      setIsEnhancing(false);
    }
  };

  const handleGetAISuggestions = async (section) => {
    try {
      const response = await aiAPI.reviewContent(course.id, {
        section,
        criteria: ['clarity', 'engagement', 'learning_effectiveness']
      });
      
      setAiSuggestions(prev => ({
        ...prev,
        [section]: response.data.suggestions
      }));
    } catch (error) {
      toast.error('Failed to get AI suggestions');
    }
  };

  const addLearningObjective = () => {
    const objectives = getValues('learning_objectives');
    setValue('learning_objectives', [...objectives, '']);
  };

  const removeLearningObjective = (index) => {
    const objectives = getValues('learning_objectives');
    setValue('learning_objectives', objectives.filter((_, i) => i !== index));
  };

  const addModule = () => {
    const modules = getValues('modules');
    setValue('modules', [...modules, {
      title: 'New Module',
      description: '',
      sequence_number: modules.length + 1,
      lessons: []
    }]);
  };

  const removeModule = (index) => {
    const modules = getValues('modules');
    setValue('modules', modules.filter((_, i) => i !== index));
  };

  const addLesson = (moduleIndex) => {
    const modules = getValues('modules');
    const module = modules[moduleIndex];
    module.lessons = module.lessons || [];
    module.lessons.push({
      title: 'New Lesson',
      description: '',
      duration_minutes: 45,
      sequence_number: module.lessons.length + 1
    });
    setValue('modules', modules);
  };

  const removeLesson = (moduleIndex, lessonIndex) => {
    const modules = getValues('modules');
    modules[moduleIndex].lessons.splice(lessonIndex, 1);
    setValue('modules', modules);
  };

  const EditableSection = ({ 
    label, 
    value, 
    onChange, 
    onEnhance, 
    multiline = false, 
    sectionKey,
    placeholder = '' 
  }) => {
    const [isEditing, setIsEditing] = useState(false);
    const [tempValue, setTempValue] = useState(value);

    const handleSave = () => {
      onChange(tempValue);
      setIsEditing(false);
    };

    const handleCancel = () => {
      setTempValue(value);
      setIsEditing(false);
    };

    return (
      <div className="group relative">
        <div className="flex items-center justify-between mb-2">
          <label className="text-sm font-medium text-gray-700">{label}</label>
          <div className="flex items-center space-x-2 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              onClick={() => handleGetAISuggestions(sectionKey)}
              className="text-purple-600 hover:text-purple-800 text-xs"
              title="Get AI suggestions"
            >
              <Lightbulb className="w-4 h-4" />
            </button>
            <button
              onClick={() => onEnhance(sectionKey, value)}
              disabled={isEnhancing}
              className="text-blue-600 hover:text-blue-800 text-xs"
              title="Enhance with AI"
            >
              <Wand2 className="w-4 h-4" />
            </button>
            <button
              onClick={() => setIsEditing(!isEditing)}
              className="text-gray-600 hover:text-gray-800 text-xs"
            >
              <Edit3 className="w-4 h-4" />
            </button>
          </div>
        </div>

        {isEditing ? (
          <div className="space-y-2">
            {multiline ? (
              <textarea
                value={tempValue}
                onChange={(e) => setTempValue(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows={4}
                placeholder={placeholder}
              />
            ) : (
              <input
                type="text"
                value={tempValue}
                onChange={(e) => setTempValue(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder={placeholder}
              />
            )}
            <div className="flex space-x-2">
              <button
                onClick={handleSave}
                className="px-3 py-1 bg-green-600 text-white text-sm rounded-md hover:bg-green-700"
              >
                <CheckCircle className="w-3 h-3 mr-1 inline" />
                Save
              </button>
              <button
                onClick={handleCancel}
                className="px-3 py-1 bg-gray-600 text-white text-sm rounded-md hover:bg-gray-700"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <div className="p-3 bg-gray-50 rounded-md border border-gray-200 hover:border-gray-300 cursor-pointer"
               onClick={() => setIsEditing(true)}>
            {value || <span className="text-gray-500 italic">{placeholder}</span>}
          </div>
        )}

        {/* AI Suggestions */}
        {aiSuggestions[sectionKey] && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            className="mt-2 p-3 bg-purple-50 border border-purple-200 rounded-md"
          >
            <h5 className="text-sm font-medium text-purple-900 mb-2">AI Suggestions:</h5>
            <ul className="text-sm text-purple-800 space-y-1">
              {aiSuggestions[sectionKey].map((suggestion, index) => (
                <li key={index} className="flex items-start">
                  <span className="text-purple-600 mr-2">•</span>
                  {suggestion}
                </li>
              ))}
            </ul>
            <button
              onClick={() => setAiSuggestions(prev => ({ ...prev, [sectionKey]: null }))}
              className="text-xs text-purple-600 hover:text-purple-800 mt-2"
            >
              Dismiss
            </button>
          </motion.div>
        )}
      </div>
    );
  };

  return (
    <div className="max-w-6xl mx-auto bg-white">
      {/* Header */}
      <div className="flex items-center justify-between p-6 border-b border-gray-200">
        <div className="flex items-center space-x-4">
          <h2 className="text-xl font-semibold text-gray-900">Course Editor</h2>
          {unsavedChanges && (
            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
              <AlertTriangle className="w-3 h-3 mr-1" />
              Unsaved Changes
            </span>
          )}
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={() => setPreviewMode(!previewMode)}
            className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            {previewMode ? <Edit3 className="w-4 h-4 mr-2" /> : <Eye className="w-4 h-4 mr-2" />}
            {previewMode ? 'Edit' : 'Preview'}
          </button>

          <button
            onClick={handleSubmit(handleSaveChanges)}
            disabled={!unsavedChanges}
            className="flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            <Save className="w-4 h-4 mr-2" />
            Save Changes
          </button>

          <button
            onClick={onClose}
            className="flex items-center px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Close
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="p-6 space-y-8">
        {/* Course Title */}
        <EditableSection
          label="Course Title"
          value={watchedData.title}
          onChange={(value) => setValue('title', value)}
          onEnhance={handleEnhanceContent}
          sectionKey="title"
          placeholder="Enter course title..."
        />

        {/* Course Description */}
        <EditableSection
          label="Course Description"
          value={watchedData.description}
          onChange={(value) => setValue('description', value)}
          onEnhance={handleEnhanceContent}
          sectionKey="description"
          multiline
          placeholder="Describe what students will learn in this course..."
        />

        {/* Learning Objectives */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">Learning Objectives</h3>
            <button
              onClick={addLearningObjective}
              className="flex items-center px-3 py-2 text-sm font-medium text-blue-600 hover:text-blue-800"
            >
              <Plus className="w-4 h-4 mr-1" />
              Add Objective
            </button>
          </div>

          <div className="space-y-3">
            {(watchedData.learning_objectives || []).map((objective, index) => (
              <div key={index} className="flex items-center space-x-3">
                <input
                  {...register(`learning_objectives.${index}`)}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Enter learning objective..."
                />
                <button
                  onClick={() => removeLearningObjective(index)}
                  className="text-red-600 hover:text-red-800"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Modules */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-medium text-gray-900">Course Modules</h3>
            <button
              onClick={addModule}
              className="flex items-center px-3 py-2 text-sm font-medium text-blue-600 hover:text-blue-800"
            >
              <Plus className="w-4 h-4 mr-1" />
              Add Module
            </button>
          </div>

          <div className="space-y-6">
            {(watchedData.modules || []).map((module, moduleIndex) => (
              <motion.div
                key={moduleIndex}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="border border-gray-200 rounded-lg p-6"
              >
                <div className="flex items-center justify-between mb-4">
                  <h4 className="text-md font-medium text-gray-900">
                    Module {moduleIndex + 1}
                  </h4>
                  <button
                    onClick={() => removeModule(moduleIndex)}
                    className="text-red-600 hover:text-red-800"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                <div className="space-y-4">
                  <input
                    {...register(`modules.${moduleIndex}.title`)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Module title..."
                  />

                  <textarea
                    {...register(`modules.${moduleIndex}.description`)}
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Module description..."
                  />

                  {/* Lessons */}
                  <div>
                    <div className="flex items-center justify-between mb-3">
                      <h5 className="text-sm font-medium text-gray-700">Lessons</h5>
                      <button
                        onClick={() => addLesson(moduleIndex)}
                        className="text-xs text-blue-600 hover:text-blue-800"
                      >
                        <Plus className="w-3 h-3 mr-1 inline" />
                        Add Lesson
                      </button>
                    </div>

                    <div className="space-y-2">
                      {(module.lessons || []).map((lesson, lessonIndex) => (
                        <div key={lessonIndex} className="flex items-center space-x-2 p-3 bg-gray-50 rounded-md">
                          <input
                            {...register(`modules.${moduleIndex}.lessons.${lessonIndex}.title`)}
                            className="flex-1 px-2 py-1 border border-gray-300 rounded text-sm"
                            placeholder="Lesson title..."
                          />
                          <input
                            {...register(`modules.${moduleIndex}.lessons.${lessonIndex}.duration_minutes`, { valueAsNumber: true })}
                            type="number"
                            min="1"
                            max="240"
                            className="w-20 px-2 py-1 border border-gray-300 rounded text-sm"
                            placeholder="45"
                          />
                          <span className="text-xs text-gray-500">min</span>
                          <button
                            onClick={() => removeLesson(moduleIndex, lessonIndex)}
                            className="text-red-600 hover:text-red-800"
                          >
                            <Trash2 className="w-3 h-3" />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Loading overlay for AI enhancement */}
      {isEnhancing && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 flex items-center space-x-4">
            <RefreshCw className="w-6 h-6 text-blue-600 animate-spin" />
            <span className="text-gray-900">Enhancing content with AI...</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default CourseEditor;