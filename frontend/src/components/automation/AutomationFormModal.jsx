import React, { useState } from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Box,
} from "@mui/material";

/**
 * AutomationFormModal component
 * Props:
 * - open: bool (contrôle si la modal est ouverte)
 * - onClose: function (appelée pour fermer la modal)
 * - onSubmit: function (appelée avec les données du formulaire)
 */
const AutomationFormModal = ({ open, onClose, onSubmit, initialData = {} }) => {
  const [formData, setFormData] = useState({
    name: initialData.name || "",
    description: initialData.description || "",
    schedule: initialData.schedule || "",
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = () => {
    onSubmit(formData);
    onClose();
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>
        {initialData.id
          ? "Modifier une automatisation"
          : "Nouvelle automatisation"}
      </DialogTitle>
      <DialogContent>
        <Box display="flex" flexDirection="column" gap={2} mt={1}>
          <TextField
            label="Nom"
            name="name"
            value={formData.name}
            onChange={handleChange}
            fullWidth
          />
          <TextField
            label="Description"
            name="description"
            value={formData.description}
            onChange={handleChange}
            fullWidth
            multiline
            rows={3}
          />
          <TextField
            label="Schedule (ex: cron)"
            name="schedule"
            value={formData.schedule}
            onChange={handleChange}
            fullWidth
          />
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Annuler</Button>
        <Button onClick={handleSubmit} variant="contained" color="primary">
          {initialData.id ? "Modifier" : "Créer"}
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default AutomationFormModal;
