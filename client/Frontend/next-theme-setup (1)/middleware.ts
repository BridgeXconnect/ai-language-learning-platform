import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import { AUTH_TOKEN_KEY } from './lib/config';

// List of routes that don't require authentication
const publicRoutes = ['/login', '/register', '/forgot-password'];

// Function to check if the path matches any of the public routes
const isPublicRoute = (path: string) => {
  return publicRoutes.some(route => path === route || path.startsWith(`${route}/`));
};

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // Allow public routes without authentication
  if (isPublicRoute(pathname)) {
    return NextResponse.next();
  }
  
  // Check for authentication token
  const token = request.cookies.get(AUTH_TOKEN_KEY)?.value;
  
  // If no token found, redirect to login
  if (!token) {
    const url = new URL('/login', request.url);
    url.searchParams.set('from', pathname);
    return NextResponse.redirect(url);
  }
  
  // Continue with the request if authenticated
  return NextResponse.next();
}

// Configure middleware to run on specific paths
export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public files (public folder)
     * - api routes (they handle their own authentication)
     */
    '/((?!_next/static|_next/image|favicon.ico|public|api).*)',
  ],
}; 