import axios from "axios";

/**
 * Axios 基础实例
 * base URL 由 VITE_API_BASE 环境变量控制，默认 localhost:20210
 * 开发时 vite proxy 会把 /gui 代理到该地址，生产时直接请求
 */
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE ?? "http://localhost:20210",
  timeout: 30_000,
  headers: { "Content-Type": "application/json" },
});

// 统一错误处理
apiClient.interceptors.response.use(
  (res) => res,
  (err) => {
    const msg: string =
      err?.response?.data?.detail ??
      err?.response?.data?.message ??
      err?.message ??
      "请求失败";
    return Promise.reject(new Error(msg));
  },
);

export default apiClient;
