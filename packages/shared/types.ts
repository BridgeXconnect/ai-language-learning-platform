// Shared types for the AI Language Learning Platform
// Moved from client/lib/types.ts

// Auth types
export interface User {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  status: string;
  roles: string[];
  avatarUrl?: string;
}

export function isValidUser(obj: any): obj is User {
  return (
    obj &&
    typeof obj.id === 'number' &&
    typeof obj.username === 'string' &&
    typeof obj.email === 'string' &&
    typeof obj.status === 'string' &&
    Array.isArray(obj.roles) &&
    obj.roles.every((role: any) => typeof role === 'string')
  );
}

export interface AuthState {
  user: User | null;
  isLoading: boolean;
  error: string | null;
}

export enum CourseRequestStatus {
  DRAFT = 'DRAFT',
  SUBMITTED = 'SUBMITTED',
  UNDER_REVIEW = 'UNDER_REVIEW',
  APPROVED = 'APPROVED',
  REJECTED = 'REJECTED',
  GENERATION_IN_PROGRESS = 'GENERATION_IN_PROGRESS',
  COMPLETED = 'COMPLETED',
}

export enum SOPFileStatus {
  PENDING = 'PENDING',
  UPLOADING = 'UPLOADING',
  PROCESSING = 'PROCESSING',
  COMPLETED = 'COMPLETED',
  ERROR = 'ERROR',
}

export interface SOPFile {
  id: string;
  name: string;
  size: number;
  type?: string;
  url?: string;
  file?: File;
  status: SOPFileStatus;
  progress?: number;
  errorMessage?: string;
  notes?: string;
}

export interface ClientDetails {
  companyName: string;
  contactPerson: string;
  email: string;
  phone?: string;
  industry?: string;
  companySize?: string;
}

export interface CourseRequest {
  id: string;
  clientDetails: ClientDetails;
  sopFiles: SOPFile[];
  status: CourseRequestStatus;
  requestedBy: string;
  requestedByName: string;
  createdAt: string;
  updatedAt: string;
  notes?: string;
}

export enum CourseStatus {
  DRAFT = 'DRAFT',
  IN_PROGRESS = 'IN_PROGRESS',
  REVIEW = 'REVIEW',
  PUBLISHED = 'PUBLISHED',
  ARCHIVED = 'ARCHIVED',
}

export interface Course {
  id: string;
  title: string;
  description: string;
  status: CourseStatus;
  createdAt: string;
  updatedAt: string;
  createdBy: string;
  lessons: Lesson[];
  clientDetails?: ClientDetails;
  sopFiles?: SOPFile[];
}

export interface Lesson {
  id: string;
  title: string;
  description: string;
  content: string;
  order: number;
  exercises: Exercise[];
}

export interface Exercise {
  id: string;
  title: string;
  description: string;
  type: string;
  content: string;
  order: number;
}

export enum GenerationStatus {
  QUEUED = 'QUEUED',
  PROCESSING = 'PROCESSING',
  COMPLETED = 'COMPLETED',
  FAILED = 'FAILED',
}

export interface GenerationProgress {
  id: string;
  status: GenerationStatus;
  progress: number;
  message: string;
  courseId?: string;
  error?: string;
}

// NOTE: React.ReactNode is replaced with 'any' for now. Revisit if/when types are unified across packages.
export interface ColumnDefinition<T> {
  accessorKey: keyof T | string;
  header: string | (() => any);
  cell?: (props: { row: T; value: any }) => any;
  enableSorting?: boolean;
  enableFiltering?: boolean;
}

export interface DashboardStats {
  totalCourses: number;
  activeCourses: number;
  totalStudents: number;
  activeStudents: number;
  completionRate: number;
  courseRequests: number;
  pendingApprovals: number;
}

export interface TrainerDashboardStats {
  assignedCourses: number;
  pendingReviews: number;
  completedReviews: number;
  averageFeedbackScore: number;
}

export interface StudentCourse {
  id: string;
  title: string;
  description: string;
  progress: number;
  completedLessons: number;
  totalLessons: number;
  lastAccessedAt: string;
}

export interface StudentProgress {
  courseId: string;
  lessonId: string;
  completed: boolean;
  score: number;
  timeSpent: number;
  lastAccessedAt: string;
}

export interface CourseManagerRequest {
  id: number;
  company_name: string;
  industry: string;
  status: string;
  priority: string;
  submitted_by: string;
  submitted_at: string;
  training_goals: string;
  current_english_level: string;
  target_english_level: string;
  participant_count: number;
  duration_weeks: number;
  estimated_budget: number;
  urgency: string;
  sop_files: Array<{
    name: string;
    size: string;
    type: string;
  }>;
  notes: string;
  workflow_id?: string;
  generation_method?: string;
  generation_progress?: number;
  workflow_status?: string;
  quality_score?: number;
  course_id?: string;
} 