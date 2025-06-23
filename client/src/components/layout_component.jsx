import React, { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/auth_context';
import { 
  HomeIcon, 
  UserGroupIcon, 
  AcademicCapIcon, 
  ClipboardDocumentListIcon,
  UserIcon,
  ChartBarIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon,
  Bars3Icon,
  XMarkIcon,
  BellIcon
} from '@heroicons/react/24/outline';

const Layout = ({ children }) => {
  const { user, logout, hasRole } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Define navigation items based on user role
  const getNavigationItems = () => {
    const baseItems = [
      { name: 'Dashboard', href: '/', icon: HomeIcon, current: location.pathname === '/' },
    ];

    if (hasRole('sales')) {
      baseItems.push({
        name: 'Sales Portal',
        href: '/sales',
        icon: ClipboardDocumentListIcon,
        current: location.pathname.startsWith('/sales'),
      });
    }

    if (hasRole('course_manager')) {
      baseItems.push({
        name: 'Course Manager',
        href: '/course-manager',
        icon: AcademicCapIcon,
        current: location.pathname.startsWith('/course-manager'),
      });
    }

    if (hasRole('trainer')) {
      baseItems.push({
        name: 'Trainer Portal',
        href: '/trainer',
        icon: UserGroupIcon,
        current: location.pathname.startsWith('/trainer'),
      });
    }

    if (hasRole('student')) {
      baseItems.push({
        name: 'Student Portal',
        href: '/student',
        icon: AcademicCapIcon,
        current: location.pathname.startsWith('/student'),
      });
    }

    if (hasRole('admin')) {
      baseItems.push(
        {
          name: 'Analytics',
          href: '/analytics',
          icon: ChartBarIcon,
          current: location.pathname.startsWith('/analytics'),
        },
        {
          name: 'Settings',
          href: '/settings',
          icon: Cog6ToothIcon,
          current: location.pathname.startsWith('/settings'),
        }
      );
    }

    return baseItems;
  };

  const navigationItems = getNavigationItems();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const Sidebar = ({ mobile = false }) => (
    <div className={`${mobile ? 'md:hidden' : 'hidden md:flex'} md:w-64 md:flex-col md:fixed md:inset-y-0`}>
      <div className="flex flex-col flex-grow pt-5 bg-white border-r border-gray-200 overflow-y-auto">
        {/* Logo */}
        <div className="flex items-center flex-shrink-0 px-4">
          <img
            className="h-8 w-auto"
            src="/logo.svg"
            alt="Dynamic English Course Creator"
          />
          <span className="ml-2 text-lg font-semibold text-gray-900">
            Course Creator
          </span>
        </div>

        {/* Navigation */}
        <div className="mt-5 flex-grow flex flex-col">
          <nav className="flex-1 px-2 pb-4 space-y-1">
            {navigationItems.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={`${
                  item.current
                    ? 'bg-primary-50 border-primary-500 text-primary-700'
                    : 'border-transparent text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                } group flex items-center px-2 py-2 text-sm font-medium border-l-4 rounded-r-md transition-colors duration-150`}
                onClick={() => mobile && setSidebarOpen(false)}
              >
                <item.icon
                  className={`${
                    item.current ? 'text-primary-500' : 'text-gray-400 group-hover:text-gray-500'
                  } mr-3 flex-shrink-0 h-6 w-6`}
                />
                {item.name}
              </Link>
            ))}
          </nav>
        </div>

        {/* User Menu */}
        <div className="flex-shrink-0 flex border-t border-gray-200 p-4">
          <div className="flex items-center w-full group">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center">
                <span className="text-white text-sm font-medium">
                  {user?.username?.charAt(0).toUpperCase()}
                </span>
              </div>
            </div>
            <div className="ml-3 flex-1">
              <p className="text-sm font-medium text-gray-700">{user?.username}</p>
              <p className="text-xs text-gray-500 capitalize">{user?.role}</p>
            </div>
            <button
              onClick={handleLogout}
              className="ml-3 p-1 text-gray-400 hover:text-gray-500"
              title="Logout"
            >
              <ArrowRightOnRectangleIcon className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );

  return (
    <div className="h-screen flex overflow-hidden bg-gray-50">
      {/* Mobile sidebar */}
      {sidebarOpen && (
        <div className="fixed inset-0 flex z-40 md:hidden">
          <div
            className="fixed inset-0 bg-gray-600 bg-opacity-75"
            onClick={() => setSidebarOpen(false)}
          />
          <div className="relative flex-1 flex flex-col max-w-xs w-full bg-white">
            <div className="absolute top-0 right-0 -mr-12 pt-2">
              <button
                className="ml-1 flex items-center justify-center h-10 w-10 rounded-full focus:outline-none focus:ring-2 focus:ring-inset focus:ring-white"
                onClick={() => setSidebarOpen(false)}
              >
                <XMarkIcon className="h-6 w-6 text-white" />
              </button>
            </div>
            <Sidebar mobile />
          </div>
        </div>
      )}

      {/* Static sidebar for desktop */}
      <Sidebar />

      {/* Main content */}
      <div className="flex flex-col w-0 flex-1 overflow-hidden md:ml-64">
        {/* Top bar */}
        <div className="relative z-10 flex-shrink-0 flex h-16 bg-white border-b border-gray-200">
          <button
            className="px-4 border-r border-gray-200 text-gray-500 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500 md:hidden"
            onClick={() => setSidebarOpen(true)}
          >
            <Bars3Icon className="h-6 w-6" />
          </button>
          
          <div className="flex-1 px-4 flex justify-between items-center">
            <div className="flex-1">
              {/* Breadcrumb or page title could go here */}
            </div>
            
            <div className="ml-4 flex items-center md:ml-6 space-x-3">
              {/* Notifications */}
              <button className="p-1 text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
                <BellIcon className="h-6 w-6" />
              </button>

              {/* Profile dropdown - simplified for now */}
              <div className="relative">
                <button className="flex items-center text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
                  <div className="w-8 h-8 bg-primary-500 rounded-full flex items-center justify-center">
                    <span className="text-white text-sm font-medium">
                      {user?.username?.charAt(0).toUpperCase()}
                    </span>
                  </div>
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Page content */}
        <main className="flex-1 relative overflow-y-auto focus:outline-none">
          <div className="py-6">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8">
              {children}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;