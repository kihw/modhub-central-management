import React, { Component } from 'react';
import PropTypes from 'prop-types';

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorStack: null
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI.
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // Catch errors in any components below and re-render with error message
    console.error("Error caught by ErrorBoundary:", error, errorInfo);
    
    this.setState({
      error: error,
      errorInfo: errorInfo,
      errorStack: error.stack
    });
    
    // Log to service if needed
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  resetError = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      errorStack: null
    });
  }

  render() {
    if (this.state.hasError) {
      // You can render any custom fallback UI
      if (this.props.fallback) {
        return typeof this.props.fallback === 'function' 
          ? this.props.fallback(this.state.error, this.state.errorInfo, this.resetError)
          : this.props.fallback;
      }
      
      // Default error UI
      return (
        <div className="error-boundary-container p-6 m-4 bg-red-50 border border-red-300 rounded-lg shadow-md">
          <h2 className="text-xl font-bold text-red-700 mb-4">Une erreur est survenue</h2>
          
          <div className="mb-4 p-4 bg-white rounded border border-red-200">
            <p className="text-red-600 font-medium">{this.state.error?.toString()}</p>
            {this.state.error?.message && (
              <p className="mt-2 text-gray-700">{this.state.error.message}</p>
            )}
          </div>
          
          {this.state.errorStack && (
            <details className="mb-4">
              <summary className="cursor-pointer font-semibold text-gray-700 mb-2">
                Stack Trace
              </summary>
              <pre className="whitespace-pre-wrap p-3 bg-gray-100 rounded text-xs overflow-auto max-h-64">
                {this.state.errorStack}
              </pre>
            </details>
          )}
          
          {this.state.errorInfo && (
            <details className="mb-4">
              <summary className="cursor-pointer font-semibold text-gray-700 mb-2">
                Component Stack
              </summary>
              <pre className="whitespace-pre-wrap p-3 bg-gray-100 rounded text-xs overflow-auto max-h-64">
                {this.state.errorInfo.componentStack}
              </pre>
            </details>
          )}
          
          <div className="flex gap-4 mt-6">
            <button
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors shadow-sm"
              onClick={this.resetError}
            >
              Réessayer
            </button>
            
            <button
              className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors shadow-sm"
              onClick={() => window.location.reload()}
            >
              Recharger la page
            </button>
          </div>
        </div>
      );
    }

    // Normally, just render children
    return this.props.children;
  }
}

ErrorBoundary.propTypes = {
  children: PropTypes.node.isRequired,
  fallback: PropTypes.oneOfType([PropTypes.node, PropTypes.func]),
  onError: PropTypes.func
};

export default ErrorBoundary;