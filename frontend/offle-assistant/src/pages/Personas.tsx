import React, { useEffect, useState } from "react";
import { api } from "../utils/api";

type Persona = {
    id: string;
    name: string;
};

const Personas: React.FC = () => {
    const [personas, setPersonas] = useState<Persona[]>([]);
    const [name, setName] = useState("");
    const [description, setDescription] = useState("");
    const [loading, setLoading] = useState(true);

    const fetchPersonas = async () => {
        try {
            const res = await api.get("/personas/owned");
            console.log("API Response:", res.data); // Debugging API response

            // Convert dictionary into an array of objects
            const transformedPersonas = Object.entries(res.data).map(([id, name]) => ({
                id,
                name: name as string,
            }));

            setPersonas(transformedPersonas);
        } catch (err) {
            console.error("Failed to fetch personas:", err);
            alert("Error fetching personas");
        } finally {
            setLoading(false); 
        }
    };

    useEffect(() => {
        fetchPersonas();
    }, []);

    const createPersona = async () => {
        try {
            await api.post("/personas/build", { name, description });
            alert("Persona Created!");
            setName("");
            setDescription("");
            fetchPersonas(); // Get Data
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

            {loading ? (
                <p>Loading personas...</p>
            ) : (
                <ul>
                    {personas.length > 0 ? (
                        personas.map((p) => (
                            <li key={p.id}>{p.name}</li>
                        ))
                    ) : (
                        <p>No personas found.</p>
                    )}
                </ul>
            )}
        </div>
    );
};

export default Personas;
