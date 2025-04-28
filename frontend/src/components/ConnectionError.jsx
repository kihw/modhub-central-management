import React from "react";
import { Box, Typography, Button } from "@mui/material";
import { Warning as WarningIcon } from "@mui/icons-material";

const ConnectionError = () => {
  const handleRetry = () => {
    window.location.reload(); // Recharge la page pour retenter la connexion
  };

  return (
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      justifyContent="center"
      height="100vh"
      textAlign="center"
      p={2}
    >
      <WarningIcon color="error" sx={{ fontSize: 80 }} />
      <Typography variant="h4" mt={2}>
        Connexion au serveur impossible
      </Typography>
      <Typography variant="body1" mt={1}>
        Vérifiez que le backend est en ligne et essayez de recharger la page.
      </Typography>
      <Button
        variant="contained"
        color="primary"
        onClick={handleRetry}
        sx={{ mt: 3 }}
      >
        Réessayer
      </Button>
    </Box>
  );
};

export default ConnectionError;
