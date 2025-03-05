// src/context/AuthContext.tsx
import React, { createContext, useState, useEffect } from "react";

type AuthContextType = {
  isAdmin: boolean;
  setRole: (role: string) => void;
  logout: () => void;
};

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAdmin, setIsAdmin] = useState<boolean>(false);

  useEffect(() => {
    const role = localStorage.getItem("role");
    setIsAdmin(role === "admin");
  }, []);

  const setRole = (role: string) => {
    localStorage.setItem("role", role);
    setIsAdmin(role === "admin"); // Update state immediately
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("role");
    setIsAdmin(false);
    window.location.href = "/";
  };

  return (
    <AuthContext.Provider value={{ isAdmin, setRole, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
