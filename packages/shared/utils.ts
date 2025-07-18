// Shared utility functions for the AI Language Learning Platform
// Moved from client/lib/utils.ts
// Requires: clsx, tailwind-merge (install in root package.json)

import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
} 