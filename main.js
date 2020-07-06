const { app, BrowserWindow, Menu } = require('electron')
require('electron-reload')(__dirname);

let mainWindow;

app.on('ready', function(){
    mainWindow = new BrowserWindow({
        webPreferences:{nodeIntegration: true},
        backgroundColor: '#2d5ba8'
    });
    mainWindow.loadFile('src/index.html');
    mainWindow.on('closed', function(){
        app.quit();
    })

    addDevTools();
    Menu.setApplicationMenu(Menu.buildFromTemplate(menuTemplate));
})


const menuTemplate = [
    {
        label:'Menu',
        submenu: [
            //{ type: 'seperator' },
            {
                label: 'Quit',
                click(){
                    app.quit();
                },
                accelerator: process.platform == 'darwin' ? 'Command+Q' : 'Ctrl+Q'
            }
        ]
    }
];

function addDevTools(){
    menuTemplate.push({
        label: 'Tools',
        submenu: [
            {
                label: 'Dev Tools',
                accelerator: process.platform == 'darwin' ? 'Command+I' : 'Ctrl+I',
                click(item, focusedWindow){
                    focusedWindow.toggleDevTools();
                }
            },
            {
                role: 'reload'
            }
        ]
    });
}
