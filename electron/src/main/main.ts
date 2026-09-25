import { app, BrowserWindow, Menu, ipcMain, dialog, shell } from 'electron';
import * as path from 'path';
import { promises as fs } from 'fs';
import Store from 'electron-store';

// Initialize electron store for persistent data
const store = new Store();

class DecksmithApp {
  private mainWindow: BrowserWindow | null = null;
  private isDev = process.env.NODE_ENV === 'development';

  constructor() {
    this.setupApp();
  }

  private setupApp(): void {
    // Handle app ready
    app.whenReady().then(() => {
      this.createWindow();
      this.setupMenu();
      this.setupIpcHandlers();
    });

    // Handle window closed
    app.on('window-all-closed', () => {
      if (process.platform !== 'darwin') {
        app.quit();
      }
    });

    // Handle app activate (macOS)
    app.on('activate', () => {
      if (BrowserWindow.getAllWindows().length === 0) {
        this.createWindow();
      }
    });
  }

  private createWindow(): void {
    // Create the browser window
    this.mainWindow = new BrowserWindow({
      width: 1400,
      height: 900,
      minWidth: 1000,
      minHeight: 700,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        preload: path.join(__dirname, '../renderer/preload.js'),
      },
      titleBarStyle: 'default',
      icon: path.join(__dirname, '../../assets/decksmith_icon.ico'),
      show: false, // Don't show until ready
    });

    // Load the app
    if (this.isDev) {
      this.mainWindow.loadURL('http://localhost:8080');
      this.mainWindow.webContents.openDevTools();
    } else {
      this.mainWindow.loadFile(path.join(__dirname, '../renderer/index.html'));
    }

    // Show when ready to prevent visual flash
    this.mainWindow.once('ready-to-show', () => {
      this.mainWindow?.show();
      
      // Focus on Windows/Linux
      if (process.platform === 'win32' || process.platform === 'linux') {
        this.mainWindow?.focus();
      }
    });

    // Handle window closed
    this.mainWindow.on('closed', () => {
      this.mainWindow = null;
    });

    // Handle external links
    this.mainWindow.webContents.setWindowOpenHandler(({ url }) => {
      shell.openExternal(url);
      return { action: 'deny' };
    });
  }

  private setupMenu(): void {
    const template = [
      {
        label: 'File',
        submenu: [
          {
            label: 'New Collection',
            accelerator: 'CmdOrCtrl+N',
            click: () => this.sendToRenderer('menu:new-collection')
          },
          {
            label: 'Import Collection',
            accelerator: 'CmdOrCtrl+I',
            click: () => this.sendToRenderer('menu:import-collection')
          },
          {
            label: 'Export Collection',
            accelerator: 'CmdOrCtrl+E',
            click: () => this.sendToRenderer('menu:export-collection')
          },
          { type: 'separator' },
          {
            label: 'Quit',
            accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
            click: () => app.quit()
          }
        ]
      },
      {
        label: 'Deck',
        submenu: [
          {
            label: 'New Deck',
            accelerator: 'CmdOrCtrl+Shift+N',
            click: () => this.sendToRenderer('menu:new-deck')
          },
          {
            label: 'Import Deck',
            accelerator: 'CmdOrCtrl+Shift+I',
            click: () => this.sendToRenderer('menu:import-deck')
          },
          {
            label: 'Export Deck',
            accelerator: 'CmdOrCtrl+Shift+E',
            click: () => this.sendToRenderer('menu:export-deck')
          }
        ]
      },
      {
        label: 'View',
        submenu: [
          {
            label: 'Reload',
            accelerator: 'CmdOrCtrl+R',
            click: () => this.mainWindow?.reload()
          },
          {
            label: 'Force Reload',
            accelerator: 'CmdOrCtrl+Shift+R',
            click: () => this.mainWindow?.webContents.reloadIgnoringCache()
          },
          {
            label: 'Toggle Developer Tools',
            accelerator: process.platform === 'darwin' ? 'Alt+Cmd+I' : 'Ctrl+Shift+I',
            click: () => this.mainWindow?.webContents.toggleDevTools()
          },
          { type: 'separator' },
          {
            label: 'Actual Size',
            accelerator: 'CmdOrCtrl+0',
            click: () => this.mainWindow?.webContents.setZoomLevel(0)
          },
          {
            label: 'Zoom In',
            accelerator: 'CmdOrCtrl+Plus',
            click: () => {
              const currentZoom = this.mainWindow?.webContents.getZoomLevel() || 0;
              this.mainWindow?.webContents.setZoomLevel(currentZoom + 1);
            }
          },
          {
            label: 'Zoom Out',
            accelerator: 'CmdOrCtrl+-',
            click: () => {
              const currentZoom = this.mainWindow?.webContents.getZoomLevel() || 0;
              this.mainWindow?.webContents.setZoomLevel(currentZoom - 1);
            }
          }
        ]
      },
      {
        label: 'Help',
        submenu: [
          {
            label: 'About Decksmith',
            click: () => this.sendToRenderer('menu:about')
          },
          {
            label: 'GitHub Repository',
            click: () => shell.openExternal('https://github.com/shorres/Magic-Tool')
          }
        ]
      }
    ];

    const menu = Menu.buildFromTemplate(template as any);
    Menu.setApplicationMenu(menu);
  }

  private setupIpcHandlers(): void {
    // File operations - the dialog and the read/write both happen here, so the
    // renderer can only touch files the user explicitly picked.
    // `contentByExtension` lets the renderer offer several formats (e.g. { csv: '...' });
    // the one matching the chosen file's extension is written, falling back to `content`.
    ipcMain.handle('file:saveText', async (event, options: {
      title?: string;
      defaultPath?: string;
      filters?: Electron.FileFilter[];
      content: string;
      contentByExtension?: Record<string, string>;
    }) => {
      const { content, contentByExtension, ...dialogOptions } = options;
      const result = await dialog.showSaveDialog(this.mainWindow!, dialogOptions);
      if (result.canceled || !result.filePath) {
        return { canceled: true };
      }
      const extension = path.extname(result.filePath).slice(1).toLowerCase();
      await fs.writeFile(result.filePath, contentByExtension?.[extension] ?? content, 'utf8');
      return { canceled: false, filePath: result.filePath };
    });

    ipcMain.handle('file:openText', async (event, options: { title?: string; filters?: Electron.FileFilter[] }) => {
      const result = await dialog.showOpenDialog(this.mainWindow!, { ...options, properties: ['openFile'] });
      if (result.canceled || result.filePaths.length === 0) {
        return { canceled: true };
      }
      const filePath = result.filePaths[0];
      const content = await fs.readFile(filePath, 'utf8');
      return { canceled: false, filePath, content };
    });

    // Store operations
    ipcMain.handle('store:get', (event, key) => {
      return store.get(key);
    });

    ipcMain.handle('store:set', (event, key, value) => {
      store.set(key, value);
      return true;
    });

    // App info
    ipcMain.handle('app:getVersion', () => {
      return app.getVersion();
    });

    // Shell operations
    ipcMain.handle('shell:openExternal', async (event, url) => {
      await shell.openExternal(url);
    });
  }

  private sendToRenderer(channel: string, ...args: any[]): void {
    this.mainWindow?.webContents.send(channel, ...args);
  }
}

// Create the app instance
new DecksmithApp();
