import { contextBridge, ipcRenderer } from 'electron';

interface FileFilter {
  name: string;
  extensions: string[];
}

// Channels the main process sends when a menu item is clicked
const MENU_CHANNELS = [
  'menu:new-collection',
  'menu:import-collection',
  'menu:export-collection',
  'menu:new-deck',
  'menu:import-deck',
  'menu:export-deck',
  'menu:about',
];

// Define the API that will be available in the renderer process
const electronAPI = {
  // File operations (dialog + read/write happen in the main process)
  saveTextFile: (options: {
    title?: string;
    defaultPath?: string;
    filters?: FileFilter[];
    content: string;
    contentByExtension?: Record<string, string>; // written instead of `content` when the chosen file has that extension
  }):
    Promise<{ canceled: boolean; filePath?: string }> => ipcRenderer.invoke('file:saveText', options),
  openTextFile: (options: { title?: string; filters?: FileFilter[] }):
    Promise<{ canceled: boolean; filePath?: string; content?: string }> => ipcRenderer.invoke('file:openText', options),

  // Store operations (persistent data storage)
  store: {
    get: (key: string) => ipcRenderer.invoke('store:get', key),
    set: (key: string, value: any) => ipcRenderer.invoke('store:set', key, value),
  },

  // App info
  getAppVersion: (): Promise<string> => ipcRenderer.invoke('app:getVersion'),

  // Shell operations
  shell: {
    openExternal: (url: string) => ipcRenderer.invoke('shell:openExternal', url),
  },

  // Menu events (from main process) - the callback receives the channel name
  onMenuAction: (callback: (action: string) => void) => {
    MENU_CHANNELS.forEach(channel => {
      ipcRenderer.on(channel, () => callback(channel));
    });
  },
};

// Safely expose the API to the renderer process
contextBridge.exposeInMainWorld('electronAPI', electronAPI);

// Type definitions for TypeScript
declare global {
  interface Window {
    electronAPI: typeof electronAPI;
  }
}
