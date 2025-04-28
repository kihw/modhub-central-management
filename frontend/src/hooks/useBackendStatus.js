import { useEffect, useState } from "react";

export const useBackendStatus = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkBackend = async () => {
      try {
        const response = await fetch("/api/status");
        if (response.ok) {
          setIsConnected(true);
        } else {
          setIsConnected(false);
        }
      } catch (error) {
        setIsConnected(false);
      } finally {
        setLoading(false);
      }
    };

    checkBackend();

    // Optionnel : rafraîchir toutes les X secondes
    const interval = setInterval(checkBackend, 10000); // 10 sec
    return () => clearInterval(interval);
  }, []);

  return { isConnected, loading };
};
