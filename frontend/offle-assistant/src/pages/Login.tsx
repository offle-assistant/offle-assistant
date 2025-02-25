import React from "react";
import AuthForm from "../components/AuthForm";

const Login: React.FC = () => {
    return (
        <div>
            <h1>Login</h1>
            <AuthForm type="login" />
        </div>
    );
};

export default Login;
