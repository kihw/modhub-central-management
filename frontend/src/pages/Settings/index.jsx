```jsx
import React, { useState, useEffect } from 'react';
import { FiSettings, FiSave, FiRefreshCw, FiHelpCircle, FiToggleLeft, FiToggleRight } from 'react-icons/fi';
import { Tabs, TabList, Tab, TabPanel } from 'react-tabs';
import { Switch, Select, Input, Button, notification, Tooltip, Card, Divider } from '../../components/ui';
import { useSettings } from '../../contexts/SettingsContext';
import { useTheme } from '../../contexts/ThemeContext';
import ConfirmDialog from '../../components/ConfirmDialog';