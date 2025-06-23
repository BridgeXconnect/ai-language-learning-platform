import React, { useState, useEffect, useRef, forwardRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  XMarkIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  InformationCircleIcon,
  XCircleIcon,
  ChevronDownIcon,
  ChevronUpIcon,
  MagnifyingGlassIcon,
  EyeIcon,
  EyeSlashIcon,
  CalendarDaysIcon,
  ClockIcon,
  StarIcon,
  HeartIcon,
  ShareIcon,
  BookmarkIcon,
  PlusIcon,
  MinusIcon,
  ArrowUpIcon,
  ArrowDownIcon,
  ArrowLeftIcon,
  ArrowRightIcon
} from '@heroicons/react/24/outline';
import { 
  CheckCircleIcon as CheckCircleIconSolid,
  ExclamationTriangleIcon as ExclamationTriangleIconSolid,
  InformationCircleIcon as InformationCircleIconSolid,
  XCircleIcon as XCircleIconSolid,
  StarIcon as StarIconSolid,
  HeartIcon as HeartIconSolid,
  BookmarkIcon as BookmarkIconSolid
} from '@heroicons/react/24/solid';

// Enhanced Button Component
export const Button = forwardRef(({ 
  children, 
  variant = 'primary', 
  size = 'md', 
  loading = false,
  disabled = false,
  icon: Icon = null,
  iconPosition = 'left',
  fullWidth = false,
  className = '',
  ...props 
}, ref) => {
  const baseClasses = `btn btn-${variant} btn-${size}`;
  const loadingClasses = loading ? 'btn-loading' : '';
  const widthClasses = fullWidth ? 'w-full' : '';
  
  return (
    <motion.button
      ref={ref}
      disabled={disabled || loading}
      className={`${baseClasses} ${loadingClasses} ${widthClasses} ${className}`}
      whileHover={{ scale: disabled || loading ? 1 : 1.02 }}
      whileTap={{ scale: disabled || loading ? 1 : 0.98 }}
      transition={{ duration: 0.15, ease: "easeOut" }}
      {...props}
    >
      {!loading && Icon && iconPosition === 'left' && <Icon className="h-4 w-4" />}
      {loading ? 'Loading...' : children}
      {!loading && Icon && iconPosition === 'right' && <Icon className="h-4 w-4" />}
    </motion.button>
  );
});

Button.displayName = 'Button';

// Enhanced Input Component
export const Input = forwardRef(({ 
  label,
  error,
  help,
  icon: Icon = null,
  iconPosition = 'left',
  type = 'text',
  className = '',
  containerClassName = '',
  ...props 
}, ref) => {
  const [showPassword, setShowPassword] = useState(false);
  const inputType = type === 'password' && showPassword ? 'text' : type;
  
  return (
    <div className={`form-group ${containerClassName}`}>
      {label && (
        <label className="form-label">
          {label}
        </label>
      )}
      <div className="relative">
        {Icon && iconPosition === 'left' && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Icon className="h-5 w-5 text-neutral-400" />
          </div>
        )}
        <input
          ref={ref}
          type={inputType}
          className={`form-input ${error ? 'form-input-error' : ''} ${
            Icon && iconPosition === 'left' ? 'pl-10' : ''
          } ${
            type === 'password' || (Icon && iconPosition === 'right') ? 'pr-10' : ''
          } ${className}`}
          {...props}
        />
        {type === 'password' && (
          <button
            type="button"
            className="absolute inset-y-0 right-0 pr-3 flex items-center"
            onClick={() => setShowPassword(!showPassword)}
          >
            {showPassword ? (
              <EyeSlashIcon className="h-5 w-5 text-neutral-400 hover:text-neutral-600" />
            ) : (
              <EyeIcon className="h-5 w-5 text-neutral-400 hover:text-neutral-600" />
            )}
          </button>
        )}
        {Icon && iconPosition === 'right' && type !== 'password' && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            <Icon className="h-5 w-5 text-neutral-400" />
          </div>
        )}
      </div>
      {error && (
        <div className="form-error">
          <XCircleIcon className="h-4 w-4" />
          {error}
        </div>
      )}
      {help && !error && (
        <div className="form-help">
          {help}
        </div>
      )}
    </div>
  );
});

