import React from "react";
import { Box, Typography, Chip } from "@mui/material";
import {
  CheckCircle as CheckIcon,
  Cancel as CancelIcon,
} from "@mui/icons-material";
import { useBackendStatus } from "../hooks/useBackendStatus";

const ServerStatusIndicator = () => {
  const { isConnected, loading } = useBackendStatus();

  let status = "Indéterminé";
  let color = "default";
  let icon = null;

  if (loading) {
    status = "Vérification...";
  } else if (isConnected) {
    status = "Connecté";
    color = "success";
    icon = <CheckIcon />;
  } else {
    status = "Déconnecté";
    color = "error";
    icon = <CancelIcon />;
  }

  return (
    <Box display="flex" alignItems="center">
      <Typography variant="body1" mr={1}>
        Serveur :
      </Typography>
      <Chip
        icon={icon}
        label={status}
        color={color}
        variant="outlined"
        sx={{ fontWeight: "bold" }}
      />
    </Box>
  );
};

export default ServerStatusIndicator;
