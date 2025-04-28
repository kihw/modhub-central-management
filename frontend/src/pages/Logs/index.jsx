```jsx
import React, { useState, useEffect, useMemo } from 'react';
import { FiSearch, FiFilter, FiDownload, FiTrash2, FiAlertCircle, FiInfo, FiCheckCircle } from 'react-icons/fi';
import { format } from 'date-fns';
import { Button, Input, Select, DateRangePicker, Checkbox } from '../../components/ui';