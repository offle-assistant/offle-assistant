// src/pages/Login.tsx
import React from "react";
import AuthForm from "../components/AuthForm";
import { Box, Typography, Paper, Button } from "@mui/material";
import { Link } from "react-router-dom";

const Login: React.FC = () => {
  return (
    <Box
      sx={{
        height: "100vh",
        width: "100vw",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        background: "linear-gradient(to right, #667eea, #764ba2)", // Smooth gradient
      }}
    >
      <Paper
        elevation={4}
        sx={{
          p: 4,
          borderRadius: 3,
          width: "400px",
          textAlign: "center",
          backgroundColor: "white",
        }}
      >
        <Typography variant="h4" sx={{ mb: 2, fontWeight: "bold", color: "#333" }}>
          Assistant Login
        </Typography>
        <AuthForm type="login" />
        
        {/* Register Button */}
        <Typography sx={{ mt: 2 }}>Don't have an account?</Typography>
        <Button
          component={Link}
          to="/register"
          variant="outlined"
          color="primary"
          sx={{ mt: 1, width: "100%" }}
        >
          Register
        </Button>
      </Paper>
    </Box>
  );
};

export default Login;
