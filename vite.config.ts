import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import fs from 'fs';
import path from 'path';

const safePublicDir = path.resolve(__dirname, 'public_safe');

function buildSafePublicDir() {
  if (!fs.existsSync(safePublicDir)) {
    fs.mkdirSync(safePublicDir, { recursive: true });
  }
  const publicDir = path.resolve(__dirname, 'public');
  if (!fs.existsSync(publicDir)) return;
  const files = fs.readdirSync(publicDir);
  files.forEach(file => {
    const src = path.join(publicDir, file);
    const dest = path.join(safePublicDir, file);
    try {
      fs.accessSync(src, fs.constants.R_OK);
      fs.copyFileSync(src, dest);
    } catch {
      /* skip unreadable files */
    }
  });
}

buildSafePublicDir();

export default defineConfig({
  publicDir: safePublicDir,
  plugins: [react()],
  optimizeDeps: {
    exclude: ['lucide-react'],
  },
});
