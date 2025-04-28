import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "path";
import electron from "vite-plugin-electron";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    electron({
      entry: "electron/main.js",
      vite: {
        build: {
          outDir: "dist-electron",
          rollupOptions: {
            external: ["electron", "electron-devtools-installer"],
          },
        },
      },
    }),
  ],
  resolve: {
    alias: {
      "@": resolve(__dirname, "src"),
      "@components": resolve(__dirname, "src/components"),
      "@pages": resolve(__dirname, "src/pages"),
      "@services": resolve(__dirname, "src/services"),
      "@store": resolve(__dirname, "src/redux"),
      "@utils": resolve(__dirname, "src/utils"),
      "@hooks": resolve(__dirname, "src/hooks"),
      "@context": resolve(__dirname, "src/context"),
    },
  },
  build: {
    outDir: "dist",
    assetsDir: "assets",
    emptyOutDir: true,
    sourcemap: process.env.NODE_ENV === "development",
  },
  server: {
    port: 3000,
    strictPort: true,
    host: true,
    proxy: {
      "/api": {
        target: "http://localhost:8668",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
