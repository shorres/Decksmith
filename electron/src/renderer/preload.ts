import { contextBridge, ipcRenderer } from 'electron';

// Define the API that will be available in the renderer process
const electronAPI = {
  // File operations
  openFileDialog: (options: any) => ipcRenderer.invoke('dialog:openFile', options),
  saveFileDialog: (options: any) => ipcRenderer.invoke('dialog:saveFile', options),

  // Store operations (persistent data storage)
  store: {
    get: (key: string) => ipcRenderer.invoke('store:get', key),
    set: (key: string, value: any) => ipcRenderer.invoke('store:set', key, value),
    delete: (key: string) => ipcRenderer.invoke('store:delete', key),
    clear: () => ipcRenderer.invoke('store:clear'),
  },

  // App info
  getAppVersion: () => ipcRenderer.invoke('app:getVersion'),
  getAppName: () => ipcRenderer.invoke('app:getName'),

  // Menu events (from main process)
  onMenuAction: (callback: (action: string) => void) => {
    const handler = (event: any, action: string) => callback(action);
    ipcRenderer.on('menu:new-collection', handler);
    ipcRenderer.on('menu:import-collection', handler);
    ipcRenderer.on('menu:export-collection', handler);
    ipcRenderer.on('menu:new-deck', handler);
    ipcRenderer.on('menu:import-deck', handler);
    ipcRenderer.on('menu:export-deck', handler);
    ipcRenderer.on('menu:about', handler);
  },

  // Remove listeners
  removeAllListeners: (channel: string) => {
    ipcRenderer.removeAllListeners(channel);
  }
};

// Safely expose the API to the renderer process
contextBridge.exposeInMainWorld('electronAPI', electronAPI);

// Type definitions for TypeScript
declare global {
  interface Window {
    electronAPI: typeof electronAPI;
  }
}
