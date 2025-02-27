import React, { useEffect, useState } from "react";
import { api } from "../utils/api";
import {
  Box,
  Typography,
  CircularProgress,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Paper,
  Divider,
  Fab,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
} from "@mui/material";
import AddIcon from "@mui/icons-material/Add";

//TODO: Remove the padding on root, and root box element to get rid of white space?



type Persona = {
  id: string;
  name: string;
  description: string;
};

const Personas: React.FC = () => {
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [selectedPersona, setSelectedPersona] = useState<Persona | null>(null);
  const [loading, setLoading] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [editDialogOpen, setEditDialogOpen] = useState(false);


  useEffect(() => {
    fetchPersonas();
  }, []);

  // Fetch all personas
  const fetchPersonas = async () => {
    try {
        const res = await api.get<{ user_id: string; persona_dict: { [id: string]: string } }>("/personas/owned");

        console.log("API Response:", res.data); // Debugging step

        // Ensure we extract only `persona_dict`
        if (!res.data.persona_dict || Object.keys(res.data.persona_dict).length === 0) {
            console.warn("No personas found in API response.");
            setPersonas([]);
            return;
        }

        const transformedPersonas = Object.entries(res.data.persona_dict)
            .map(([id, name]) => {
                if (id.length !== 24) {
                    console.error("Skipping invalid Persona ID:", id);
                    return null; // Skip invalid IDs
                }
                return {
                    id,
                    name,
                    description: "No description available", // Placeholder description
                };
            })
            .filter((p): p is Persona => p !== null); // ✅ Type assertion to remove `null`

        setPersonas(transformedPersonas);

        if (transformedPersonas.length > 0) {
            fetchPersonaDetails(transformedPersonas[0].id); // Auto-select first persona safely
        } else {
            console.warn("No valid personas found.");
        }
    } catch (err) {
        console.error("Failed to fetch personas:", err);
        alert("Error fetching personas");
    } finally {
        setLoading(false);
    }
};


  const fetchPersonaDetails = async (personaId: string) => {
    setSelectedPersona(null);
    try {
      const res = await api.get<Persona>(`/personas/${personaId}`);
      setSelectedPersona(res.data);
    } catch (err) {
      console.error("Failed to fetch persona details:", err);
      alert("Error fetching persona details");
    }
};

  // Create a new persona
  const createPersona = async () => {
    try {
      await api.post("/personas/build", { name, description });
      alert("Persona Created!");
      setName("");
      setDescription("");
      setDialogOpen(false);
      fetchPersonas(); // Refresh Data
    } catch (err) {
      console.error("Failed to create persona:", err);
      alert("Failed to create persona");
    }
  };

  // Function to update persona details
const updatePersona = async (personaId: string | undefined) => {
  if (!personaId || !selectedPersona) return;

  try {
    const updates = {
      name: selectedPersona.name,
      description: selectedPersona.description,
    };

    const res = await api.put(`/personas/build/${personaId}`, updates);
    console.log("Update Response:", res.data);
    alert("Persona updated successfully!");

    // Refresh persona list after update
    fetchPersonas();
    setEditDialogOpen(false);
  } catch (err) {
    console.error("Failed to update persona:", err);
    alert("Error updating persona");
  }
};


return (
  <Box
    sx={{
      display: "flex",
      height: "85vh", // Full viewport height
      width: "90vw", // Full viewport width
      backgroundColor: "#121212", // Dark mode
      color: "white",
      overflow: "hidden", // Prevent scrollbar
      padding: "16px", // Add padding to prevent elements touching screen edges
      boxSizing: "border-box",
    }}
  >
    {/* Left Sidebar: Persona List */}
    <Paper
      sx={{
        width: { xs: "35%", md: "30%" }, // Responsive width
        maxWidth: "350px",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        background: "linear-gradient(to bottom, #6A11CB, #2575FC)",
        color: "white",
        borderRadius: "12px",
        boxShadow: "6px 0px 15px rgba(0,0,0,0.3)",
        overflow: "hidden",
        marginRight: "16px", // Add gap between sections
      }}
    >
      <Typography variant="h6" sx={{ fontWeight: "bold", textAlign: "center", p: 2 }}>
        Personas
      </Typography>
      <Divider sx={{ borderColor: "rgba(255,255,255,0.5)" }} />
      {loading ? (
        <Box sx={{ textAlign: "center", mt: 3 }}>
          <CircularProgress sx={{ color: "white" }} />
          <Typography>Loading personas...</Typography>
        </Box>
      ) : (
        <List sx={{ flexGrow: 1, overflowY: "auto", p: 1 }}>
          {personas.length > 0 ? (
            personas.map((persona) => (
              <ListItem key={persona.id} disablePadding>
                <ListItemButton
                  selected={selectedPersona?.id === persona.id}
                  onClick={() => fetchPersonaDetails(persona.id)}
                  sx={{
                    color: "white",
                    "&.Mui-selected": { backgroundColor: "rgba(255,255,255,0.3)" },
                    "&:hover": { backgroundColor: "rgba(255,255,255,0.2)" },
                    borderRadius: "8px",
                    transition: "0.3s",
                    padding: "12px",
                  }}
                >
                  <ListItemText primary={persona.name} />
                </ListItemButton>
              </ListItem>
            ))
          ) : (
            <Typography sx={{ textAlign: "center", mt: 2 }}>No personas found.</Typography>
          )}
        </List>
      )}
    </Paper>

    {/* Right Side: Persona Details */}
    <Paper
      sx={{
        flexGrow: 1,
        width: "70%",
        height: "100%",
        p: 4,
        background: "#1E1E1E",
        color: "white",
        borderRadius: "12px",
        boxShadow: "-6px 0px 15px rgba(0,0,0,0.3)",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        overflow: "hidden",
      }}
    >
      {selectedPersona ? (
        <>
          <Typography variant="h4" sx={{ fontWeight: "bold", mb: 2 }}>
            {selectedPersona.name}
          </Typography>
          <Typography variant="body1" sx={{ mb: 2 }}>
            {selectedPersona.description}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            More details coming soon...
          </Typography>
          <Button
            variant="contained"
            sx={{ mt: 3, backgroundColor: "#4CAF50", color: "white" }}
            onClick={() => setEditDialogOpen(true)}
          >
            EDIT PERSONA
          </Button>
        </>
      ) : (
        <Typography variant="h5" sx={{ textAlign: "center", mt: 10, color: "gray" }}>
          Select a persona to view details
        </Typography>
      )}
    </Paper>

    {/* Floating Action Button (FAB) to Open Create Dialog */}
    <Fab
      color="secondary"
      sx={{
        position: "absolute",
        bottom: 24,
        left: "calc(20% + 40px)", // Position near persona list
        boxShadow: "0px 4px 12px rgba(0,0,0,0.3)",
        background: "linear-gradient(to right, #FF512F, #DD2476)",
        "&:hover": { transform: "scale(1.1)", transition: "0.2s" },
      }}
      onClick={() => setDialogOpen(true)}
    >
      <AddIcon />
    </Fab>

    {/* Dialog for Creating a Persona */}
    <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} fullWidth maxWidth="sm">
      <DialogTitle sx={{ backgroundColor: "#4A90E2", color: "white" }}>Create a New Persona</DialogTitle>
      <DialogContent sx={{ backgroundColor: "rgba(255,255,255,0.95)" }}>
        <TextField
          label="Persona Name"
          variant="outlined"
          fullWidth
          value={name}
          onChange={(e) => setName(e.target.value)}
          sx={{ mt: 2 }}
        />
        <TextField
          label="Description"
          variant="outlined"
          fullWidth
          multiline
          rows={3}
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          sx={{ mt: 2 }}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setDialogOpen(false)} color="secondary">
          Cancel
        </Button>
        <Button onClick={createPersona} sx={{ background: "#FF512F", color: "white" }}>
          Create
        </Button>
      </DialogActions>
    </Dialog>

    {/* Dialog for Editing a Persona */}
    <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} fullWidth maxWidth="sm">
      <DialogTitle sx={{ backgroundColor: "#4A90E2", color: "white" }}>Edit Persona</DialogTitle>
      <DialogContent sx={{ backgroundColor: "rgba(255,255,255,0.95)" }}>
        <TextField
          label="Persona Name"
          variant="outlined"
          fullWidth
          value={selectedPersona?.name || ""}
          onChange={(e) => 
            setSelectedPersona((prev) => prev ? { ...prev, name: e.target.value } : prev)
          }
          sx={{ mt: 2 }}
        />
        <TextField
          label="Description"
          variant="outlined"
          fullWidth
          multiline
          rows={3}
          value={selectedPersona?.description || ""}
          onChange={(e) => 
            setSelectedPersona((prev) => prev ? { ...prev, description: e.target.value } : prev)
          }
          sx={{ mt: 2 }}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={() => setEditDialogOpen(false)} color="secondary">
          Cancel
        </Button>
        <Button 
          onClick={() => selectedPersona && updatePersona(selectedPersona.id)} 
          sx={{ background: "#4CAF50", color: "white" }}
        >
          Save Changes
        </Button>
      </DialogActions>
    </Dialog>

  </Box>
);


};

export default Personas;
