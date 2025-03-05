// src/components/AuthForm.tsx
import React, { useState, useContext } from "react";
import { Button, TextField, Box } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { api, setAuthToken } from "../utils/api";
import {jwtDecode} from "jwt-decode";
import { AuthContext } from "../context/AuthContext"; // Import Auth Context

type AuthFormProps = {
  type: "login" | "register";
};

const AuthForm: React.FC<AuthFormProps> = ({ type }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();
  const authContext = useContext(AuthContext); // Access Auth Context

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await api.post(type === "login" ? "/auth/login" : "/auth/register", { email, password });
      const token = res.data.access_token;

      localStorage.setItem("token", token);
      setAuthToken(token);

      // Decode token and update role in Auth Context
      const decoded = jwtDecode<{ role: string }>(token);
      authContext?.setRole(decoded.role); // Updates role and forces navbar update

      navigate("/personas");
    } catch (err) {
      // ✅ Fix: Log error for debugging & handle axios errors properly
      console.error("Authentication error:", err);
    }
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
      <TextField label="Email" type="email" variant="outlined" value={email} onChange={(e) => setEmail(e.target.value)} required fullWidth />
      <TextField label="Password" type="password" variant="outlined" value={password} onChange={(e) => setPassword(e.target.value)} required fullWidth />
      <Button type="submit" variant="contained" color="primary" sx={{ borderRadius: 3, fontSize: "1rem", p: 1 }}>
        {type === "login" ? "Login" : "Register"}
      </Button>
    </Box>
  );
};

export default AuthForm;
