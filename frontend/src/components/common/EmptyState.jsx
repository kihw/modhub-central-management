import React from 'react';
import { FiInfo, FiPlus, FiSettings, FiAlertCircle } from 'react-icons/fi';

const VARIANTS = {
  info: {
    icon: FiInfo,
    buttonVariant: 'primary',
    color: 'blue',
  },
  warning: {
    icon: FiAlertCircle,
    buttonVariant: 'warning',
    color: 'yellow',
  },
  error: {
    icon: FiAlertCircle,
    buttonVariant: 'danger',
    color: 'red',
  },
  noData: {
    icon: FiInfo,
    buttonVariant: 'primary',
    color: 'gray',
  },
  setup: {
    icon: FiSettings,
    buttonVariant: 'secondary',
    color: 'purple',
  },
};

const EmptyState = ({
  title = 'No data available',
  description = 'There is no data to display at the moment.',
  actionText = '',
  variant = 'noData',
  onActionClick = null,
  className = '',
  icon: CustomIcon = null,
}) => {
  const variantConfig = VARIANTS[variant] || VARIANTS.noData;
  const Icon = CustomIcon || variantConfig.icon;
  
  const iconColorClass = `text-${variantConfig.color}-500`;
  const titleColorClass = variant === 'noData' ? 'text-gray-700' : `text-${variantConfig.color}-700`;

  return (
    <div className={`flex flex-col items-center justify-center p-8 text-center rounded-lg border border-gray-200 ${className}`}>
      <div className={`rounded-full p-3 mb-4 bg-${variantConfig.color}-100`}>
        <Icon className={`w-8 h-8 ${iconColorClass}`} />
      </div>
      
      <h3 className={`mb-2 text-lg font-medium ${titleColorClass}`}>{title}</h3>
      
      <p className="mb-5 text-sm text-gray-500 max-w-md mx-auto">
        {description}
      </p>
      
      {actionText && onActionClick && (
        <button
          onClick={onActionClick}
          className={`inline-flex items-center px-4 py-2 text-sm font-medium rounded-md
            ${variantConfig.buttonVariant === 'primary' ? 'bg-blue-600 hover:bg-blue-700 text-white' : ''}
            ${variantConfig.buttonVariant === 'secondary' ? 'bg-purple-600 hover:bg-purple-700 text-white' : ''}
            ${variantConfig.buttonVariant === 'danger' ? 'bg-red-600 hover:bg-red-700 text-white' : ''}
            ${variantConfig.buttonVariant === 'warning' ? 'bg-yellow-500 hover:bg-yellow-600 text-white' : ''}
          `}
        >
          <FiPlus className="mr-2 -ml-1 w-5 h-5" />
          {actionText}
        </button>
      )}
    </div>
  );
};

export default EmptyState;