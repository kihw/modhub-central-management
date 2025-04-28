import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useDispatch, useSelector } from 'react-redux';
import { 
  Box, 
  Typography, 
  Container, 
  Paper, 
  Button, 
  FormControl, 
  FormControlLabel, 
  Radio, 
  RadioGroup, 
  Divider, 
  TextField, 
  Switch, 
  Select, 
  MenuItem, 
  InputLabel,
  Snackbar,
  Alert
} from '@mui/material';
import { setTheme } from '../redux/slices/themeSlice';
import { setLanguage } from '../redux/slices/languageSlice';
import { updateSettings, resetSettings } from '../redux/slices/settingsSlice';
import { useTheme } from '@mui/material/styles';

const Settings = () => {
  const { t } = useTranslation();
  const dispatch = useDispatch();
  const theme = useTheme();
  const currentTheme = useSelector(state => state.theme.current);
  const currentLanguage = useSelector(state => state.language.current);
  const settings = useSelector(state => state.settings);

  const [localSettings, setLocalSettings] = useState({
    cacheSize: settings.cacheSize || 500,
    autoUpdate: settings.autoUpdate !== undefined ? settings.autoUpdate : true,
    debugMode: settings.debugMode || false,
    apiEndpoint: settings.apiEndpoint || 'https://api.example.com',
    dataExportFormat: settings.dataExportFormat || 'json',
    notificationsEnabled: settings.notificationsEnabled !== undefined ? settings.notificationsEnabled : true
  });
  
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'success'
  });

  useEffect(() => {
    // Update local settings when redux state changes
    setLocalSettings({
      cacheSize: settings.cacheSize || 500,
      autoUpdate: settings.autoUpdate !== undefined ? settings.autoUpdate : true,
      debugMode: settings.debugMode || false,
      apiEndpoint: settings.apiEndpoint || 'https://api.example.com',
      dataExportFormat: settings.dataExportFormat || 'json',
      notificationsEnabled: settings.notificationsEnabled !== undefined ? settings.notificationsEnabled : true
    });
  }, [settings]);

  const handleThemeChange = (event) => {
    dispatch(setTheme(event.target.value));
  };

  const handleLanguageChange = (event) => {
    dispatch(setLanguage(event.target.value));
  };

  const handleSettingChange = (key, value) => {
    setLocalSettings({
      ...localSettings,
      [key]: value
    });
  };

  const handleSaveSettings = () => {
    dispatch(updateSettings(localSettings));
    setSnackbar({
      open: true,
      message: t('settings.saveSuccess'),
      severity: 'success'
    });
  };

  const handleResetSettings = () => {
    dispatch(resetSettings());
    setSnackbar({
      open: true,
      message: t('settings.resetSuccess'),
      severity: 'info'
    });
  };

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        {t('settings.title')}
      </Typography>
      
      <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          {t('settings.appearance')}
        </Typography>
        
        <Box sx={{ mb: 3 }}>
          <FormControl component="fieldset">
            <Typography variant="subtitle2" gutterBottom>
              {t('settings.theme')}
            </Typography>
            <RadioGroup
              row
              name="theme"
              value={currentTheme}
              onChange={handleThemeChange}
            >
              <FormControlLabel
                value="light"
                control={<Radio />}
                label={t('settings.lightTheme')}
              />
              <FormControlLabel
                value="dark"
                control={<Radio />}
                label={t('settings.darkTheme')}
              />
              <FormControlLabel
                value="system"
                control={<Radio />}
                label={t('settings.systemTheme')}
              />
            </RadioGroup>
          </FormControl>
        </Box>
        
        <Box sx={{ mb: 3 }}>
          <FormControl fullWidth>
            <InputLabel id="language-select-label">{t('settings.language')}</InputLabel>
            <Select
              labelId="language-select-label"
              id="language-select"
              value={currentLanguage}
              label={t('settings.language')}
              onChange={handleLanguageChange}
            >
              <MenuItem value="en">English</MenuItem>
              <MenuItem value="fr">Français</MenuItem>
              <MenuItem value="de">Deutsch</MenuItem>
              <MenuItem value="es">Español</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </Paper>
      
      <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          {t('settings.application')}
        </Typography>
        
        <Box sx={{ mb: 3 }}>
          <TextField
            fullWidth
            label={t('settings.cacheSize')}
            type="number"
            value={localSettings.cacheSize}
            onChange={(e) => handleSettingChange('cacheSize', parseInt(e.target.value, 10))}
            InputProps={{
              endAdornment: <Typography variant="body2">MB</Typography>,
            }}
            margin="normal"
          />
        </Box>
        
        <Box sx={{ mb: 3 }}>
          <TextField
            fullWidth
            label={t('settings.apiEndpoint')}
            value={localSettings.apiEndpoint}
            onChange={(e) => handleSettingChange('apiEndpoint', e.target.value)}
            margin="normal"
          />
        </Box>
        
        <Box sx={{ mb: 3 }}>
          <FormControl fullWidth margin="normal">
            <InputLabel id="export-format-label">{t('settings.dataExportFormat')}</InputLabel>
            <Select
              labelId="export-format-label"
              id="export-format"
              value={localSettings.dataExportFormat}
              label={t('settings.dataExportFormat')}
              onChange={(e) => handleSettingChange('dataExportFormat', e.target.value)}
            >
              <MenuItem value="json">JSON</MenuItem>
              <MenuItem value="csv">CSV</MenuItem>
              <MenuItem value="xml">XML</MenuItem>
              <MenuItem value="excel">Excel</MenuItem>
            </Select>
          </FormControl>
        </Box>
        
        <Box sx={{ mb: 3 }}>
          <FormControlLabel
            control={
              <Switch
                checked={localSettings.autoUpdate}
                onChange={(e) => handleSettingChange('autoUpdate', e.target.checked)}
              />
            }
            label={t('settings.autoUpdate')}
          />
        </Box>
        
        <Box sx={{ mb: 3 }}>
          <FormControlLabel
            control={
              <Switch
                checked={localSettings.notificationsEnabled}
                onChange={(e) => handleSettingChange('notificationsEnabled', e.target.checked)}
              />
            }
            label={t('settings.enableNotifications')}
          />
        </Box>
        
        <Box sx={{ mb: 3 }}>
          <FormControlLabel
            control={
              <Switch
                checked={localSettings.debugMode}
                onChange={(e) => handleSettingChange('debugMode', e.target.checked)}
              />
            }
            label={t('settings.debugMode')}
          />
        </Box>
      </Paper>
      
      <Divider sx={{ my: 3 }} />
      
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
        <Button
          variant="outlined"
          color="error"
          onClick={handleResetSettings}
        >
          {t('settings.resetToDefault')}
        </Button>
        
        <Button
          variant="contained"
          color="primary"
          onClick={handleSaveSettings}
        >
          {t('settings.saveSettings')}
        </Button>
      </Box>
      
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

export default Settings;