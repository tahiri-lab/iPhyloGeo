const {app, BrowserWindow} = require('electron');
const dash = require('dash');

let win;

function createWindow() {
    // Create the browser window.
    win = new BrowserWindow({
        width: 1350,
        height: 800,
        minHeight: 800,
        minWidth: 1350,
    });

    // and load the index.html of the app.
    win.loadURL(`http://localhost:8050`);
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
