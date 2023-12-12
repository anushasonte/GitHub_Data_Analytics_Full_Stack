import React, { useState, useEffect } from "react";
import { ListItem, ListItemButton, ListItemText } from "@mui/material";

const CommonGraphsButton = ({ onClick }) => {
  return (
    <ListItem button onClick={onClick}>
      <ListItemButton>
        <ListItemText primary="Common Graphs" />
      </ListItemButton>
    </ListItem>
  );
};

export default CommonGraphsButton;