import React, { useEffect, useState } from "react";
import { api } from "../utils/api";
import {
  Box,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Divider,
  CircularProgress,
  TextField,
  Button,
} from "@mui/material";

type Persona = {
  id: string;
  name: string;
};

type Message = {
  sender: string;
  content: string;
};

const ChatPage: React.FC = () => {
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [selectedPersona, setSelectedPersona] = useState<Persona | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [messageContent, setMessageContent] = useState("");

  // Fetch all personas
  const fetchPersonas = async () => {
    try {
      const res = await api.get("/personas/owned");
      console.log("API Response:", res.data); // Debugging
  
      // Ensure the response contains persona_dict
      if (!res.data || !res.data.persona_dict || typeof res.data.persona_dict !== "object") {
        throw new Error("Invalid API response format: Missing persona_dict");
      }
  
      // Extract the persona_dict object
      const personaDict = res.data.persona_dict;
  
      // Transform personas into a valid array
      const transformedPersonas = Object.entries(personaDict).map(([id, name]) => ({
        id,
        name: typeof name === "string" ? name : "Unnamed Persona", // Handle unexpected formats
      }));
  
      console.log("Transformed Personas:", transformedPersonas); // Debugging output
  
      setPersonas(transformedPersonas);
      setLoading(false);
    } catch (err) {
      console.error("Failed to fetch personas:", err);
    }
  };
  

  // Fetch message history for the selected persona
  const fetchMessageHistory = async (personaId: string) => {
    try {
      const res = await api.get<{ message_history: Message[] }>(`/personas/message-history/${personaId}`);
      setMessages(res.data.message_history);
    } catch (err) {
      console.error("Failed to fetch message history:", err);
    }
  };

  // Handle sending a message
  const sendMessage = async () => {
    if (!selectedPersona || !messageContent.trim()) return;
    try {
      const res = await api.post(`/personas/chat/${selectedPersona.id}`, { content: messageContent });
      setMessages((prevMessages) => [...prevMessages, { sender: "You", content: messageContent }]);
      setMessages((prevMessages) => [...prevMessages, { sender: "AI", content: res.data.response }]);
      setMessageContent("");
    } catch (err) {
      console.error("Failed to send message:", err);
    }
  };

  useEffect(() => {
    fetchPersonas();
  }, []);

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
          width: { xs: "35%", md: "30%" },
          maxWidth: "350px",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          background: "linear-gradient(to bottom, #6A11CB, #2575FC)",
          color: "white",
          borderRadius: "12px",
          boxShadow: "6px 0px 15px rgba(0,0,0,0.3)",
          overflow: "hidden",
          marginRight: "16px",
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
                    onClick={() => {
                      setSelectedPersona(persona);
                      fetchMessageHistory(persona.id);
                    }}
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

      {/* Right Side: Chat Section */}
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
          justifyContent: "space-between",
          overflow: "hidden",
        }}
      >
        {selectedPersona ? (
          <>
            <Typography variant="h4" sx={{ fontWeight: "bold", mb: 2, textAlign: "center" }}>
              Chat with {selectedPersona.name}
            </Typography>

            {/* Chat Messages */}
            <Box sx={{ flexGrow: 1, overflowY: "auto", p: 2, borderRadius: "8px", bgcolor: "#222" }}>
              {messages.length > 0 ? (
                messages.map((msg, index) => (
                  <Typography key={index} sx={{ mb: 1, color: msg.sender === "You" ? "#4CAF50" : "white" }}>
                    <strong>{msg.sender}:</strong> {msg.content}
                  </Typography>
                ))
              ) : (
                <Typography sx={{ color: "gray", textAlign: "center", mt: 5 }}>
                  Start a conversation with {selectedPersona.name}!
                </Typography>
              )}
            </Box>

                        {/* Input and Send Button */}
            <Box sx={{ display: "flex", gap: 1, mt: 2, pb: 2, position: "relative" }}>
            <TextField
                fullWidth
                variant="outlined"
                placeholder="Type a message..."
                value={messageContent}
                onChange={(e) => setMessageContent(e.target.value)}
                sx={{
                bgcolor: "white",
                borderRadius: "8px",
                "& .MuiOutlinedInput-root": {
                    padding: "10px",
                },
                }}
            />
            <Button
                variant="contained"
                sx={{
                bgcolor: "#4CAF50",
                color: "white",
                height: "100%",
                px: 3, // Padding inside the button
                }}
                onClick={sendMessage}
            >
                Send
            </Button>
            </Box>

          </>
        ) : (
          <Typography variant="h5" sx={{ textAlign: "center", mt: 10, color: "gray" }}>
            Select a persona to start chatting
          </Typography>
        )}
      </Paper>
    </Box>
  );
};

export default ChatPage;
