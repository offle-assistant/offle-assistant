import axios from "axios";
import { getToken, logout } from "./auth"; //Handles 401 Unauthorized errors

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const api = axios.create({
    baseURL: API_BASE_URL,
    withCredentials: true,
    headers: { "Content-Type": "application/json" }
});

export const setAuthToken = (token: string | null) => {
    if (token) {
        localStorage.setItem("token", token); 
        api.defaults.headers.common["Authorization"] = `Bearer ${token}`;
    } else {
        localStorage.removeItem("token"); 
        delete api.defaults.headers.common["Authorization"];
    }
};

//Attach token automatically if it exists on refresh
const token = getToken();
if (token) {
    setAuthToken(token);
}

//Automatically log out on 401 Unauthorized
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            console.warn("⚠️ Unauthorized! Logging out...");
            logout(); 
        }
        return Promise.reject(error);
    }
);