Input.displayName = 'Input';

// Enhanced Select Component
export const Select = forwardRef(({ 
  label,
  error,
  help,
  options = [],
  placeholder = 'Select an option',
  className = '',
  containerClassName = '',
  ...props 
}, ref) => {
  return (
    <div className={`form-group ${containerClassName}`}>
      {label && (
        <label className="form-label">
          {label}
        </label>
      )}
      <div className="relative">
        <select
          ref={ref}
          className={`form-input appearance-none pr-10 ${error ? 'form-input-error' : ''} ${className}`}
          {...props}
        >
          {placeholder && (
            <option value="" disabled>
              {placeholder}
            </option>
          )}
          {options.map((option, index) => (
            <option key={index} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
        <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
          <ChevronDownIcon className="h-5 w-5 text-neutral-400" />
        </div>
      </div>
      {error && (
        <div className="form-error">
          <XCircleIcon className="h-4 w-4" />
          {error}
        </div>
      )}
      {help && !error && (
        <div className="form-help">
          {help}
        </div>
      )}
    </div>
  );
});

Select.displayName = 'Select';

// Enhanced Textarea Component
export const Textarea = forwardRef(({ 
  label,
  error,
  help,
  rows = 4,
  className = '',
  containerClassName = '',
  ...props 
}, ref) => {
  return (
    <div className={`form-group ${containerClassName}`}>
      {label && (
        <label className="form-label">
          {label}
        </label>
      )}
      <textarea
        ref={ref}
        rows={rows}
        className={`form-input resize-none ${error ? 'form-input-error' : ''} ${className}`}
        {...props}
      />
      {error && (
        <div className="form-error">
          <XCircleIcon className="h-4 w-4" />
          {error}
        </div>
      )}
      {help && !error && (
        <div className="form-help">
          {help}
        </div>
      )}
    </div>
  );
});

Textarea.displayName = 'Textarea';

// Enhanced Card Component
export const Card = ({ 
  children, 
  variant = 'default',
  interactive = false,
  className = '',
  ...props 
}) => {
  const variantClasses = {
    default: 'card',
    elevated: 'card card-elevated',
    interactive: 'card card-interactive'
  };

  return (
    <motion.div 
      className={`${variantClasses[variant]} ${interactive ? 'card-interactive' : ''} ${className}`}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      whileHover={interactive ? { y: -2, boxShadow: "0 10px 25px 0 rgba(0, 0, 0, 0.1)" } : {}}
      {...props}
    >
      {children}
    </motion.div>
  );
};

export const CardHeader = ({ children, className = '', ...props }) => (
  <div className={`card-header ${className}`} {...props}>
    {children}
  </div>
);

export const CardBody = ({ children, className = '', ...props }) => (
  <div className={`card-body ${className}`} {...props}>
    {children}
  </div>
);

export const CardFooter = ({ children, className = '', ...props }) => (
  <div className={`card-footer ${className}`} {...props}>
    {children}
  </div>
);

// Enhanced Badge Component
export const Badge = ({ 
  children, 
  variant = 'neutral', 
  size = 'md',
  icon: Icon = null,
  className = '',
  ...props 
}) => {
  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5',
    md: 'text-xs px-2.5 py-1',
    lg: 'text-sm px-3 py-1.5'
  };

  return (
    <span 
      className={`badge badge-${variant} ${sizeClasses[size]} ${className}`}
      {...props}
    >
      {Icon && <Icon className="h-3 w-3" />}
      {children}
    </span>
  );
};

// Enhanced Alert Component
export const Alert = ({ 
  children, 
  variant = 'info', 
  dismissible = false,
  onDismiss,
  className = '',
  ...props 
}) => {
  const [visible, setVisible] = useState(true);

  const icons = {
    success: CheckCircleIconSolid,
    warning: ExclamationTriangleIconSolid,
    error: XCircleIconSolid,
    info: InformationCircleIconSolid
  };

  const Icon = icons[variant];

  const handleDismiss = () => {
    setVisible(false);
    if (onDismiss) onDismiss();
  };

  if (!visible) return null;

  return (
    <motion.div 
      className={`alert alert-${variant} ${className}`} 
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      {...props}
    >
      <Icon className="h-5 w-5 flex-shrink-0" />
      <div className="flex-1">{children}</div>
      {dismissible && (
        <motion.button
          onClick={handleDismiss}
          className="flex-shrink-0 ml-2 p-1 rounded-md hover:bg-black/10 transition-colors"
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.9 }}
        >
          <XMarkIcon className="h-4 w-4" />
        </motion.button>
      )}
    </motion.div>
  );
};

