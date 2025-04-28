import React, { Component } from 'react';
import PropTypes from 'prop-types';

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI.
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    // Catch errors in any components below and re-render with error message
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
    
    // You can also log the error to an error reporting service
    console.error("Error caught by ErrorBoundary:", error, errorInfo);
    
    // Call the onError prop if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  resetError = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
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
        <div className="error-boundary-container p-4 m-4 bg-red-50 border border-red-300 rounded-md">
          <h2 className="text-xl font-bold text-red-700 mb-2">Une erreur est survenue</h2>
          <details className="whitespace-pre-wrap text-red-600 mb-4">
            <summary className="cursor-pointer font-semibold">Voir les détails</summary>
            <p className="mt-2">{this.state.error && this.state.error.toString()}</p>
            <p className="mt-2 text-sm">
              {this.state.errorInfo && this.state.errorInfo.componentStack}
            </p>
          </details>
          <button
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
            onClick={this.resetError}
          >
            Réessayer
          </button>
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