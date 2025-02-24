import React from "react";
import AuthForm from "../components/AuthForm";

const Register: React.FC = () => {
    return (
        <div>
            <h1>Register</h1>
            <AuthForm type="register" />
        </div>
    );
};

export default Register;
