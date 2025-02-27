// src/components/Navbar.tsx
import React, { useState, useContext } from "react";
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Menu,
  MenuItem,
  Box,
} from "@mui/material";
import MenuIcon from "@mui/icons-material/Menu";
import { Link } from "react-router-dom";
import { AuthContext } from "../context/AuthContext"; // Import Auth Context

const Navbar: React.FC = () => {
  const { isAdmin, logout } = useContext(AuthContext) || { isAdmin: false, logout: () => {} };
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleMenuOpen = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  return (
    <AppBar
      position="fixed"
      sx={{
        background: "linear-gradient(to right, #667eea, #764ba2)", // Matches theme
        padding: "8px 16px",
      }}
    >
      <Toolbar>
        {/* Mobile Menu Button */}
        <IconButton
          edge="start"
          color="inherit"
          aria-label="menu"
          sx={{ display: { md: "none" } }}
          onClick={handleMenuOpen}
        >
          <MenuIcon />
        </IconButton>

        {/* App Title */}
        <Typography
          variant="h6"
          sx={{ flexGrow: 1, fontWeight: "bold", letterSpacing: 1 }}
        >
          Offle Assistant
        </Typography>

        {/* Desktop Navigation Buttons */}
        <Box sx={{ display: { xs: "none", md: "block" } }}>
          {isAdmin && (
            <Button color="inherit" component={Link} to="/admin">
              Admin
            </Button>
          )}
          <Button color="inherit" component={Link} to="/personas">
            Personas
          </Button>
          <Button color="inherit" component={Link} to="/chat">
            Chat
          </Button>
          <Button color="inherit" onClick={logout}>
            Logout
          </Button>
        </Box>

        {/* Mobile Menu */}
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
          sx={{ display: { md: "none" } }}
        >
          {isAdmin && (
            <MenuItem component={Link} to="/admin" onClick={handleMenuClose}>
              Admin
            </MenuItem>
          )}
          <MenuItem component={Link} to="/personas" onClick={handleMenuClose}>
            Personas
          </MenuItem>
          <MenuItem component={Link} to="/chat" onClick={handleMenuClose}>
            Chat
          </MenuItem>
          <MenuItem
            onClick={() => {
              handleMenuClose();
              logout();
            }}
          >
            Logout
          </MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
