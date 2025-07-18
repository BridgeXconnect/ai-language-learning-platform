// Shared constants for the AI Language Learning Platform
// Moved from client/lib/constants.ts

export enum UserRole {
  SALES = "sales",
  COURSE_MANAGER = "course_manager",
  TRAINER = "trainer",
  STUDENT = "student",
  ADMIN = "admin",
}

export interface User {
  id: string
  name: string
  email: string
  roles: UserRole[]
  avatarUrl?: string
} 