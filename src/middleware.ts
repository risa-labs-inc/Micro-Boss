import { NextRequest, NextResponse } from 'next/server';

// Define public routes
const publicRoutes = ['/login', '/register'];

// Middleware function
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // Check if token exists
  const token = request.cookies.get('microboss_auth_token')?.value;
  const isAuthenticated = !!token;
  
  // If route requires authentication and user is not authenticated, redirect to login
  if (!isAuthenticated && !publicRoutes.includes(pathname) && !pathname.startsWith('/_next') && !pathname.startsWith('/api') && !pathname.includes('.')) {
    const loginUrl = new URL('/login', request.url);
    return NextResponse.redirect(loginUrl);
  }
  
  // If user is authenticated and tries to access login/register, redirect to dashboard
  if (isAuthenticated && publicRoutes.includes(pathname)) {
    const dashboardUrl = new URL('/', request.url);
    return NextResponse.redirect(dashboardUrl);
  }
  
  return NextResponse.next();
}

// Configure the middleware to run on specific paths
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
}; 