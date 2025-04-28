import React, { useState, useEffect } from 'react';
import { Trash2, Edit, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Badge } from './ui/Badge';

const TaskList = ({ tasks, onDeleteTask, onEditTask, onToggleTaskStatus }) => {
  const [filteredTasks, setFilteredTasks] = useState([]);
  const [filter, setFilter] = useState('all');
  const [sortBy, setSortBy] = useState('date');
  const [searchQuery, setSearchQuery] = useState('');

  useEffect(() => {
    let result = [...tasks];
    
    // Filter by status
    if (filter === 'active') {
      result = result.filter(task => !task.completed);
    } else if (filter === 'completed') {
      result = result.filter(task => task.completed);
    }
    
    // Filter by search query
    if (searchQuery) {
      result = result.filter(task => 
        task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        task.description.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }
    
    // Sort tasks
    if (sortBy === 'date') {
      result.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt));
    } else if (sortBy === 'priority') {
      const priorityOrder = { high: 0, medium: 1, low: 2 };
      result.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);
    } else if (sortBy === 'name') {
      result.sort((a, b) => a.title.localeCompare(b.title));
    }
    
    setFilteredTasks(result);
  }, [tasks, filter, sortBy, searchQuery]);

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status) => {
    if (status) return <CheckCircle className="h-5 w-5 text-green-500" />;
    return <Clock className="h-5 w-5 text-blue-500" />;
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex flex-col md:flex-row justify-between items-center mb-6">
        <h2 className="text-xl font-semibold mb-4 md:mb-0">Tâches à exécuter</h2>
        
        <div className="flex flex-col sm:flex-row gap-4 w-full md:w-auto">
          <div className="relative">
            <input
              type="text"
              placeholder="Rechercher..."
              className="pl-10 pr-4 py-2 border rounded-md w-full sm:w-64"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <svg className="absolute left-3 top-2.5 h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
          </div>
          
          <div className="flex gap-2">
            <select 
              className="border rounded-md px-3 py-2 bg-white"
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
            >
              <option value="all">Tous</option>
              <option value="active">En cours</option>
              <option value="completed">Terminé</option>
            </select>
            
            <select 
              className="border rounded-md px-3 py-2 bg-white"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
            >
              <option value="date">Date</option>
              <option value="priority">Priorité</option>
              <option value="name">Nom</option>
            </select>
          </div>
        </div>
      </div>
      
      {filteredTasks.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-10 text-gray-500">
          <AlertCircle className="h-12 w-12 mb-3" />
          <p className="text-lg">Aucune tâche trouvée</p>
          <p className="text-sm">Modifiez vos filtres ou ajoutez une nouvelle tâche</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Statut
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tâche
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Priorité
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              <AnimatePresence>
                {filteredTasks.map((task) => (
                  <motion.tr 
                    key={task.id}
                    layout
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 20 }}
                    transition={{ duration: 0.2 }}
                    className={task.completed ? "bg-gray-50" : ""}
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <button
                        onClick={() => onToggleTaskStatus(task.id)}
                        className="flex items-center justify-center h-8 w-8 rounded-full hover:bg-gray-100"
                      >
                        {getStatusIcon(task.completed)}
                      </button>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex flex-col">
                        <span className={`text-sm font-medium ${task.completed ? "text-gray-400 line-through" : "text-gray-900"}`}>
                          {task.title}
                        </span>
                        <span className={`text-xs ${task.completed ? "text-gray-400" : "text-gray-500"}`}>
                          {task.description}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Badge className={getPriorityColor(task.priority)}>
                        {task.priority.charAt(0).toUpperCase() + task.priority.slice(1)}
                      </Badge>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(task.createdAt)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => onEditTask(task)}
                        className="text-indigo-600 hover:text-indigo-900 inline-flex items-center mr-3"
                      >
                        <Edit className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => onDeleteTask(task.id)}
                        className="text-red-600 hover:text-red-900 inline-flex items-center"
                      >
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </td>
                  </motion.tr>
                ))}
              </AnimatePresence>
            </tbody>
          </table>
        </div>
      )}
      
      <div className="mt-4 text-sm text-gray-500">
        {filteredTasks.length} tâche(s) • {tasks.filter(t => t.completed).length} terminée(s)
      </div>
    </div>
  );
};

export default TaskList;