const { app, BrowserWindow, ipcMain, Tray, Menu, shell, dialog } = require('electron');
const path = require('path');
const isDev = require('electron-is-dev');
const { spawn } = require('child_process');
const axios = require('axios');
const fs = require('fs');
const log = require('electron-log');

// Configure logging
log.transports.file.level = 'info';
log.transports.console.level = 'debug';

// Global references
let mainWindow;
let tray;
let backendProcess;
let apiBaseUrl = 'http://localhost:8000';
let isBackendReady = false;
let isQuitting = false;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    icon: path.join(__dirname, '../assets/icons/icon.png'),
    frame: false,
    show: false, // Hide until ready-to-show
    backgroundColor: '#1a1a1a'
  });

  // Load the app
  const startURL = isDev
    ? 'http://localhost:3000'
    : `file://${path.join(__dirname, '../build/index.html')}`;

  mainWindow.loadURL(startURL);

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // Handle window closing
  mainWindow.on('close', (event) => {
    if (!isQuitting) {
      event.preventDefault();
      mainWindow.hide();
      return false;
    }
    return true;
  });

  // Handle window closed
  mainWindow.on('closed', () => {
    mainWindow = null;
  });

  // Create tray
  createTray();
}

function createTray() {
  tray = new Tray(path.join(__dirname, '../assets/icons/tray-icon.png'));
  const contextMenu = Menu.buildFromTemplate([
    { label: 'Open ModHub', click: () => mainWindow.show() },
    { type: 'separator' },
    { 
      label: 'Gaming Mode', 
      type: 'checkbox',
      checked: false,
      click: (menuItem) => toggleMod('gaming', menuItem.checked)
    },
    { 
      label: 'Night Mode', 
      type: 'checkbox',
      checked: false,
      click: (menuItem) => toggleMod('night', menuItem.checked)
    },
    { 
      label: 'Media Mode', 
      type: 'checkbox',
      checked: false,
      click: (menuItem) => toggleMod('media', menuItem.checked)
    },
    { type: 'separator' },
    { label: 'Settings', click: () => {
        mainWindow.show();
        mainWindow.webContents.send('navigate', '/settings');
    }},
    { type: 'separator' },
    { label: 'Quit', click: () => {
        isQuitting = true;
        app.quit();
    }}
  ]);

  tray.setToolTip('ModHub Central');
  tray.setContextMenu(contextMenu);
  
  tray.on('click', () => {
    mainWindow.isVisible() ? mainWindow.hide() : mainWindow.show();
  });
}

async function startBackend() {
  try {
    // Path to Python executable and backend script
    let pythonExecutable = isDev ? 'python' : path.join(process.resourcesPath, 'app', 'backend', 'venv', 'bin', 'python');
    if (process.platform === 'win32') {
      pythonExecutable = isDev ? 'python' : path.join(process.resourcesPath, 'app', 'backend', 'venv', 'Scripts', 'python.exe');
    }
    
    const backendScript = isDev 
      ? path.join(__dirname, '../../backend/main.py')
      : path.join(process.resourcesPath, 'app', 'backend', 'main.py');
    
    log.info(`Starting backend: ${pythonExecutable} ${backendScript}`);

    // Start the backend process
    backendProcess = spawn(pythonExecutable, [backendScript]);
    
    backendProcess.stdout.on('data', (data) => {
      log.info(`Backend stdout: ${data}`);
      if (data.toString().includes('Application startup complete')) {
        isBackendReady = true;
        log.info('Backend is ready');
        mainWindow.webContents.send('backend-status', { status: 'connected' });
      }
    });
    
    backendProcess.stderr.on('data', (data) => {
      log.error(`Backend stderr: ${data}`);
    });
    
    backendProcess.on('close', (code) => {
      log.info(`Backend process exited with code ${code}`);
      isBackendReady = false;
      if (!isQuitting) {
        dialog.showErrorBox(
          'Backend Error',
          `The backend process has unexpectedly terminated with code ${code}. The application may not function correctly.`
        );
        mainWindow.webContents.send('backend-status', { status: 'disconnected' });
      }
    });

    // Wait for backend to be ready
    await waitForBackend();
  } catch (error) {
    log.error('Failed to start backend:', error);
    dialog.showErrorBox(
      'Backend Error',
      `Failed to start the backend process: ${error.message}`
    );
  }
}

