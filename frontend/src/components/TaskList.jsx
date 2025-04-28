import React from "react";
import {
  Box,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
} from "@mui/material";
import {
  Autorenew as RunningIcon,
  CheckCircle as DoneIcon,
  Error as ErrorIcon,
} from "@mui/icons-material";

/**
 * Dummy tasks for the example. Replace this with your actual task data.
 */
const dummyTasks = [
  { id: 1, name: "Téléchargement de mods", status: "running" },
  { id: 2, name: "Mise à jour des logs", status: "done" },
  { id: 3, name: "Analyse automatique", status: "error" },
];

const statusDetails = {
  running: { label: "En cours", color: "primary", icon: <RunningIcon /> },
  done: { label: "Terminé", color: "success", icon: <DoneIcon /> },
  error: { label: "Erreur", color: "error", icon: <ErrorIcon /> },
};

const TaskList = ({ tasks = dummyTasks }) => {
  return (
    <Box>
      <List>
        {tasks.map((task) => {
          const { label, color, icon } = statusDetails[task.status] || {};
          return (
            <ListItem key={task.id}>
              <ListItemIcon>{icon}</ListItemIcon>
              <ListItemText primary={task.name} />
              <Chip label={label} color={color} variant="outlined" />
            </ListItem>
          );
        })}
      </List>
    </Box>
  );
};

export default TaskList;