// Enhanced Modal Component
export const Modal = ({ 
  isOpen, 
  onClose, 
  title,
  children,
  size = 'md',
  className = '',
  ...props 
}) => {
  const sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
    full: 'max-w-7xl'
  };

  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <>
      <div 
        className={`modal-backdrop ${isOpen ? 'active' : ''}`}
        onClick={onClose}
      />
      <div className={`modal ${isOpen ? 'active' : ''} ${sizeClasses[size]} ${className}`} {...props}>
        {title && (
          <div className="modal-header">
            <h3 className="heading-lg">{title}</h3>
            <button
              onClick={onClose}
              className="p-2 hover:bg-neutral-100 rounded-lg transition-colors"
            >
              <XMarkIcon className="h-5 w-5" />
            </button>
          </div>
        )}
        <div className="modal-body">
          {children}
        </div>
      </div>
    </>
  );
};

// Enhanced Tooltip Component
export const Tooltip = ({ 
  children, 
  content, 
  position = 'top',
  className = '',
  ...props 
}) => {
  const [visible, setVisible] = useState(false);

  const positionClasses = {
    top: 'bottom-full left-1/2 transform -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 transform -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 transform -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 transform -translate-y-1/2 ml-2'
  };

  return (
    <div 
      className={`tooltip relative inline-block ${className}`}
      onMouseEnter={() => setVisible(true)}
      onMouseLeave={() => setVisible(false)}
      {...props}
    >
      {children}
      {visible && (
        <div className={`absolute z-tooltip bg-neutral-900 text-white text-xs px-2 py-1 rounded whitespace-nowrap ${positionClasses[position]}`}>
          {content}
        </div>
      )}
    </div>
  );
};

// Enhanced Dropdown Component
export const Dropdown = ({ 
  trigger, 
  children, 
  position = 'bottom-left',
  className = '',
  ...props 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  const positionClasses = {
    'bottom-left': 'top-full left-0 mt-2',
    'bottom-right': 'top-full right-0 mt-2',
    'top-left': 'bottom-full left-0 mb-2',
    'top-right': 'bottom-full right-0 mb-2'
  };

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className={`relative inline-block ${className}`} ref={dropdownRef} {...props}>
      <div onClick={() => setIsOpen(!isOpen)}>
        {trigger}
      </div>
      {isOpen && (
        <div className={`absolute z-dropdown bg-white border border-neutral-200 rounded-lg shadow-lg py-2 min-w-48 ${positionClasses[position]}`}>
          {children}
        </div>
      )}
    </div>
  );
};

export const DropdownItem = ({ 
  children, 
  onClick,
  icon: Icon = null,
  className = '',
  ...props 
}) => (
  <button
    className={`w-full text-left px-4 py-2 text-sm text-neutral-700 hover:bg-neutral-100 flex items-center space-x-2 ${className}`}
    onClick={onClick}
    {...props}
  >
    {Icon && <Icon className="h-4 w-4" />}
    <span>{children}</span>
  </button>
);

