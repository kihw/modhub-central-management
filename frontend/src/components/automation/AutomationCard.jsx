import React from "react";
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Button,
  Box,
  Chip,
} from "@mui/material";
import { Autorenew as ScheduleIcon } from "@mui/icons-material";

const AutomationCard = ({ automation, onEdit, onDelete }) => {
  return (
    <Card variant="outlined" sx={{ minWidth: 275 }}>
      <CardContent>
        <Typography variant="h5" component="div">
          {automation.name}
        </Typography>
        <Typography sx={{ mb: 1.5 }} color="text.secondary">
          {automation.description}
        </Typography>
        <Box display="flex" alignItems="center" gap={1}>
          <ScheduleIcon fontSize="small" color="action" />
          <Typography variant="body2">
            Schedule: {automation.schedule}
          </Typography>
        </Box>
        {automation.status && (
          <Box mt={2}>
            <Chip
              label={automation.status}
              color={automation.status === "active" ? "success" : "default"}
            />
          </Box>
        )}
      </CardContent>
      <CardActions>
        <Button size="small" onClick={() => onEdit(automation)}>
          Modifier
        </Button>
        <Button size="small" color="error" onClick={() => onDelete(automation)}>
          Supprimer
        </Button>
      </CardActions>
    </Card>
  );
};

export default AutomationCard;
