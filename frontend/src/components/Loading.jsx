import React, { useEffect, useState } from 'react';

const Loading = ({ text = 'Chargement en cours', fullScreen = false }) => {
  const [dots, setDots] = useState('');
  
  useEffect(() => {
    const interval = setInterval(() => {
      setDots((prevDots) => {
        if (prevDots.length >= 3) return '';
        return prevDots + '.';
      });
    }, 400);
    
    return () => clearInterval(interval);
  }, []);

  const containerClasses = fullScreen
    ? 'fixed inset-0 flex flex-col items-center justify-center bg-gray-900 bg-opacity-80 z-50'
    : 'flex flex-col items-center justify-center p-6';

  return (
    <div
      className={containerClasses}
    >
      <div className="flex flex-col items-center">
        <svg 
          className="w-16 h-16 mb-4" 
          viewBox="0 0 38 38" 
          xmlns="http://www.w3.org/2000/svg"
          stroke="#4f46e5"
        >
          <g fill="none" fillRule="evenodd">
            <g transform="translate(1 1)" strokeWidth="2">
              <circle strokeOpacity=".3" cx="18" cy="18" r="18"/>
              <path d="M36 18c0-9.94-8.06-18-18-18">
                <animateTransform
                  attributeName="transform"
                  type="rotate"
                  from="0 18 18"
                  to="360 18 18"
                  dur="1s"
                  repeatCount="indefinite"
                />
              </path>
            </g>
          </g>
        </svg>
        <div
          className="text-lg text-indigo-100 font-medium"
        >
          {text}{dots}
        </div>
      </div>
    </div>
  );
};

export default Loading;