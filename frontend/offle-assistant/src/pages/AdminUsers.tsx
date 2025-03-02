import React, { useEffect, useState } from "react";
import { api } from "../utils/api";
import {
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Select,
  MenuItem,
  CircularProgress,
} from "@mui/material";

type User = {
  id: string;
  username: string;
  email: string;
  role: string;
};

const AdminUsers: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchUsers = async () => {
    try {
      const res = await api.get<User[]>("/admin/users");
      setUsers(res.data);
      setLoading(false);
    } catch (err) {
      console.error("Failed to fetch users:", err);
      setLoading(false);
    }
  };

  const handleRoleChange = async (userId: string, newRole: string) => {
    try {
      await api.put(`/admin/users/${userId}/role`, { new_role: newRole });
      setUsers((prevUsers) =>
        prevUsers.map((user) =>
          user.id === userId ? { ...user, role: newRole } : user
        )
      );
    } catch (err) {
      console.error("Failed to update role:", err);
    }
  };

  const handleDeleteUser = async (userId: string) => {
    try {
      await api.delete(`/admin/users/${userId}/delete`);
      setUsers((prevUsers) => prevUsers.filter((user) => user.id !== userId));
    } catch (err) {
      console.error("Failed to delete user:", err);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  return (
    <Box
      sx={{
        p: 4,
        maxWidth: "1100px",
        margin: "auto",
        textAlign: "center",
        color: "white",
      }}
    >
      {/* Page Title with Gradient Background */}
      <Box
        sx={{
          background: "linear-gradient(to right, #667eea, #764ba2)",
          p: 2,
          borderRadius: "8px",
          mb: 3,
        }}
      >
        <Typography variant="h4" sx={{ fontWeight: "bold" }}>
          Manage Users
        </Typography>
      </Box>

      {/* Loading Indicator */}
      {loading ? (
        <Box sx={{ display: "flex", justifyContent: "center", mt: 4 }}>
          <CircularProgress sx={{ color: "white" }} />
        </Box>
      ) : (
        <TableContainer
          component={Paper}
          sx={{
            backgroundColor: "#1e1e1e",
            borderRadius: "12px",
            boxShadow: "0px 4px 10px rgba(0,0,0,0.3)",
            overflow: "hidden",
          }}
        >
          <Table>
            <TableHead>
              <TableRow sx={{ background: "#764ba2" }}>
                <TableCell sx={{ color: "white", fontWeight: "bold" }}>
                  Username
                </TableCell>
                <TableCell sx={{ color: "white", fontWeight: "bold" }}>
                  Email
                </TableCell>
                <TableCell sx={{ color: "white", fontWeight: "bold" }}>
                  Role
                </TableCell>
                <TableCell sx={{ color: "white", fontWeight: "bold" }}>
                  Actions
                </TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {users.map((user, index) => (
                <TableRow
                  key={user.id}
                  sx={{
                    backgroundColor: index % 2 === 0 ? "#292929" : "#1e1e1e",
                    "&:hover": { backgroundColor: "#333" },
                  }}
                >
                  <TableCell sx={{ color: "white" }}>{user.username}</TableCell>
                  <TableCell sx={{ color: "white" }}>{user.email}</TableCell>
                  <TableCell>
                    <Select
                      value={user.role}
                      onChange={(e) =>
                        handleRoleChange(user.id, e.target.value)
                      }
                      sx={{
                        color: "white",
                        backgroundColor: "#333",
                        borderRadius: "8px",
                        "& .MuiOutlinedInput-notchedOutline": {
                          borderColor: "white",
                        },
                      }}
                    >
                      <MenuItem value="admin">Admin</MenuItem>
                      <MenuItem value="user">User</MenuItem>
                    </Select>
                  </TableCell>
                  <TableCell>
                    <Button
                      variant="contained"
                      sx={{
                        background: "linear-gradient(to right, #ff416c, #ff4b2b)",
                        color: "white",
                        borderRadius: "8px",
                        "&:hover": {
                          background: "linear-gradient(to right, #ff4b2b, #ff416c)",
                        },
                      }}
                      onClick={() => handleDeleteUser(user.id)}
                    >
                      Delete
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
};

export default AdminUsers;
