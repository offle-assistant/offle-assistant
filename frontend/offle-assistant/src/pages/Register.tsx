// src/pages/Register.tsx
import React from "react";
import AuthForm from "../components/AuthForm";
import { Box, Typography, Paper, Button } from "@mui/material";
import { Link } from "react-router-dom";

const Register: React.FC = () => {
  return (
    <Box
      sx={{
        height: "100vh",
        width: "100vw",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        background: "linear-gradient(to right, #667eea, #764ba2)", // Match Login Page
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
          Assistant Register
        </Typography>
        <AuthForm type="register" />

        {/* Login Button */}
        <Typography sx={{ mt: 2 }}>Already have an account?</Typography>
        <Button
          component={Link}
          to="/"
          variant="outlined"
          color="primary"
          sx={{ mt: 1, width: "100%" }}
        >
          Login
        </Button>
      </Paper>
    </Box>
  );
};

export default Register;
