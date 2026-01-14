require('dotenv').config();
const {app, BrowserWindow} = require('electron');

let win;

// Function to wait for the server to be ready
async function waitForServer(url, maxAttempts = 30, interval = 1000) {
    const http = require('http');

    for (let attempt = 0; attempt < maxAttempts; attempt++) {
        try {
            await new Promise((resolve, reject) => {
                const request = http.get(url, (res) => {
                    resolve(res);
                });
                request.on('error', reject);
                request.setTimeout(1000, () => {
                    request.destroy();
                    reject(new Error('Timeout'));
                });
            });
            console.log('Server is ready!');
            return true;
        } catch (error) {
            console.log(`Waiting for server... attempt ${attempt + 1}/${maxAttempts}`);
            await new Promise(resolve => setTimeout(resolve, interval));
        }
    }
    throw new Error('Server did not start in time');
}

async function createWindow() {
    const url = process.env.URL + ':' + process.env.PORT;

    // Wait for the Python server to be ready
    try {
        await waitForServer(url);
    } catch (error) {
        console.error('Failed to connect to server:', error.message);
        app.quit();
        return;
    }

    // Create the browser window.
    win = new BrowserWindow({
        width: 1350,
        height: 800,
        minHeight: 800,
        minWidth: 1350,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            webSecurity: true,
        }
    });

    // Handle load errors
    win.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
        console.error('Failed to load:', errorDescription);
    });

    win.webContents.on('did-finish-load', () => {
        console.log('Page loaded successfully');
    });

    // and load the index.html of the app.
    win.loadURL(url);
    win.webContents.openDevTools();

    // Emitted when the window is closed.
    win.on('closed', () => {
        win = null;
    });
}

app.on('ready', createWindow);

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        app.quit();
    }
});

app.on('activate', () => {
    if (win === null) {
        createWindow();
    }
});
