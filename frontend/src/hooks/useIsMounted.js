import { useRef, useEffect } from 'react';

/**
 * Custom hook to track if a component is mounted
 * Use this to prevent state updates after unmounting
 * 
 * @returns {React.MutableRefObject<boolean>} A ref that's true when component is mounted
 * 
 * @example
 * const isMounted = useIsMounted();
 * 
 * useEffect(() => {
 *   fetchData().then(data => {
 *     // Only update state if component is still mounted
 *     if (isMounted.current) {
 *       setData(data);
 *     }
 *   });
 * }, []);
 */
function useIsMounted() {
  const isMounted = useRef(false);
  
  useEffect(() => {
    isMounted.current = true;
    
    return () => {
      isMounted.current = false;
    };
  }, []);
  
  return isMounted;
}

export default useIsMounted;