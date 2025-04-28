import React, { useState, useEffect } from 'react';
import { Box, Typography, Paper, Button, Container, Grid, CircularProgress, Snackbar, Alert } from '@mui/material';
import { PlayArrow, Stop, Add, Delete } from '@mui/icons-material';
import AutomationCard from '../components/automation/AutomationCard';
import AutomationFormModal from '../components/automation/AutomationFormModal';
import { useElectronAPI } from '../contexts/ElectronAPIContext';
import { useTheme } from '@mui/material/styles';

const Automation = () => {
  const theme = useTheme();
  const { electronAPI } = useElectronAPI();
  const [automations, setAutomations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [runningAutomations, setRunningAutomations] = useState({});
  const [openModal, setOpenModal] = useState(false);
  const [editingAutomation, setEditingAutomation] = useState(null);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'info'
  });

  useEffect(() => {
    fetchAutomations();
    
    // Set up event listeners for automation status updates
    if (electronAPI) {
      electronAPI.onAutomationStatus((event, { id, status, log }) => {
        if (status === 'running') {
          setRunningAutomations(prev => ({ ...prev, [id]: true }));
        } else if (status === 'stopped') {
          setRunningAutomations(prev => {
            const newState = { ...prev };
            delete newState[id];
            return newState;
          });
        }
        
        if (log) {
          showSnackbar(log, 'info');
        }
      });
    }

    return () => {
      // Clean up event listeners
      if (electronAPI) {
        electronAPI.removeAllListeners('automation-status');
      }
    };
  }, [electronAPI]);

  const fetchAutomations = async () => {
    setLoading(true);
    try {
      if (electronAPI) {
        const result = await electronAPI.getAutomations();
        setAutomations(result || []);
      }
    } catch (error) {
      console.error('Error fetching automations:', error);
      showSnackbar('Failed to fetch automations', 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleStartAutomation = async (id) => {
    try {
      if (electronAPI) {
        await electronAPI.startAutomation(id);
        showSnackbar('Automation started', 'success');
      }
    } catch (error) {
      console.error('Error starting automation:', error);
      showSnackbar('Failed to start automation', 'error');
    }
  };

  const handleStopAutomation = async (id) => {
    try {
      if (electronAPI) {
        await electronAPI.stopAutomation(id);
        showSnackbar('Automation stopped', 'info');
      }
    } catch (error) {
      console.error('Error stopping automation:', error);
      showSnackbar('Failed to stop automation', 'error');
    }
  };

  const handleDeleteAutomation = async (id) => {
    try {
      if (electronAPI) {
        await electronAPI.deleteAutomation(id);
        await fetchAutomations();
        showSnackbar('Automation deleted', 'success');
      }
    } catch (error) {
      console.error('Error deleting automation:', error);
      showSnackbar('Failed to delete automation', 'error');
    }
  };

  const handleCreateAutomation = () => {
    setEditingAutomation(null);
    setOpenModal(true);
  };

  const handleEditAutomation = (automation) => {
    setEditingAutomation(automation);
    setOpenModal(true);
  };

  const handleSaveAutomation = async (automationData) => {
    try {
      if (electronAPI) {
        if (editingAutomation) {
          await electronAPI.updateAutomation({
            ...automationData,
            id: editingAutomation.id
          });
          showSnackbar('Automation updated', 'success');
        } else {
          await electronAPI.createAutomation(automationData);
          showSnackbar('Automation created', 'success');
        }
        await fetchAutomations();
        setOpenModal(false);
      }
    } catch (error) {
      console.error('Error saving automation:', error);
      showSnackbar('Failed to save automation', 'error');
    }
  };

  const showSnackbar = (message, severity = 'info') => {
    setSnackbar({
      open: true,
      message,
      severity
    });
  };

  const handleCloseSnackbar = () => {
    setSnackbar(prev => ({ ...prev, open: false }));
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
          <Typography variant="h4" component="h1" gutterBottom>
            Automations
          </Typography>
          <Button
            variant="contained"
            color="primary"
            startIcon={<Add />}
            onClick={handleCreateAutomation}
          >
            New Automation
          </Button>
        </Box>

        {loading ? (
          <Box display="flex" justifyContent="center" alignItems="center" height="60vh">
            <CircularProgress />
          </Box>
        ) : automations.length === 0 ? (
          <Paper 
            sx={{ 
              p: 4, 
              textAlign: 'center',
              backgroundColor: theme.palette.mode === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.02)'
            }}
          >
            <Typography variant="h6" color="textSecondary" gutterBottom>
              No automations found
            </Typography>
            <Typography variant="body1" color="textSecondary" paragraph>
              Create your first automation to automate your workflows.
            </Typography>
            <Button
              variant="outlined"
              color="primary"
              startIcon={<Add />}
              onClick={handleCreateAutomation}
            >
              Create Automation
            </Button>
          </Paper>
        ) : (
          <Grid container spacing={3}>
            {automations.map((automation) => (
              <Grid item xs={12} sm={6} md={4} key={automation.id}>
                <AutomationCard
                  automation={automation}
                  isRunning={!!runningAutomations[automation.id]}
                  onStart={() => handleStartAutomation(automation.id)}
                  onStop={() => handleStopAutomation(automation.id)}
                  onEdit={() => handleEditAutomation(automation)}
                  onDelete={() => handleDeleteAutomation(automation.id)}
                />
              </Grid>
            ))}
          </Grid>
        )}
      </Box>

      <AutomationFormModal
        open={openModal}
        onClose={() => setOpenModal(false)}
        onSave={handleSaveAutomation}
        automation={editingAutomation}
      />

      <Snackbar 
        open={snackbar.open} 
        autoHideDuration={6000} 
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default Automation;