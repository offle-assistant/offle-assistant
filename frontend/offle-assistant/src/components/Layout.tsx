// src/components/Layout.tsx
import React from "react";
import { Outlet } from "react-router-dom";
import Navbar from "./Navbar";
import { Box, Container } from "@mui/material";

const Layout: React.FC = () => {

  return (
    <Box>
      {/* Navbar at the Top */}
      <Navbar />

      {/* Main Content (Outlet for Nested Routes) */}
      <Box component="main" sx={{ mt: 8, p: 3 }}>
        <Container maxWidth="lg">
          <Outlet />
        </Container>
      </Box>
    </Box>
  );
};

export default Layout;
