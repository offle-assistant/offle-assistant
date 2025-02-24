import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Personas from "./pages/Personas";
// import ChatPage from "./pages/ChatPage";

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<Login />} />
                <Route path="/register" element={<Register />} />
                <Route path="/personas" element={<Personas />} />
                {/* <Route path="/chat/:personaId" element={<ChatPage />} /> */}
            </Routes>
        </Router>
    );
}

export default App;
