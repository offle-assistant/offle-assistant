// src/App.tsx
import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Personas from "./pages/Personas";
import PrivateRoute from "./components/PrivateRoute";
import Layout from "./components/Layout";
import { AuthProvider } from "./context/AuthContext";
import ChatPage from "./pages/ChatPage";

const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route element={<PrivateRoute />}>
            <Route element={<Layout />}>
              <Route path="personas" element={<Personas />} />
              <Route path="chat" element={<ChatPage />} />

            </Route>
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  );
};

export default App;
