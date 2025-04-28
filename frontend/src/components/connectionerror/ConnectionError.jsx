import React from 'react';
import { FiAlertTriangle, FiRefreshCw } from 'react-icons/fi';

const ConnectionError = ({ 
  message = "Impossible de se connecter au service backend", 
  details = "Le service est peut-être arrêté ou inaccessible.",
  onRetry = null,
  className = ""
}) => {
  return (
    <div className={`bg-red-50 border-l-4 border-red-500 p-4 rounded-md shadow-sm ${className}`}>
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <FiAlertTriangle className="h-6 w-6 text-red-500" aria-hidden="true" />
        </div>
        <div className="ml-3">
          <h3 className="text-lg font-medium text-red-800">Erreur de connexion</h3>
          <div className="mt-2 text-sm text-red-700">
            <p>{message}</p>
            <p className="mt-1 text-sm text-red-600">{details}</p>
          </div>
          {onRetry && (
            <div className="mt-4">
              <button
                type="button"
                onClick={onRetry}
                className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
              >
                <FiRefreshCw className="mr-2 -ml-0.5 h-4 w-4" aria-hidden="true" />
                Réessayer la connexion
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ConnectionError;