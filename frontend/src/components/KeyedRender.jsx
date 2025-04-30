import React, { useState, useEffect } from 'react';

/**
 * KeyedRender is a component that helps with unmounting and remounting components
 * when data changes significantly. This can help avoid DOM reconciliation issues
 * 
 * @param {Object} props
 * @param {any} props.value - Value to derive key from
 * @param {React.ReactNode} props.children - Child components to render
 * @param {boolean} props.disabled - If true, behaves like a normal Fragment
 * @returns {React.ReactNode}
 * 
 * @example
 * // Will completely unmount and remount children when userId changes
 * <KeyedRender value={userId}>
 *   <UserProfile user={user} />
 * </KeyedRender>
 */
function KeyedRender({ value, children, disabled = false }) {
  const [key, setKey] = useState(0);
  
  useEffect(() => {
    if (!disabled) {
      // Generate a new key when value changes significantly
      setKey(prevKey => prevKey + 1);
    }
  }, [value, disabled]);
  
  if (disabled) {
    return <>{children}</>;
  }
  
  return (
    <React.Fragment key={key}>
      {children}
    </React.Fragment>
  );
}

export default KeyedRender;