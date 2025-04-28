const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const isDev = require('electron-is-dev');
const { autoUpdater } = require('electron-updater');
const log = require('electron-log');

// Configuration des logs
log.transports.file.level = 'info';
autoUpdater.logger = log;

// Conserver une référence globale de l'objet window, sinon la fenêtre 
// sera fermée automatiquement quand l'objet JavaScript sera garbage collected.
let mainWindow;

function createWindow() {
  // Créer la fenêtre du navigateur.
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    icon: path.join(__dirname, 'icons/icon.png'),
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false,
      enableRemoteModule: true,
      preload: path.join(__dirname, 'preload.js')
    }
  });

  // Charger l'application React.
  mainWindow.loadURL(
    isDev
      ? 'http://localhost:3000'
      : `file://${path.join(__dirname, '../build/index.html')}`
  );

  // Ouvrir les DevTools en mode développement.
  if (isDev) {
    mainWindow.webContents.openDevTools({ mode: 'detach' });
  }

  // Émis lorsque la fenêtre est fermée.
  mainWindow.on('closed', () => {
    // Déréférencer l'objet window pour permettre le garbage collection
    mainWindow = null;
  });

  // Configurer l'auto-updater
  if (!isDev) {
    autoUpdater.checkForUpdatesAndNotify();
  }
}

// Cette méthode sera appelée quand Electron a fini de s'initialiser
// et est prêt à créer des fenêtres de navigateur.
// Certaines APIs peuvent être utilisées uniquement après cet événement.
app.whenReady().then(() => {
  createWindow();
  
  app.on('activate', () => {
    // Sur macOS, il est courant de recréer une fenêtre de l'application lorsque
    // l'icône du dock est cliquée et qu'il n'y a pas d'autres fenêtres ouvertes.
    if (mainWindow === null) createWindow();
  });
});

// Quitter quand toutes les fenêtres sont fermées, sauf sur macOS.
app.on('window-all-closed', () => {
  // Sous macOS, il est courant pour les applications et leur barre de menu
  // de rester actives jusqu'à ce que l'utilisateur quitte explicitement avec Cmd + Q
  if (process.platform !== 'darwin') app.quit();
});

// Gestion des mises à jour
autoUpdater.on('update-available', () => {
  if (mainWindow) {
    mainWindow.webContents.send('update-available');
  }
});

autoUpdater.on('update-downloaded', () => {
  if (mainWindow) {
    mainWindow.webContents.send('update-downloaded');
  }
});

// IPC handlers
ipcMain.handle('install-update', () => {
  autoUpdater.quitAndInstall();
});

ipcMain.handle('open-file-dialog', async (event, options) => {
  const { filePaths } = await dialog.showOpenDialog(options);
  return filePaths;
});

ipcMain.handle('save-file-dialog', async (event, options) => {
  const { filePath } = await dialog.showSaveDialog(options);
  return filePath;
});

// Gestion des erreurs non interceptées
process.on('uncaughtException', (error) => {
  log.error('Uncaught Exception:', error);
  
  if (mainWindow) {
    mainWindow.webContents.send('uncaught-exception', error.message);
  }
});