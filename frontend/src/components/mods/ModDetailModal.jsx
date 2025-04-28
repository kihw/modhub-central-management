import React from "react";
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  Button,
  Box,
  Chip,
} from "@mui/material";

/**
 * ModDetailModal component
 * Props:
 * - open: bool (contrôle l'ouverture)
 * - onClose: function (ferme la modal)
 * - mod: objet contenant les infos du mod (name, version, description, status)
 */
const ModDetailModal = ({ open, onClose, mod }) => {
  if (!mod) return null;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Détails du Mod</DialogTitle>
      <DialogContent dividers>
        <Typography variant="h6">{mod.name}</Typography>
        <Typography variant="subtitle1" color="text.secondary">
          Version: {mod.version}
        </Typography>
        {mod.status && (
          <Box mt={1}>
            <Chip
              label={mod.status}
              color={mod.status === "installed" ? "success" : "default"}
              variant="outlined"
            />
          </Box>
        )}
        <Typography variant="body1" mt={2}>
          {mod.description}
        </Typography>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Fermer</Button>
        {mod.status !== "installed" && (
          <Button
            variant="contained"
            color="primary"
            onClick={() => console.log("Installer mod")}
          >
            Installer
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

export default ModDetailModal;