async function waitForBackend() {
  let attempts = 0;
  const maxAttempts = 30; // 30 seconds timeout
  
  while (attempts < maxAttempts) {
    try {
      const response = await axios.get(`${apiBaseUrl}/health`);
      if (response.status === 200) {
        log.info('Backend health check successful');
        isBackendReady = true;
        mainWindow.webContents.send('backend-status', { status: 'connected' });
        return;
      }
    } catch (error) {
      // Ignore error and try again
    }
    
    attempts++;
    await new Promise(resolve => setTimeout(resolve, 1000));
  }
  
  log.error('Backend health check failed after maximum attempts');
  dialog.showErrorBox(
    'Connection Error',
    'Failed to connect to the backend service. The application may not function correctly.'
  );
}

async function toggleMod(modType, enabled) {
  try {
    if (!isBackendReady) {
      throw new Error('Backend is not ready');
    }
    
    const response = await axios.post(`${apiBaseUrl}/mods/${modType}`, { 
      enabled: enabled 
    });
    
    log.info(`Toggled ${modType} mode: ${enabled}`);
    mainWindow.webContents.send('mod-update', { type: modType, enabled: enabled });
    
    return response.data;
  } catch (error) {
    log.error(`Error toggling ${modType} mode:`, error);
    dialog.showErrorBox(
      'Error',
      `Failed to toggle ${modType} mode: ${error.message}`
    );
  }
}

// IPC Handlers
function setupIPC() {
  // Window controls
  ipcMain.on('minimize-window', () => {
    mainWindow.minimize();
  });
  
  ipcMain.on('maximize-window', () => {
    if (mainWindow.isMaximized()) {
      mainWindow.unmaximize();
    } else {
      mainWindow.maximize();
    }
  });
  
  ipcMain.on('close-window', () => {
    mainWindow.hide();
  });

  // Toggle mods from renderer
  ipcMain.handle('toggle-mod', async (event, { modType, enabled }) => {
    return await toggleMod(modType, enabled);
  });

  // Get app info
  ipcMain.handle('get-app-info', () => {
    return {
      version: app.getVersion(),
      appPath: app.getAppPath(),
      isDev: isDev
    };
  });

  // Open external links
  ipcMain.on('open-external-link', (event, url) => {
    shell.openExternal(url);
  });

  // Backend API proxy
  ipcMain.handle('api-request', async (event, { method, endpoint, data }) => {
    try {
      if (!isBackendReady) {
        throw new Error('Backend is not ready');
      }
      
      const url = `${apiBaseUrl}${endpoint}`;
      let response;
      
      switch (method.toLowerCase()) {
        case 'get':
          response = await axios.get(url, { params: data });
          break;
        case 'post':
          response = await axios.post(url, data);
          break;
        case 'put':
          response = await axios.put(url, data);
          break;
        case 'delete':
          response = await axios.delete(url, { data });
          break;
        default:
          throw new Error(`Unsupported method: ${method}`);
      }
      
      return response.data;
    } catch (error) {
      log.error('API request error:', error);
      throw error;
    }
  });
}

// App lifecycle events
app.on('ready', async () => {
  log.info('App is ready');
  
  createWindow();
  setupIPC();
  await startBackend();
  
  // Check for updates if not in dev mode
  if (!isDev) {
    // Add update checking code here
  }
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  } else {
    mainWindow.show();
  }
});

app.on('before-quit', () => {
  log.info('Application is quitting');
  isQuitting = true;
  
  // Terminate backend process
  if (backendProcess) {
    log.info('Killing backend process');
    backendProcess.kill();
  }
});

// Auto-launch setup (can be toggled in settings)
// const AutoLaunch = require('auto-launch');
// const autoLauncher = new AutoLaunch({
//   name: 'ModHub Central',
//   path: app.getPath('exe'),
// });
// 
// ipcMain.handle('get-auto-launch', async () => {
//   return await autoLauncher.isEnabled();
// });
// 
// ipcMain.handle('set-auto-launch', async (event, enable) => {
//   try {
//     if (enable) {
//       await autoLauncher.enable();
//     } else {
//       await autoLauncher.disable();
//     }
//     return await autoLauncher.isEnabled();
//   } catch (error) {
//     log.error('Auto-launch error:', error);
//     return false;
//   }
// });