/**
 * Axios instance pre-configured with the base URL.
 * Attaches the Supabase JWT token to every request automatically.
 *
 * Usage:
 *   import api from "../lib/api";
 *   const res = await api.get("/score");
 *   const res = await api.post("/analyze", { code, language, problem_name });
 */

import axios from "axios";
import { supabase } from "./supabaseClient";

const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";

const api = axios.create({ baseURL: BASE_URL });

// Attach the current Supabase JWT before each request
api.interceptors.request.use(async (config) => {
  const { data: { session } } = await supabase.auth.getSession();
  if (session?.access_token) {
    config.headers["Authorization"] = `Bearer ${session.access_token}`;
  }
  return config;
});

export default api;
