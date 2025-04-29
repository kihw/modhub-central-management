import React from 'react';
import { FiAlertTriangle, FiRefreshCw, FiDatabase, FiTerminal } from 'react-icons/fi';

const ConnectionError = ({ 
  message = "Impossible de se connecter au service backend", 
  details = "Le service est peut-être arrêté ou inaccessible.",
  onRetry = null,
  className = "",
  error = null
}) => {
  const troubleshootSteps = [
    "Vérifiez que le script 'run.py' est en cours d'exécution",
    "Assurez-vous que le port 8668 est disponible et non bloqué par un pare-feu",
    "Vérifiez les logs dans le terminal qui exécute le script",
    "Redémarrez l'application complètement si le problème persiste"
  ];

  // Extract more specific error information if available
  const errorDetails = error ? (
    <div className="mt-2 p-2 bg-red-100 border-l-4 border-red-500 text-xs font-mono overflow-x-auto">
      {error.message || JSON.stringify(error)}
    </div>
  ) : null;

  return (
    <div className={`bg-red-50 border-l-4 border-red-500 p-4 rounded-md shadow-sm ${className}`}>
      <div className="flex flex-col">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <FiAlertTriangle className="h-6 w-6 text-red-500" aria-hidden="true" />
          </div>
          <div className="ml-3">
            <h3 className="text-lg font-medium text-red-800">Erreur de connexion</h3>
            <div className="mt-2 text-sm text-red-700">
              <p>{message}</p>
              <p className="mt-1 text-sm text-red-600">{details}</p>
              {errorDetails}
            </div>
          </div>
        </div>
        
        <div className="mt-4 ml-9">
          <h4 className="text-sm font-medium text-red-800">Étapes de dépannage:</h4>
          <ul className="list-disc pl-5 mt-1 text-xs text-red-700 space-y-1">
            {troubleshootSteps.map((step, index) => (
              <li key={index}>{step}</li>
            ))}
          </ul>
        </div>
        
        <div className="mt-4 ml-9 flex flex-col sm:flex-row gap-3">
          {onRetry && (
            <button
              type="button"
              onClick={onRetry}
              className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              <FiRefreshCw className="mr-2 -ml-0.5 h-4 w-4" aria-hidden="true" />
              Réessayer la connexion
            </button>
          )}
          
          <button
            type="button"
            onClick={() => {
              window.location.reload();
            }}
            className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <FiRefreshCw className="mr-2 -ml-0.5 h-4 w-4" aria-hidden="true" />
            Recharger l'application
          </button>

          <button
            type="button"
            onClick={() => {
              // For development purposes, could link to docs or repository
              window.open('https://github.com/kihw/modhub-central-management', '_blank');
            }}
            className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-gray-700 bg-gray-100 hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
          >
            <FiTerminal className="mr-2 -ml-0.5 h-4 w-4" aria-hidden="true" />
            Documentation
          </button>
        </div>
        
        <div className="mt-4 ml-9 pt-3 border-t border-red-200">
          <div className="flex items-center">
            <FiDatabase className="text-red-500 mr-2" />
            <p className="text-xs text-red-700">
              Adresse du backend: <span className="font-mono">http://localhost:8668</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ConnectionError;