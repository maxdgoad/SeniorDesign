const { app, BrowserWindow } = require('electron');
let { PythonShell } = require('python-shell');
let process = require('child_process')

app.commandLine.appendSwitch("disable-http-cache"); // disables cache

// runs backend/Server.py in the background
function startPythonPersistent() {
	console.log("python start")
	var python = require('child_process').spawn('python', ['backend/Server.py']);
	python.stdout.on('data', function (data) {
		console.log("Python response: ", data.toString('utf8'));

	});

	python.on('message', function (data) {
		console.log(data)
	});

	python.stderr.on('data', (data) => {
		console.log("Python response: ", data.toString('utf8'));
	});

	python.on('close', (code) => {
		console.log(`child process exited with code ${code}`);
	});

}

// electron init stuff
function createWindow() {
	// Create the browser window.
	const win = new BrowserWindow({
		width: 1280,
		height: 800,
		//fullscreen: true, //uncomment in the final code
		webPreferences: {
			nodeIntegration: true
		}
	})
	//win.removeMenu() //uncomment in the final code
	win.loadFile('index.html')
}

app.whenReady().then(createWindow)

app.on('window-all-closed', () => {
	if (process.platform !== 'darwin') {
		app.quit()
	}
})

app.on('activate', () => {
	if (BrowserWindow.getAllWindows().length === 0) {
		createWindow()
	}
})

startPythonPersistent()

