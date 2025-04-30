import { useState, useEffect, useCallback } from "react";
import axios from "axios";

const useFetch = (url, options = {}) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const {
    immediate = true,
    interval = null,
    transform = (data) => data,
  } = options;

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      const response = await axios.get(url);
      setData(transform(response.data));
      setError(null);
    } catch (err) {
      setError(err.message || "Une erreur est survenue");
      console.error(
        `Erreur lors de la récupération des données depuis ${url}:`,
        err
      );
    } finally {
      setLoading(false);
    }
  }, [url, transform]);

  useEffect(() => {
    if (immediate) {
      fetchData();
    }

    if (interval) {
      const intervalId = setInterval(fetchData, interval);
      return () => clearInterval(intervalId);
    }
  }, [fetchData, immediate, interval]);

  return { data, loading, error, refetch: fetchData };
};

export default useFetch;
