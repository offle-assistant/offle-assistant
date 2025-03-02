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
  role: string; // "user" or "assistant"
  content: string;
  timestamp?: string; // Optional timestamp field
};

type MessageHistory = {
  _id: string;
  messages: Message[];
};

const ChatPage: React.FC = () => {
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [selectedPersona, setSelectedPersona] = useState<Persona | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [messageContent, setMessageContent] = useState("");
  const [messageHistoryId, setMessageHistoryId] = useState<string | null>(null);


  // Fetch all personas
  const fetchPersonas = async () => {
    try {
      const res = await api.get("/personas/owned");
      console.log("API Response:", res.data);

      if (!res.data || !res.data.persona_dict || typeof res.data.persona_dict !== "object") {
        throw new Error("Invalid API response format: Missing persona_dict");
      }

      const personaDict = res.data.persona_dict;

      const transformedPersonas = Object.entries(personaDict).map(([id, name]) => ({
        id,
        name: typeof name === "string" ? name : "Unnamed Persona",
      }));

      console.log("Transformed Personas:", transformedPersonas);

      setPersonas(transformedPersonas);
      setLoading(false);
    } catch (err) {
      console.error("Failed to fetch personas:", err);
    }
  };

  // Fetch message history for the selected persona
  const fetchMessageHistory = async (personaId: string) => {
    try {
      const res = await api.get<{ message_history: MessageHistory[] }>(`/personas/message-history/${personaId}`);
      console.log("Full Message History Object:", res.data.message_history);
  
      if (!res.data || !Array.isArray(res.data.message_history)) {
        throw new Error("Invalid message history response");
      }
  
      // If a history exists, set the messageHistoryId from the first entry
      if (res.data.message_history.length > 0) {
        setMessageHistoryId(res.data.message_history[0]._id);
      }
  
      const formattedMessages: Message[] = res.data.message_history.flatMap((history) =>
        history.messages.map((msg) => ({
          role: msg.role,
          content: msg.content || "No content available",
          timestamp: msg.timestamp || new Date().toISOString(),
        }))
      );
  
      setMessages(formattedMessages);
    } catch (err) {
      console.error("Failed to fetch message history:", err);
    }
  };
  

  const sendMessage = async () => {
    if (!selectedPersona || !messageContent.trim()) return;
  
    try {
      const res = await api.post(`/personas/chat/${selectedPersona.id}`, {
        message_history_id: messageHistoryId, // Now using the correct state
        content: messageContent,
      });
  
      console.log("Chat API Response:", res.data);
  
      // Set messageHistoryId if it's a new conversation
      if (!messageHistoryId) {
        setMessageHistoryId(res.data.message_history_id);
      }
  
      setMessages((prevMessages) => [
        ...prevMessages,
        { role: "user", content: messageContent, timestamp: new Date().toISOString() },
        { role: "assistant", content: res.data.response, timestamp: new Date().toISOString() },
      ]);
  
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
        height: "85vh",
        width: "90vw",
        backgroundColor: "#121212",
        color: "white",
        overflow: "hidden",
        padding: "16px",
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
                  <Typography key={index} sx={{ mb: 1, color: msg.role === "user" ? "#4CAF50" : "white" }}>
                    <strong>{msg.role === "user" ? "You" : "AI"}:</strong> {msg.content}
                    <small style={{ color: "gray", marginLeft: "10px" }}>{msg.timestamp}</small>
                  </Typography>
                ))
              ) : (
                <Typography sx={{ color: "gray", textAlign: "center", mt: 5 }}>
                  Start a conversation with {selectedPersona?.name}!
                </Typography>
              )}
            </Box>

            {/* Input and Send Button */}
            <Box sx={{ display: "flex", gap: 1, pb: 2, alignItems: "center" }}>
              <TextField
                fullWidth
                variant="outlined"
                value={messageContent}
                onChange={(e) => setMessageContent(e.target.value)}
                sx={{
                  bgcolor: "rgba(255, 255, 255, 0.1)", // Slight transparency to contrast against background
                  borderRadius: "8px",
                  input: { color: "white" }, // Set text color to white
                  "& .MuiOutlinedInput-root": {
                    "& fieldset": { borderColor: "rgba(255, 255, 255, 0.5)" }, // Light border
                    "&:hover fieldset": { borderColor: "white" }, // White border on hover
                    "&.Mui-focused fieldset": { borderColor: "#4CAF50" }, // Green border on focus
                  },
                }}
              />
              <Button variant="contained" sx={{ bgcolor: "#4CAF50", color: "white" }} onClick={sendMessage}>
                Send
              </Button>
            </Box>

          </>
        ) : (
          <Typography>Select a persona to start chatting</Typography>
        )}
      </Paper>
    </Box>
  );
};

export default ChatPage;