// Enhanced Progress Component
export const Progress = ({ 
  value = 0, 
  max = 100, 
  variant = 'primary',
  size = 'md',
  showLabel = false,
  className = '',
  ...props 
}) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);
  
  const sizeClasses = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3'
  };

  return (
    <div className={`space-y-2 ${className}`} {...props}>
      {showLabel && (
        <div className="flex justify-between text-sm">
          <span className="text-neutral-700">Progress</span>
          <span className="text-neutral-500">{Math.round(percentage)}%</span>
        </div>
      )}
      <div className={`progress ${sizeClasses[size]}`}>
        <div 
          className={`progress-bar progress-bar-${variant}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};

// Enhanced Rating Component
export const Rating = ({ 
  value = 0, 
  max = 5, 
  onChange,
  readonly = false,
  size = 'md',
  className = '',
  ...props 
}) => {
  const [hoverValue, setHoverValue] = useState(0);
  
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-5 w-5',
    lg: 'h-6 w-6'
  };

  const handleClick = (rating) => {
    if (!readonly && onChange) {
      onChange(rating);
    }
  };

  return (
    <div className={`flex items-center space-x-1 ${className}`} {...props}>
      {[...Array(max)].map((_, index) => {
        const rating = index + 1;
        const filled = rating <= (hoverValue || value);
        
        return (
          <button
            key={index}
            type="button"
            disabled={readonly}
            className={`${readonly ? 'cursor-default' : 'cursor-pointer hover:scale-110'} transition-transform`}
            onClick={() => handleClick(rating)}
            onMouseEnter={() => !readonly && setHoverValue(rating)}
            onMouseLeave={() => !readonly && setHoverValue(0)}
          >
            {filled ? (
              <StarIconSolid className={`${sizeClasses[size]} text-yellow-400`} />
            ) : (
              <StarIcon className={`${sizeClasses[size]} text-neutral-300`} />
            )}
          </button>
        );
      })}
    </div>
  );
};

// Enhanced Toggle Component
export const Toggle = ({ 
  checked = false, 
  onChange,
  label,
  description,
  disabled = false,
  size = 'md',
  className = '',
  ...props 
}) => {
  const sizeClasses = {
    sm: 'h-5 w-9',
    md: 'h-6 w-11',
    lg: 'h-7 w-14'
  };

  const thumbSizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-5 w-5',
    lg: 'h-6 w-6'
  };

  return (
    <div className={`flex items-start space-x-3 ${className}`} {...props}>
      <button
        type="button"
        disabled={disabled}
        className={`relative inline-flex ${sizeClasses[size]} flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 ${
          checked ? 'bg-primary-600' : 'bg-neutral-200'
        } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
        onClick={() => !disabled && onChange && onChange(!checked)}
      >
        <span
          className={`pointer-events-none inline-block ${thumbSizeClasses[size]} transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
            checked ? 'translate-x-5' : 'translate-x-0'
          }`}
        />
      </button>
      {(label || description) && (
        <div className="flex-1">
          {label && (
            <label className="body-sm font-medium text-neutral-900">
              {label}
            </label>
          )}
          {description && (
            <p className="body-xs text-neutral-500">
              {description}
            </p>
          )}
        </div>
      )}
    </div>
  );
};

