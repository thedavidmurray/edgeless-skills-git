```json
{
  "name": "my-command-center",
  "version": "1.0.0",
  "description": "Native desktop data dashboard",
  "main": "main.js",
  "scripts": {
    "start": "electron .",
    "build:mac": "electron-builder --mac",
    "build:win": "electron-builder --win",
    "build:linux": "electron-builder --linux",
    "build:all": "electron-builder --mac --win --linux"
  },
  "build": {
    "appId": "com.example.command-center",
    "productName": "My Command Center",
    "directories": { "output": "dist", "buildResources": "assets" },
    "files": [
      "main.js",
      "preload.js",
      "index.html",
      "themes.css",
      "theme-builder.html",
      "assets/**/*"
    ],
    "mac": {
      "target": [
        { "target": "dmg", "arch": ["arm64", "x64"] },
        { "target": "zip", "arch": ["arm64", "x64"] }
      ],
      "category": "public.app-category.utilities",
      "icon": "assets/icon.png"
    },
    "win": {
      "target": [
        { "target": "nsis", "arch": ["x64"] },
        { "target": "portable", "arch": ["x64"] }
      ],
      "icon": "assets/icon.png"
    },
    "linux": {
      "target": [
        { "target": "AppImage", "arch": ["x64"] },
        { "target": "deb", "arch": ["x64"] }
      ],
      "icon": "assets/icon.png"
    },
    "dmg": {
      "title": "My Command Center",
      "contents": [
        { "x": 130, "y": 220, "type": "file" },
        { "x": 410, "y": 220, "type": "link", "path": "/Applications" }
      ],
      "window": { "width": 540, "height": 380 }
    }
  },
  "devDependencies": {
    "electron": "^33.0.0",
    "electron-builder": "^25.0.0"
  }
}
```
