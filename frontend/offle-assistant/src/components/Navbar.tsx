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
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";
import { Link } from "react-router-dom";
import { AuthContext } from "../context/AuthContext"; // Import Auth Context

const Navbar: React.FC = () => {
  const { isAdmin, logout } = useContext(AuthContext) || { isAdmin: false, logout: () => {} };

  const [mobileMenuEl, setMobileMenuEl] = useState<null | HTMLElement>(null);
  const [adminMenuEl, setAdminMenuEl] = useState<null | HTMLElement>(null);

  const handleMobileMenuOpen = (event: React.MouseEvent<HTMLButtonElement>) => {
    setMobileMenuEl(event.currentTarget);
  };

  const handleMobileMenuClose = () => {
    setMobileMenuEl(null);
  };

  const handleAdminMenuOpen = (event: React.MouseEvent<HTMLButtonElement>) => {
    setAdminMenuEl(event.currentTarget);
  };

  const handleAdminMenuClose = () => {
    setAdminMenuEl(null);
  };

  return (
    <AppBar position="fixed" sx={{ background: "linear-gradient(to right, #667eea, #764ba2)", padding: "8px 16px" }}>
      <Toolbar>
        {/* Mobile Menu Button */}
        <IconButton
          edge="start"
          color="inherit"
          aria-label="menu"
          sx={{ display: { md: "none" } }}
          onClick={handleMobileMenuOpen}
        >
          <MenuIcon />
        </IconButton>

        {/* App Title */}
        <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: "bold", letterSpacing: 1 }}>
          Offle Assistant
        </Typography>

        {/* Desktop Navigation */}
        <Box sx={{ display: { xs: "none", md: "flex" }, gap: 2 }}>
          {isAdmin && (
            <>
              <Button color="inherit" onClick={handleAdminMenuOpen} endIcon={<ArrowDropDownIcon />}>
                Admin
              </Button>
              <Menu anchorEl={adminMenuEl} open={Boolean(adminMenuEl)} onClose={handleAdminMenuClose}>
                <MenuItem component={Link} to="/admin/users" onClick={handleAdminMenuClose}>
                  Manage Users
                </MenuItem>
                <MenuItem component={Link} to="/admin/settings" onClick={handleAdminMenuClose}>
                  Settings
                </MenuItem>
                <MenuItem component={Link} to="/admin/logs" onClick={handleAdminMenuClose}>
                  View Logs
                </MenuItem>
              </Menu>
            </>
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
        <Menu anchorEl={mobileMenuEl} open={Boolean(mobileMenuEl)} onClose={handleMobileMenuClose} sx={{ display: { md: "none" } }}>
          {isAdmin && (
            <>
              <MenuItem component={Link} to="/admin/users" onClick={handleMobileMenuClose}>
                Manage Users
              </MenuItem>
              <MenuItem component={Link} to="/admin/settings" onClick={handleMobileMenuClose}>
                Settings
              </MenuItem>
              <MenuItem component={Link} to="/admin/logs" onClick={handleMobileMenuClose}>
                View Logs
              </MenuItem>
            </>
          )}
          <MenuItem component={Link} to="/personas" onClick={handleMobileMenuClose}>
            Personas
          </MenuItem>
          <MenuItem component={Link} to="/chat" onClick={handleMobileMenuClose}>
            Chat
          </MenuItem>
          <MenuItem
            onClick={() => {
              handleMobileMenuClose();
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
