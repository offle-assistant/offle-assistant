import React, { useState, useEffect } from "react";
import { Navigate, Outlet } from "react-router-dom";
import { getToken } from "../utils/auth";

const PrivateRoute: React.FC = () => {
    const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null);

    useEffect(() => {
        const token = getToken();
        setIsAuthenticated(!!token); // Convert to boolean
    }, []);

    if (isAuthenticated === null) {
        return <p>Loading...</p>;
    }

    return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
};

export default PrivateRoute;
