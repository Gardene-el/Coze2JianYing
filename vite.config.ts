import { resolve } from "node:path";
import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import type { ViteDevServer } from "vite";

const mode =
  process.env.NODE_ENV === "production" ? "production" : "development";
const isDev = mode !== "production";

export default defineConfig(({ mode: envMode }) => {
  const env = loadEnv(envMode, process.cwd(), "");
  const apiBase = env.VITE_API_BASE || "http://localhost:20210";

  return {
    // 开发时用 '/'，Electron 生产打包需要相对路径
    base: isDev ? "/" : "./",

    plugins: [
      react(),
      // 将根路径 / 重写到 apps/desktop/index.html，使独立 SPA 开发模式（bun run dev）
      // 和 Electron 开发模式（electron-vite renderer）一致
      isDev && {
        name: "desktop-html-rewrite",
        configureServer(server: ViteDevServer) {
          server.middlewares.use((req, _res, next) => {
            if (req.url === "/" || req.url === "/index.html") {
              req.url = "/apps/desktop/index.html";
            }
            next();
          });
        },
      },
    ],

    resolve: {
      alias: {
        "@": resolve(__dirname, "src/frontend"),
      },
    },

    build: {
      outDir: "dist",
      emptyOutDir: true,
      rollupOptions: {
        input: resolve(__dirname, "apps/desktop/index.html"),
        output: {
          manualChunks: {
            antd: ["antd", "antd-style"],
            react: ["react", "react-dom", "react-router-dom"],
            zustand: ["zustand"],
          },
        },
      },
    },

    server: {
      port: 5173,
      host: true,
      proxy: {
        "/gui": {
          target: apiBase,
          changeOrigin: true,
        },
      },
    },

    optimizeDeps: {
      include: ["antd", "antd-style", "zustand", "axios", "react-router-dom"],
    },
  };
});
