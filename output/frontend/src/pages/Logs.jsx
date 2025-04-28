import React, { useState, useEffect, useRef } from 'react';
import { Box, Typography, Paper, Chip, TextField, IconButton, CircularProgress, Tooltip } from '@mui/material';
import { Download as DownloadIcon, Refresh as RefreshIcon, Delete as DeleteIcon, Search as SearchIcon, Clear as ClearIcon } from '@mui/icons-material';
import { formatDistanceToNow } from 'date-fns';
import { fr } from 'date-fns/locale';
import { useSnackbar } from 'notistack';
import { ipcRenderer } from 'electron';

const Logs = () => {
  const [logs, setLogs] = useState([]);
  const [filteredLogs, setFilteredLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [autoRefresh, setAutoRefresh] = useState(false);
  const { enqueueSnackbar } = useSnackbar();
  const logsEndRef = useRef(null);
  const refreshIntervalRef = useRef(null);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const response = await ipcRenderer.invoke('get-logs');
      
      if (response.success) {
        const formattedLogs = response.logs.map(log => ({
          ...log,
          timestamp: new Date(log.timestamp),
        })).sort((a, b) => b.timestamp - a.timestamp);
        
        setLogs(formattedLogs);
        applyFilter(formattedLogs, searchTerm);
      } else {
        enqueueSnackbar('Erreur lors du chargement des logs', { variant: 'error' });
      }
    } catch (error) {
      console.error('Erreur lors du chargement des logs:', error);
      enqueueSnackbar('Impossible de charger les logs', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const applyFilter = (logsList, term) => {
    if (!term) {
      setFilteredLogs(logsList);
      return;
    }
    
    const filtered = logsList.filter(log => 
      log.message.toLowerCase().includes(term.toLowerCase()) || 
      log.level.toLowerCase().includes(term.toLowerCase()) ||
      (log.source && log.source.toLowerCase().includes(term.toLowerCase()))
    );
    
    setFilteredLogs(filtered);
  };

  const handleSearchChange = (event) => {
    const term = event.target.value;
    setSearchTerm(term);
    applyFilter(logs, term);
  };

  const clearSearch = () => {
    setSearchTerm('');
    setFilteredLogs(logs);
  };

  const downloadLogs = async () => {
    try {
      const result = await ipcRenderer.invoke('export-logs');
      
      if (result.success) {
        enqueueSnackbar(`Logs exportés avec succès: ${result.path}`, { variant: 'success' });
      } else {
        enqueueSnackbar("Échec de l'exportation des logs", { variant: 'error' });
      }
    } catch (error) {
      console.error("Erreur lors de l'exportation des logs:", error);
      enqueueSnackbar("Impossible d'exporter les logs", { variant: 'error' });
    }
  };

  const clearLogs = async () => {
    if (window.confirm('Êtes-vous sûr de vouloir effacer tous les logs?')) {
      try {
        const result = await ipcRenderer.invoke('clear-logs');
        
        if (result.success) {
          setLogs([]);
          setFilteredLogs([]);
          enqueueSnackbar('Logs effacés avec succès', { variant: 'success' });
        } else {
          enqueueSnackbar('Échec de la suppression des logs', { variant: 'error' });
        }
      } catch (error) {
        console.error('Erreur lors de la suppression des logs:', error);
        enqueueSnackbar('Impossible de supprimer les logs', { variant: 'error' });
      }
    }
  };

  const toggleAutoRefresh = () => {
    setAutoRefresh(!autoRefresh);
  };

  useEffect(() => {
    fetchLogs();

    // Écouter les nouveaux logs
    const newLogListener = (event, newLog) => {
      setLogs(prevLogs => {
        const updatedLogs = [{
          ...newLog,
          timestamp: new Date(newLog.timestamp)
        }, ...prevLogs];
        
        applyFilter(updatedLogs, searchTerm);
        return updatedLogs;
      });
    };

    ipcRenderer.on('new-log', newLogListener);

    return () => {
      ipcRenderer.removeListener('new-log', newLogListener);
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current);
      }
    };
  }, []);

  useEffect(() => {
    if (autoRefresh) {
      refreshIntervalRef.current = setInterval(fetchLogs, 5000);
    } else if (refreshIntervalRef.current) {
      clearInterval(refreshIntervalRef.current);
    }

    return () => {
      if (refreshIntervalRef.current) {
        clearInterval(refreshIntervalRef.current);
      }
    };
  }, [autoRefresh]);

  useEffect(() => {
    if (logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [filteredLogs]);

  const getLevelColor = (level) => {
    switch (level.toLowerCase()) {
      case 'error':
        return 'error';
      case 'warn':
        return 'warning';
      case 'info':
        return 'info';
      case 'debug':
        return 'default';
      default:
        return 'default';
    }
  };

  const formatTimestamp = (timestamp) => {
    try {
      return formatDistanceToNow(new Date(timestamp), { addSuffix: true, locale: fr });
    } catch (error) {
      return 'Date invalide';
    }
  };

  return (
    <Box sx={{ padding: 3, maxWidth: '100%', height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <Typography variant="h4" gutterBottom>
        Journaux système
      </Typography>
      
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2, gap: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', flex: 1, bgcolor: 'background.paper', borderRadius: 1 }}>
          <IconButton sx={{ p: '10px' }} aria-label="search">
            <SearchIcon />
          </IconButton>
          <TextField
            fullWidth
            variant="standard"
            placeholder="Rechercher dans les logs..."
            value={searchTerm}
            onChange={handleSearchChange}
            InputProps={{ disableUnderline: true }}
            sx={{ ml: 1 }}
          />
          {searchTerm && (
            <IconButton sx={{ p: '10px' }} aria-label="clear" onClick={clearSearch}>
              <ClearIcon />
            </IconButton>
          )}
        </Box>
        
        <Tooltip title="Actualiser">
          <IconButton onClick={fetchLogs} color={autoRefresh ? 'primary' : 'default'} onClick={toggleAutoRefresh}>
            <RefreshIcon />
          </IconButton>
        </Tooltip>
        
        <Tooltip title="Télécharger les logs">
          <IconButton onClick={downloadLogs}>
            <DownloadIcon />
          </IconButton>
        </Tooltip>
        
        <Tooltip title="Effacer les logs">
          <IconButton onClick={clearLogs} color="error">
            <DeleteIcon />
          </IconButton>
        </Tooltip>
      </Box>

      <Paper 
        elevation={3} 
        sx={{ 
          flex: 1, 
          overflow: 'auto', 
          bgcolor: 'background.paper', 
          p: 2,
          mb: 2,
          borderRadius: 2 
        }}
      >
        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
            <CircularProgress />
          </Box>
        ) : filteredLogs.length === 0 ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%', color: 'text.secondary' }}>
            <Typography>
              {searchTerm ? 'Aucun résultat trouvé' : 'Aucun log disponible'}
            </Typography>
          </Box>
        ) : (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            {filteredLogs.map((log, index) => (
              <Box 
                key={index} 
                sx={{ 
                  p: 1.5, 
                  borderRadius: 1,
                  backgroundColor: index % 2 === 0 ? 'rgba(0, 0, 0, 0.03)' : 'transparent',
                  border: '1px solid',
                  borderColor: 'divider'
                }}
              >
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5, alignItems: 'center' }}>
                  <Chip 
                    label={log.level} 
                    size="small" 
                    color={getLevelColor(log.level)} 
                    sx={{ minWidth: 70, mr: 1 }}
                  />
                  
                  {log.source && (
                    <Chip 
                      label={log.source} 
                      size="small" 
                      variant="outlined"
                      sx={{ mr: 1 }}
                    />
                  )}
                  
                  <Typography variant="caption" color="text.secondary" sx={{ ml: 'auto' }}>
                    {formatTimestamp(log.timestamp)}
                  </Typography>
                </Box>
                
                <Typography 
                  variant="body2" 
                  sx={{ 
                    whiteSpace: 'pre-wrap', 
                    wordBreak: 'break-word',
                    fontFamily: 'monospace' 
                  }}
                >
                  {log.message}
                </Typography>
              </Box>
            ))}
            <div ref={logsEndRef} />
          </Box>
        )}
      </Paper>
      
      {filteredLogs.length > 0 && (
        <Typography variant="body2" color="text.secondary" align="right">
          {filteredLogs.length} {filteredLogs.length === 1 ? 'entrée' : 'entrées'} 
          {searchTerm && logs.length !== filteredLogs.length 
            ? ` (sur ${logs.length} au total)` 
            : ''}
        </Typography>
      )}
    </Box>
  );
};

export default Logs;