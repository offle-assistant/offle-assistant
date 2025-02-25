import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Personas from "./pages/Personas";
// import ChatPage from "./pages/ChatPage";
import PrivateRoute from "./components/PrivateRoute";

const App: React.FC = () => {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Login />} />
                <Route path="/register" element={<Register />} />

                {/* Protected Routes */}
                <Route element={<PrivateRoute />}>
                    <Route path="/personas" element={<Personas />} />
                    {/* <Route path="/chat/:personaId" element={<ChatPage />} /> */}
                </Route>
            </Routes>
        </Router>
    );
};

export default App;
