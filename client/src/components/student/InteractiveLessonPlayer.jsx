import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/auth_context';
import { 
  PlayIcon,
  PauseIcon,
  SpeakerWaveIcon,
  SpeakerXMarkIcon,
  ArrowLeftIcon,
  ArrowRightIcon,
  CheckCircleIcon,
  XCircleIcon,
  LightBulbIcon,
  ChatBubbleLeftIcon,
  BookmarkIcon,
  ShareIcon,
  ClockIcon,
  StarIcon,
  MicrophoneIcon,
  StopIcon,
  ArrowPathIcon,
  EyeIcon,
  EyeSlashIcon
} from '@heroicons/react/24/outline';
import { 
  CheckCircleIcon as CheckCircleIconSolid,
  BookmarkIcon as BookmarkIconSolid,
  StarIcon as StarIconSolid
} from '@heroicons/react/24/solid';
import api from '../../services/api';

const InteractiveLessonPlayer = () => {
  const { lessonId } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const videoRef = useRef(null);
  const audioRef = useRef(null);
  
  // Lesson state
  const [lesson, setLesson] = useState(null);
  const [currentSection, setCurrentSection] = useState(0);
  const [progress, setProgress] = useState(0);
  const [loading, setLoading] = useState(true);
  
  // Media controls
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [playbackSpeed, setPlaybackSpeed] = useState(1);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  
  // Interactive features
  const [showTranscript, setShowTranscript] = useState(false);
  const [isBookmarked, setIsBookmarked] = useState(false);
  const [userRating, setUserRating] = useState(0);
  const [showNotes, setShowNotes] = useState(false);
  const [notes, setNotes] = useState('');
  
  // Exercise state
  const [currentExercise, setCurrentExercise] = useState(null);
  const [exerciseAnswers, setExerciseAnswers] = useState({});
  const [exerciseResults, setExerciseResults] = useState({});
  const [showExerciseResults, setShowExerciseResults] = useState(false);
  
  // Recording state
  const [isRecording, setIsRecording] = useState(false);
  const [recordingBlob, setRecordingBlob] = useState(null);
  const [mediaRecorder, setMediaRecorder] = useState(null);

  useEffect(() => {
    fetchLessonData();
  }, [lessonId]);

  useEffect(() => {
    const video = videoRef.current;
    if (video) {
      const updateTime = () => setCurrentTime(video.currentTime);
      const updateDuration = () => setDuration(video.duration);
      
      video.addEventListener('timeupdate', updateTime);
      video.addEventListener('loadedmetadata', updateDuration);
      
      return () => {
        video.removeEventListener('timeupdate', updateTime);
        video.removeEventListener('loadedmetadata', updateDuration);
      };
    }
  }, [lesson]);

  const fetchLessonData = async () => {
    try {
      setLoading(true);
      
      // Mock lesson data until backend is available
      await new Promise(resolve => setTimeout(resolve, 800)); // Simulate loading
      
      const mockLesson = {
        id: lessonId,
        title: 'Business Presentation Skills',
        course_title: 'Advanced Business English',
        description: 'Learn how to deliver effective business presentations with confidence and clarity.',
        video_url: 'https://sample-videos.com/zip/10/mp4/720/mp4-sample-nw_small.mp4', // Sample video
        transcript: `Welcome to today's lesson on business presentation skills.
        
In this lesson, you will learn:
- How to structure a compelling presentation
- Techniques for engaging your audience
- Strategies for handling questions and feedback

Let's begin with the fundamentals of presentation structure...

A good presentation has three main parts:
1. Introduction - Hook your audience and preview your content
2. Body - Present your key points with supporting evidence
3. Conclusion - Summarize and call to action

Remember, practice makes perfect. The more you present, the more confident you'll become.`,
        content: `<div class="lesson-content">
          <h2>Business Presentation Skills</h2>
          <p>In today's business world, effective presentation skills are essential for success. Whether you're pitching to clients, presenting to your team, or speaking at a conference, your ability to communicate clearly and persuasively can make or break your career.</p>
          
          <h3>Key Learning Objectives</h3>
          <ul>
            <li>Structure presentations for maximum impact</li>
            <li>Use visual aids effectively</li>
            <li>Engage your audience throughout</li>
            <li>Handle questions with confidence</li>
          </ul>
          
          <h3>Presentation Structure</h3>
          <p>Every great presentation follows a clear structure. Think of it as telling a story with a beginning, middle, and end.</p>
          
          <h4>1. Introduction (Hook + Preview)</h4>
          <p>Start with something that grabs attention - a surprising statistic, a thought-provoking question, or a relevant story.</p>
          
          <h4>2. Body (Main Points + Evidence)</h4>
          <p>Present 2-3 key points maximum. Support each point with data, examples, or stories.</p>
          
          <h4>3. Conclusion (Summary + Call to Action)</h4>
          <p>Recap your main points and tell your audience exactly what you want them to do next.</p>
        </div>`,
        sections: [
          { title: 'Introduction', timestamp: 0 },
          { title: 'Presentation Structure', timestamp: 45 },
          { title: 'Engaging Your Audience', timestamp: 120 },
          { title: 'Handling Questions', timestamp: 180 },
          { title: 'Practice Exercise', timestamp: 240 }
        ],
        exercises: [
          {
            id: 'ex1',
            title: 'Presentation Structure Quiz',
            type: 'multiple_choice',
            questions: [
              {
                id: 'q1',
                text: 'What are the three main parts of a presentation?',
                type: 'multiple_choice',
                options: [
                  'Introduction, Body, Conclusion',
                  'Hook, Content, Summary',
                  'Start, Middle, Finish',
                  'Problem, Solution, Benefit'
                ]
              },
              {
                id: 'q2',
                text: 'How many key points should you present in the body?',
                type: 'multiple_choice',
                options: ['1-2', '2-3', '3-5', 'As many as possible']
              }
            ]
          },
          {
            id: 'ex2',
            title: 'Speaking Practice',
            type: 'speaking',
            questions: [
              {
                id: 'q3',
                text: 'Record yourself giving a 1-minute introduction to a presentation about your company.',
                type: 'speaking'
              }
            ]
          }
        ],
        duration: 15,
        cefr_level: 'B2',
        difficulty: 'Intermediate',
        previous_lesson_id: lessonId > 1 ? `lesson_${parseInt(lessonId.split('_')[1]) - 1}` : null,
        next_lesson_id: `lesson_${parseInt(lessonId.split('_')[1] || '1') + 1}`
      };
      
      setLesson(mockLesson);
      setProgress(65); // Mock progress
      setIsBookmarked(false);
      setUserRating(0);
      setNotes('');
      
    } catch (error) {
      console.error('Error fetching lesson data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePlayPause = () => {
    const video = videoRef.current;
    if (video) {
      if (isPlaying) {
        video.pause();
      } else {
        video.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleMute = () => {
    const video = videoRef.current;
    if (video) {
      video.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const handleSpeedChange = (speed) => {
    const video = videoRef.current;
    if (video) {
      video.playbackRate = speed;
      setPlaybackSpeed(speed);
    }
  };

  const handleSeek = (time) => {
    const video = videoRef.current;
    if (video) {
      video.currentTime = time;
      setCurrentTime(time);
    }
  };

  const handleSectionChange = (sectionIndex) => {
    setCurrentSection(sectionIndex);
    if (lesson?.sections[sectionIndex]?.timestamp) {
      handleSeek(lesson.sections[sectionIndex].timestamp);
    }
  };

  const handleBookmark = async () => {
    try {
      // Mock API call
      console.log(`Toggling bookmark for lesson ${lessonId}:`, !isBookmarked);
      await new Promise(resolve => setTimeout(resolve, 200));
      setIsBookmarked(!isBookmarked);
    } catch (error) {
      console.error('Error updating bookmark:', error);
    }
  };

  const handleRating = async (rating) => {
    try {
      // Mock API call
      console.log(`Rating lesson ${lessonId}:`, rating);
      await new Promise(resolve => setTimeout(resolve, 200));
      setUserRating(rating);
    } catch (error) {
      console.error('Error submitting rating:', error);
    }
  };

  const handleNotesUpdate = async () => {
    try {
      // Mock API call
      console.log(`Saving notes for lesson ${lessonId}:`, notes);
      await new Promise(resolve => setTimeout(resolve, 200));
    } catch (error) {
      console.error('Error saving notes:', error);
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      const chunks = [];

      recorder.ondataavailable = (e) => chunks.push(e.data);
      recorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/wav' });
        setRecordingBlob(blob);
      };

      recorder.start();
      setMediaRecorder(recorder);
      setIsRecording(true);
    } catch (error) {
      console.error('Error starting recording:', error);
    }
  };

  const stopRecording = () => {
    if (mediaRecorder) {
      mediaRecorder.stop();
      setIsRecording(false);
    }
  };

  const handleExerciseAnswer = (questionId, answer) => {
    setExerciseAnswers(prev => ({
      ...prev,
      [questionId]: answer
    }));
  };

  const submitExercise = async () => {
    try {
      // Mock exercise submission
      console.log('Submitting exercise answers:', exerciseAnswers);
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock results - in a real app this would come from the server
      const mockResults = {};
      Object.keys(exerciseAnswers).forEach(questionId => {
        // Simple mock scoring - first option is usually correct
        mockResults[questionId] = {
          correct: exerciseAnswers[questionId] === 'Introduction, Body, Conclusion' || 
                   exerciseAnswers[questionId] === '2-3',
          user_answer: exerciseAnswers[questionId],
          correct_answer: questionId === 'q1' ? 'Introduction, Body, Conclusion' : '2-3',
          explanation: questionId === 'q1' ? 
            'The three main parts of a presentation are Introduction, Body, and Conclusion.' :
            'Most effective presentations focus on 2-3 key points to avoid overwhelming the audience.'
        };
      });
      
      setExerciseResults(mockResults);
      setShowExerciseResults(true);
    } catch (error) {
      console.error('Error submitting exercise:', error);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const ProgressBar = () => (
    <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
      <motion.div 
        className="bg-blue-600 h-2 rounded-full"
        style={{ width: `${(currentTime / duration) * 100}%` }}
        transition={{ duration: 0.1 }}
      ></motion.div>
    </div>
  );

  const VideoControls = () => (
    <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4">
      <ProgressBar />
      <div className="flex items-center justify-between text-white">
        <div className="flex items-center space-x-4">
          <motion.button
            onClick={handlePlayPause}
            className="p-2 hover:bg-white/20 rounded-full transition-colors"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
          >
            {isPlaying ? (
              <PauseIcon className="h-6 w-6" />
            ) : (
              <PlayIcon className="h-6 w-6" />
            )}
          </motion.button>
          
          <button
            onClick={handleMute}
            className="p-2 hover:bg-white/20 rounded-full transition-colors"
          >
            {isMuted ? (
              <SpeakerXMarkIcon className="h-5 w-5" />
            ) : (
              <SpeakerWaveIcon className="h-5 w-5" />
            )}
          </button>
          
          <span className="text-sm">
            {formatTime(currentTime)} / {formatTime(duration)}
          </span>
        </div>
        
        <div className="flex items-center space-x-2">
          <select
            value={playbackSpeed}
            onChange={(e) => handleSpeedChange(parseFloat(e.target.value))}
            className="bg-black/50 text-white text-sm rounded px-2 py-1 border-none"
          >
            <option value={0.5}>0.5x</option>
            <option value={0.75}>0.75x</option>
            <option value={1}>1x</option>
            <option value={1.25}>1.25x</option>
            <option value={1.5}>1.5x</option>
            <option value={2}>2x</option>
          </select>
          
          <button
            onClick={() => setShowTranscript(!showTranscript)}
            className="p-2 hover:bg-white/20 rounded-full transition-colors"
          >
            {showTranscript ? (
              <EyeSlashIcon className="h-5 w-5" />
            ) : (
              <EyeIcon className="h-5 w-5" />
            )}
          </button>
        </div>
      </div>
    </div>
  );

  const ExerciseCard = ({ exercise }) => (
    <div className="card mb-6">
      <div className="card-header">
        <h3 className="font-semibold text-gray-900">{exercise.title}</h3>
        <p className="text-sm text-gray-600">{exercise.type}</p>
      </div>
      <div className="card-body">
        {exercise.questions.map((question, index) => (
          <div key={index} className="mb-4">
            <p className="font-medium text-gray-900 mb-2">{question.text}</p>
            
            {question.type === 'multiple_choice' && (
              <div className="space-y-2">
                {question.options.map((option, optionIndex) => (
                  <label key={optionIndex} className="flex items-center space-x-2">
                    <input
                      type="radio"
                      name={`question_${question.id}`}
                      value={option}
                      onChange={(e) => handleExerciseAnswer(question.id, e.target.value)}
                      className="text-blue-600"
                    />
                    <span className="text-gray-700">{option}</span>
                  </label>
                ))}
              </div>
            )}
            
            {question.type === 'text_input' && (
              <input
                type="text"
                onChange={(e) => handleExerciseAnswer(question.id, e.target.value)}
                className="form-input w-full"
                placeholder="Type your answer..."
              />
            )}
            
            {question.type === 'speaking' && (
              <div className="flex items-center space-x-4">
                <button
                  onClick={isRecording ? stopRecording : startRecording}
                  className={`btn ${isRecording ? 'btn-error' : 'btn-primary'}`}
                >
                  {isRecording ? (
                    <>
                      <StopIcon className="h-4 w-4" />
                      Stop Recording
                    </>
                  ) : (
                    <>
                      <MicrophoneIcon className="h-4 w-4" />
                      Start Recording
                    </>
                  )}
                </button>
                {recordingBlob && (
                  <audio controls src={URL.createObjectURL(recordingBlob)} />
                )}
              </div>
            )}
          </div>
        ))}
        
        <button
          onClick={submitExercise}
          className="btn btn-primary mt-4"
          disabled={Object.keys(exerciseAnswers).length === 0}
        >
          Submit Exercise
        </button>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="loading-spinner mx-auto mb-4" />
          <p className="text-gray-600">Loading lesson...</p>
        </div>
      </div>
    );
  }

  if (!lesson) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Lesson not found</h2>
          <p className="text-gray-600 mb-4">The lesson you're looking for doesn't exist.</p>
          <button onClick={() => navigate('/student')} className="btn btn-primary">
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <motion.div 
      className="min-h-screen bg-gray-50"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.3 }}
    >
      {/* Header */}
      <motion.div 
        className="bg-white shadow-sm border-b"
        initial={{ y: -20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/student')}
                className="btn btn-ghost"
              >
                <ArrowLeftIcon className="h-5 w-5" />
                Back to Course
              </button>
              <div>
                <h1 className="text-xl font-bold text-gray-900">{lesson.title}</h1>
                <p className="text-sm text-gray-600">{lesson.course_title}</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <button
                onClick={handleBookmark}
                className="btn btn-ghost"
              >
                {isBookmarked ? (
                  <BookmarkIconSolid className="h-5 w-5 text-blue-600" />
                ) : (
                  <BookmarkIcon className="h-5 w-5" />
                )}
              </button>
              
              <button
                onClick={() => setShowNotes(!showNotes)}
                className="btn btn-ghost"
              >
                <ChatBubbleLeftIcon className="h-5 w-5" />
                Notes
              </button>
              
              <div className="flex items-center space-x-1">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    onClick={() => handleRating(star)}
                    className="text-gray-300 hover:text-yellow-400 transition-colors"
                  >
                    {star <= userRating ? (
                      <StarIconSolid className="h-5 w-5 text-yellow-400" />
                    ) : (
                      <StarIcon className="h-5 w-5" />
                    )}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-3">
            {/* Video Player */}
            {lesson.video_url && (
              <div className="relative bg-black rounded-lg overflow-hidden mb-6">
                <video
                  ref={videoRef}
                  src={lesson.video_url}
                  className="w-full aspect-video"
                  onPlay={() => setIsPlaying(true)}
                  onPause={() => setIsPlaying(false)}
                />
                <VideoControls />
              </div>
            )}

            {/* Transcript */}
            {showTranscript && lesson.transcript && (
              <div className="card mb-6">
                <div className="card-header">
                  <h3 className="font-semibold text-gray-900">Transcript</h3>
                </div>
                <div className="card-body">
                  <div className="prose max-w-none">
                    {lesson.transcript.split('\n').map((line, index) => (
                      <p key={index} className="mb-2">{line}</p>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Lesson Content */}
            <div className="card mb-6">
              <div className="card-header">
                <h3 className="font-semibold text-gray-900">Lesson Content</h3>
              </div>
              <div className="card-body">
                <div className="prose max-w-none">
                  <div dangerouslySetInnerHTML={{ __html: lesson.content }} />
                </div>
              </div>
            </div>

            {/* Interactive Exercises */}
            {lesson.exercises && lesson.exercises.map((exercise, index) => (
              <ExerciseCard key={index} exercise={exercise} />
            ))}

            {/* Navigation */}
            <div className="flex justify-between items-center mt-8">
              <button
                onClick={() => navigate(`/student/lesson/${lesson.previous_lesson_id}`)}
                disabled={!lesson.previous_lesson_id}
                className="btn btn-secondary disabled:opacity-50"
              >
                <ArrowLeftIcon className="h-4 w-4" />
                Previous Lesson
              </button>
              
              <motion.div 
                className="text-center"
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.5, delay: 0.3 }}
              >
                <div className="text-sm text-gray-500 mb-1">Lesson Progress</div>
                <div className="text-2xl font-bold text-blue-600">{Math.round(progress)}%</div>
              </motion.div>
              
              <button
                onClick={() => navigate(`/student/lesson/${lesson.next_lesson_id}`)}
                disabled={!lesson.next_lesson_id}
                className="btn btn-primary disabled:opacity-50"
              >
                Next Lesson
                <ArrowRightIcon className="h-4 w-4" />
              </button>
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Lesson Sections */}
            <div className="card">
              <div className="card-header">
                <h3 className="font-semibold text-gray-900">Lesson Sections</h3>
              </div>
              <div className="card-body p-0">
                {lesson.sections?.map((section, index) => (
                  <button
                    key={index}
                    onClick={() => handleSectionChange(index)}
                    className={`w-full text-left p-4 border-b border-gray-200 hover:bg-gray-50 transition-colors ${
                      currentSection === index ? 'bg-blue-50 border-l-4 border-l-blue-600' : ''
                    }`}
                  >
                    <div className="font-medium text-gray-900">{section.title}</div>
                    <div className="text-sm text-gray-500">{formatTime(section.timestamp)}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Notes Panel */}
            {showNotes && (
              <div className="card">
                <div className="card-header">
                  <h3 className="font-semibold text-gray-900">My Notes</h3>
                </div>
                <div className="card-body">
                  <textarea
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    onBlur={handleNotesUpdate}
                    placeholder="Add your notes here..."
                    rows={6}
                    className="form-input w-full"
                  />
                </div>
              </div>
            )}

            {/* Lesson Info */}
            <div className="card">
              <div className="card-header">
                <h3 className="font-semibold text-gray-900">Lesson Info</h3>
              </div>
              <div className="card-body space-y-3">
                <div className="flex justify-between">
                  <span className="text-gray-600">Duration</span>
                  <span className="font-medium">{lesson.duration} min</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">CEFR Level</span>
                  <span className="font-medium">{lesson.cefr_level}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Difficulty</span>
                  <span className="font-medium">{lesson.difficulty}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Completion</span>
                  <span className="font-medium">{Math.round(progress)}%</span>
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="card">
              <div className="card-header">
                <h3 className="font-semibold text-gray-900">Quick Actions</h3>
              </div>
              <div className="card-body space-y-3">
                <button className="w-full btn btn-ghost">
                  <ArrowPathIcon className="h-4 w-4" />
                  Restart Lesson
                </button>
                <button className="w-full btn btn-ghost">
                  <ShareIcon className="h-4 w-4" />
                  Share Lesson
                </button>
                <button className="w-full btn btn-ghost">
                  <LightBulbIcon className="h-4 w-4" />
                  Get Help
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};

export default InteractiveLessonPlayer;