// Enhanced Tabs Component
export const Tabs = ({ 
  tabs = [], 
  activeTab, 
  onChange,
  variant = 'default',
  className = '',
  ...props 
}) => {
  const variantClasses = {
    default: 'border-b border-neutral-200',
    pills: 'bg-neutral-100 p-1 rounded-lg',
    underline: ''
  };

  return (
    <div className={`${className}`} {...props}>
      <div className={`flex space-x-1 ${variantClasses[variant]}`}>
        {tabs.map((tab, index) => {
          const isActive = activeTab === tab.id;
          
          return (
            <button
              key={tab.id}
              className={`px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                variant === 'pills' 
                  ? isActive 
                    ? 'bg-white text-primary-700 shadow-sm' 
                    : 'text-neutral-600 hover:text-neutral-900'
                  : variant === 'underline'
                  ? isActive
                    ? 'text-primary-600 border-b-2 border-primary-600'
                    : 'text-neutral-600 hover:text-neutral-900 border-b-2 border-transparent'
                  : isActive
                  ? 'text-primary-600 border-b-2 border-primary-600'
                  : 'text-neutral-600 hover:text-neutral-900'
              }`}
              onClick={() => onChange && onChange(tab.id)}
            >
              {tab.icon && <tab.icon className="h-4 w-4 mr-2 inline" />}
              {tab.label}
              {tab.count !== undefined && (
                <Badge variant="neutral" size="sm" className="ml-2">
                  {tab.count}
                </Badge>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
};

// Enhanced Accordion Component
export const Accordion = ({ 
  items = [], 
  allowMultiple = false,
  className = '',
  ...props 
}) => {
  const [openItems, setOpenItems] = useState(new Set());

  const toggleItem = (index) => {
    const newOpenItems = new Set(openItems);
    
    if (newOpenItems.has(index)) {
      newOpenItems.delete(index);
    } else {
      if (!allowMultiple) {
        newOpenItems.clear();
      }
      newOpenItems.add(index);
    }
    
    setOpenItems(newOpenItems);
  };

  return (
    <div className={`space-y-2 ${className}`} {...props}>
      {items.map((item, index) => {
        const isOpen = openItems.has(index);
        
        return (
          <div key={index} className="card">
            <button
              className="card-header w-full text-left flex items-center justify-between hover:bg-neutral-50 transition-colors"
              onClick={() => toggleItem(index)}
            >
              <span className="heading-lg">{item.title}</span>
              {isOpen ? (
                <ChevronUpIcon className="h-5 w-5 text-neutral-400" />
              ) : (
                <ChevronDownIcon className="h-5 w-5 text-neutral-400" />
              )}
            </button>
            {isOpen && (
              <div className="card-body animate-fade-in">
                {item.content}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};

// Enhanced Search Input Component
export const SearchInput = ({ 
  placeholder = 'Search...', 
  onSearch,
  debounceMs = 300,
  className = '',
  ...props 
}) => {
  const [value, setValue] = useState('');
  const timeoutRef = useRef(null);

  useEffect(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = setTimeout(() => {
      if (onSearch) {
        onSearch(value);
      }
    }, debounceMs);

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [value, onSearch, debounceMs]);

  return (
    <Input
      type="text"
      placeholder={placeholder}
      value={value}
      onChange={(e) => setValue(e.target.value)}
      icon={MagnifyingGlassIcon}
      iconPosition="left"
      className={className}
      {...props}
    />
  );
};

// Enhanced Pagination Component
export const Pagination = ({ 
  currentPage = 1, 
  totalPages = 1, 
  onPageChange,
  showFirstLast = true,
  showPrevNext = true,
  maxVisiblePages = 5,
  className = '',
  ...props 
}) => {
  const getVisiblePages = () => {
    const pages = [];
    const halfVisible = Math.floor(maxVisiblePages / 2);
    
    let startPage = Math.max(1, currentPage - halfVisible);
    let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
    
    if (endPage - startPage + 1 < maxVisiblePages) {
      startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }
    
    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }
    
    return pages;
  };

  const visiblePages = getVisiblePages();

  return (
    <div className={`flex items-center justify-center space-x-1 ${className}`} {...props}>
      {showFirstLast && currentPage > 1 && (
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onPageChange && onPageChange(1)}
          icon={ArrowLeftIcon}
        >
          First
        </Button>
      )}
      
      {showPrevNext && currentPage > 1 && (
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onPageChange && onPageChange(currentPage - 1)}
          icon={ArrowLeftIcon}
        />
      )}
      
      {visiblePages.map((page) => (
        <Button
          key={page}
          variant={page === currentPage ? 'primary' : 'ghost'}
          size="sm"
          onClick={() => onPageChange && onPageChange(page)}
        >
          {page}
        </Button>
      ))}
      
      {showPrevNext && currentPage < totalPages && (
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onPageChange && onPageChange(currentPage + 1)}
          icon={ArrowRightIcon}
        />
      )}
      
      {showFirstLast && currentPage < totalPages && (
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onPageChange && onPageChange(totalPages)}
          icon={ArrowRightIcon}
        >
          Last
        </Button>
      )}
    </div>
  );
};

export default {
  Button,
  Input,
  Select,
  Textarea,
  Card,
  CardHeader,
  CardBody,
  CardFooter,
  Badge,
  Alert,
  Modal,
  Tooltip,
  Dropdown,
  DropdownItem,
  Progress,
  Rating,
  Toggle,
  Tabs,
  Accordion,
  SearchInput,
  Pagination
}; 