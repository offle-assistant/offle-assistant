import React, { useState } from "react";
import { api, setAuthToken } from "../utils/api";
import { useNavigate } from "react-router-dom";
import axios from "axios";

type AuthFormProps = {
    type: "login" | "register";
};

const AuthForm: React.FC<AuthFormProps> = ({ type }) => {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        const endpoint = type === "login" ? "/auth/login" : "/auth/register";
        try {
            const res = await api.post(endpoint, { email, password });

            if (type === "login") {
                const token = res.data.access_token;
                localStorage.setItem("token", token); //Store JWT token
                setAuthToken(token); //Attach token to axios headers
                navigate("/personas"); //Redirect after login
            }
            alert("Login successful!");
        } catch (err: unknown) {
            if (axios.isAxiosError(err)) {
                alert(err.response?.data?.detail || "An error occurred");
            } else {
                alert("An unexpected error occurred");
            }
        }
    };

    return (
        <form onSubmit={handleSubmit}>
            <h2>{type === "login" ? "Login" : "Register"}</h2>
            <input type="email" placeholder="Email" onChange={(e) => setEmail(e.target.value)} required />
            <input type="password" placeholder="Password" onChange={(e) => setPassword(e.target.value)} required />
            <button type="submit">{type === "login" ? "Login" : "Register"}</button>
        </form>
    );
};

export default AuthForm;
