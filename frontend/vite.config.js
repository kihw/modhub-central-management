import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { resolve } from "path";
import electron from "vite-plugin-electron";

export default defineConfig({
  plugins: [
    react(),
    electron({
      entry: "electron/main.js",
      vite: {
        build: {
          outDir: "dist-electron",
          rollupOptions: {
            external: ["electron", "electron-devtools-installer", "path", "fs", "os"],
          },
        },
      },
    }),
  ],
  resolve: {
    alias: {
      "@": resolve(__dirname, "./src"),
      "@components": resolve(__dirname, "./src/components"),
      "@pages": resolve(__dirname, "./src/pages"),
      "@services": resolve(__dirname, "./src/services"),
      "@store": resolve(__dirname, "./src/redux"),
      "@utils": resolve(__dirname, "./src/utils"),
      "@hooks": resolve(__dirname, "./src/hooks"),
      "@context": resolve(__dirname, "./src/context"),
      "@assets": resolve(__dirname, "./src/assets"),
    },
  },
  build: {
    outDir: "dist",
    assetsDir: "assets",
    emptyOutDir: true,
    sourcemap: process.env.NODE_ENV === "development",
    rollupOptions: {
      input: {
        main: resolve(__dirname, "index.html"),
      },
      output: {
        manualChunks: (id) => {
          if (id.includes("node_modules")) {
            if (id.includes("react")) return "vendor-react";
            return "vendor";
          }
          if (id.includes("@utils")) return "utils";
          if (id.includes("@components")) return "components";
        },
        entryFileNames: "js/[name].[hash].js",
        chunkFileNames: "js/[name].[hash].js",
        assetFileNames: "assets/[name].[hash].[ext]",
      },
    },
    target: ["esnext", "chrome100"],
    minify: "esbuild",
    cssMinify: true,
    modulePreload: {
      polyfill: true,
    },
  },
  server: {
    port: 3000,
    strictPort: true,
    host: true,
    proxy: {
      "/api": {
        target: "http://localhost:8668",
        changeOrigin: true,
        secure: false,
        rewrite: (path) => path.replace(/^\/api/, ""),
        ws: true,
        timeout: 60000,
      },
    },
    cors: true,
    watch: {
      usePolling: true,
      interval: 1000,
    },
  },
  optimizeDeps: {
    include: ["react", "react-dom", "react-router-dom"],
    exclude: ["electron"],
  },
  esbuild: {
    jsxInject: `import React from 'react'`,
    target: "esnext",
    legalComments: "none",
  },
});