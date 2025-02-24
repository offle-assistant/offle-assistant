import React from "react";
import { logout } from "../utils/auth";

const Navbar: React.FC = () => {
    return (
        <nav>
            <button onClick={logout}>Logout</button>
        </nav>
    );
};

export default Navbar;
