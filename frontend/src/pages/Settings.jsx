```jsx
import React, { useState, useEffect } from 'react';
import { FiSave, FiRefreshCw, FiHardDrive, FiCpu, FiThermometer, FiUserPlus, FiAlertCircle } from 'react-icons/fi';
import { toast } from 'react-toastify';
import Switch from '../components/UI/Switch';
import Button from '../components/UI/Button';
import { useSettingsContext } from '../contexts/SettingsContext';
import Card from '../components/UI/Card';
import TabGroup from '../components/UI/TabGroup';
import Spinner from '../components/UI/Spinner';