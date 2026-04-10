const fs = require("fs");

const appPath = "apps/app.py";
const now = new Date();

fs.utimesSync(appPath, now, now);
console.log(`Locale changed. Touched ${appPath} to trigger Python reload.`);
