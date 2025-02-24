import React, { useEffect, useState } from "react";
import { api } from "../utils/api";

type Persona = {
    id: string;
    name: string;
    description: string;
};

const Personas: React.FC = () => {
    const [personas, setPersonas] = useState<Persona[]>([]);
    const [name, setName] = useState("");
    const [description, setDescription] = useState("");

    useEffect(() => {
        api.get("/personas")
            .then((res) => setPersonas(res.data))
            .catch((err) => {
                console.error("Failed to fetch personas:", err);
                alert("Error fetching personas");
            });
    }, []);

    const createPersona = async () => {
        try {
            await api.post("/personas/build", { name, description });
            alert("Persona Created!");
            setName("");
            setDescription("");
        } catch (err) {
            console.error("Failed to create persona:", err);
            alert("Failed to create persona");
        }
    };

    return (
        <div>
            <h1>Manage Personas</h1>
            <input
                type="text"
                placeholder="Persona Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
            />
            <input
                type="text"
                placeholder="Description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
            />
            <button onClick={createPersona}>Create Persona</button>

            <ul>
                {personas.map((p) => (
                    <li key={p.id}>{p.name} - {p.description}</li>
                ))}
            </ul>
        </div>
    );
};

export default Personas;
