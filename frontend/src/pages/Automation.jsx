```jsx
import React, { useState, useEffect } from 'react';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { PlusCircleIcon, TrashIcon, ChevronDownIcon, ChevronUpIcon, AdjustmentsVerticalIcon, PlayIcon, PauseIcon } from '@heroicons/react/24/outline';
import { toast } from 'react-toastify';
import axios from 'axios';