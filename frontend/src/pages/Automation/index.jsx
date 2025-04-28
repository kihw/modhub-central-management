import React, { useState, useEffect } from 'react';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { 
  PlusIcon, 
  TrashIcon, 
  SaveIcon, 
  PlayIcon,
  PauseIcon,
  ChevronDownIcon,
  ChevronUpIcon
} from '@heroicons/react/outline';
import RuleEditor from '../../components/Automation/RuleEditor';
import RuleList from '../../components/Automation/RuleList';
import ConditionSelector from '../../components/Automation/ConditionSelector';
import ActionSelector from '../../components/Automation/ActionSelector';
import ConfirmDialog from '../../components/UI/ConfirmDialog';
import Notification from '../../components/UI/Notification';

const AutomationPage = () => {
  const [rules, setRules] = useState([]);
  const [selectedRule, setSelectedRule] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
  const [notification, setNotification] = useState({ show: false, message: '', type: 'success' });
  const [expandedSection, setExpandedSection] = useState('editor');

  useEffect(() => {
    // Fetch rules from API
    const fetchRules = async () => {
      try {
        const response = await fetch('http://localhost:5000/api/rules');
        const data = await response.json();
        setRules(data);
      } catch (error) {
        console.error('Error fetching rules:', error);
        showNotification('Failed to load automation rules', 'error');
      }
    };

    fetchRules();
  }, []);

  const showNotification = (message, type = 'success') => {
    setNotification({ show: true, message, type });
    setTimeout(() => setNotification({ ...notification, show: false }), 3000);
  };

  const handleCreateRule = () => {
    const newRule = {
      id: 'temp_' + Date.now(),
      name: 'New Rule',
      description: '',
      enabled: true,
      priority: rules.length + 1,
      conditions: [],
      actions: [],
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
    
    setSelectedRule(newRule);
    setIsEditing(true);
  };

  const handleSelectRule = (rule) => {
    setSelectedRule(rule);
    setIsEditing(false);
  };

  const handleEditRule = () => {
    setIsEditing(true);
  };

  const handleSaveRule = async (rule) => {
    try {
      // If rule has temp ID, it's a new rule
      const isNewRule = rule.id.startsWith('temp_');
      const method = isNewRule ? 'POST' : 'PUT';
      const url = isNewRule 
        ? 'http://localhost:5000/api/rules' 
        : `http://localhost:5000/api/rules/${rule.id}`;
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(rule),
      });
      
      if (!response.ok) throw new Error('Failed to save rule');
      
      const savedRule = await response.json();
      
      // Update local state
      if (isNewRule) {
        setRules([...rules, savedRule]);
      } else {
        setRules(rules.map(r => r.id === savedRule.id ? savedRule : r));
      }
      
      setSelectedRule(savedRule);
      setIsEditing(false);
      showNotification(`Rule "${savedRule.name}" saved successfully`);
    } catch (error) {
      console.error('Error saving rule:', error);
      showNotification('Failed to save rule', 'error');
    }
  };

  const handleDeleteRule = async () => {
    if (!selectedRule) return;
    
    try {
      // Only call API if not a temp rule
      if (!selectedRule.id.startsWith('temp_')) {
        const response = await fetch(`http://localhost:5000/api/rules/${selectedRule.id}`, {
          method: 'DELETE',
        });
        
        if (!response.ok) throw new Error('Failed to delete rule');
      }
      
      // Update local state
      setRules(rules.filter(rule => rule.id !== selectedRule.id));
      setSelectedRule(null);
      setIsDeleteDialogOpen(false);
      showNotification(`Rule "${selectedRule.name}" deleted successfully`);
    } catch (error) {
      console.error('Error deleting rule:', error);
      showNotification('Failed to delete rule', 'error');
    }
  };

  const handleToggleRuleStatus = async (rule) => {
    try {
      const updatedRule = { ...rule, enabled: !rule.enabled };
      
      const response = await fetch(`http://localhost:5000/api/rules/${rule.id}/toggle`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ enabled: updatedRule.enabled }),
      });
      
      if (!response.ok) throw new Error('Failed to update rule status');
      
      // Update local state
      setRules(rules.map(r => r.id === rule.id ? updatedRule : r));
      
      if (selectedRule && selectedRule.id === rule.id) {
        setSelectedRule(updatedRule);
      }
      
      showNotification(`Rule "${rule.name}" ${updatedRule.enabled ? 'enabled' : 'disabled'}`);
    } catch (error) {
      console.error('Error toggling rule status:', error);
      showNotification('Failed to update rule status', 'error');
    }
  };

  const handleCancelEdit = () => {
    if (selectedRule && selectedRule.id.startsWith('temp_')) {
      // Discard new rule
      setSelectedRule(null);
    } else {
      // Revert to view mode
      setIsEditing(false);
    }
  };

  const toggleSectionExpand = (section) => {
    setExpandedSection(expandedSection === section ? null : section);
  };

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Automation Rules</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Rule List Section */}
        <div className="bg-white rounded-lg shadow p-4 lg:col-span-1">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-gray-700">Rules</h2>
            <button 
              onClick={handleCreateRule}
              className="bg-blue-500 hover:bg-blue-600 text-white p-2 rounded-md flex items-center"
            >
              <PlusIcon className="h-5 w-5 mr-1" />
              <span>New Rule</span>
            </button>
          </div>
          
          <RuleList 
            rules={rules} 
            selectedRule={selectedRule}
            onSelectRule={handleSelectRule}
            onToggleRule={handleToggleRuleStatus}
          />
        </div>
        
        {/* Rule Editor/Viewer Section */}
        <div className="bg-white rounded-lg shadow lg:col-span-2">
          {selectedRule ? (
            <DndProvider backend={HTML5Backend}>
              <div className="p-4">
                {/* Header with controls */}
                <div className="flex justify-between items-center mb-4">
                  <div className="flex items-center">
                    <h2 className="text-lg font-semibold text-gray-700 mr-3">
                      {isEditing ? 'Edit Rule' : 'Rule Details'}
                    </h2>
                    <span 
                      className={`px-2 py-1 text-xs rounded-full ${
                        selectedRule.enabled ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {selectedRule.enabled ? 'Enabled' : 'Disabled'}
                    </span>
                  </div>
                  
                  <div className="flex space-x-2">
                    {isEditing ? (
                      <>
                        <button 
                          onClick={handleCancelEdit}
                          className="bg-gray-200 hover:bg-gray-300 text-gray-700 p-2 rounded-md"
                        >
                          Cancel
                        </button>
                        <button 
                          onClick={() => handleSaveRule(selectedRule)}
                          className="bg-green-500 hover:bg-green-600 text-white p-2 rounded-md flex items-center"
                        >
                          <SaveIcon className="h-5 w-5 mr-1" />
                          Save
                        </button>
                      </>
                    ) : (
                      <>
                        <button 
                          onClick={() => setIsDeleteDialogOpen(true)}
                          className="bg-red-500 hover:bg-red-600 text-white p-2 rounded-md flex items-center"
                        >
                          <TrashIcon className="h-5 w-5 mr-1" />
                          Delete
                        </button>
                        <button 
                          onClick={handleEditRule}
                          className="bg-blue-500 hover:bg-blue-600 text-white p-2 rounded-md flex items-center"
                        >
                          Edit
                        </button>
                        <button 
                          onClick={() => handleToggleRuleStatus(selectedRule)}
                          className={`${
                            selectedRule.enabled 
                              ? 'bg-yellow-500 hover:bg-yellow-600' 
                              : 'bg-green-500 hover:bg-green-600'
                          } text-white p-2 rounded-md flex items-center`}
                        >
                          {selectedRule.enabled ? (
                            <>
                              <PauseIcon className="h-5 w-5 mr-1" />
                              Disable
                            </>
                          ) : (
                            <>
                              <PlayIcon className="h-5 w-5 mr-1" />
                              Enable
                            </>
                          )}
                        </button>
                      </>
                    )}
                  </div>
                </div>
                
                {/* Rule Editor */}
                <RuleEditor 
                  rule={selectedRule}
                  setRule={setSelectedRule}
                  isEditing={isEditing}
                />
                
                {/* Expandable Sections */}
                {isEditing && (
                  <>
                    {/* Conditions Library */}
                    <div className="mt-6 border border-gray-200 rounded-lg">
                      <button 
                        className="w-full p-3 flex justify-between items-center bg-gray-100 hover:bg-gray-200 rounded-t-lg"
                        onClick={() => toggleSectionExpand('conditions')}
                      >
                        <span className="font-medium">Conditions Library</span>
                        {expandedSection === 'conditions' ? (
                          <ChevronUpIcon className="h-5 w-5" />
                        ) : (
                          <ChevronDownIcon className="h-5 w-5" />
                        )}
                      </button>
                      
                      {expandedSection === 'conditions' && (
                        <div className="p-4">
                          <ConditionSelector 
                            onSelectCondition={(condition) => {
                              setSelectedRule({
                                ...selectedRule,
                                conditions: [...selectedRule.conditions, condition]
                              });
                            }}
                          />
                        </div>
                      )}
                    </div>
                    
                    {/* Actions Library */}
                    <div className="mt-4 border border-gray-200 rounded-lg">
                      <button 
                        className="w-full p-3 flex justify-between items-center bg-gray-100 hover:bg-gray-200 rounded-t-lg"
                        onClick={() => toggleSectionExpand('actions')}
                      >
                        <span className="font-medium">Actions Library</span>
                        {expandedSection === 'actions' ? (
                          <ChevronUpIcon className="h-5 w-5" />
                        ) : (
                          <ChevronDownIcon className="h-5 w-5" />
                        )}
                      </button>
                      
                      {expandedSection === 'actions' && (
                        <div className="p-4">
                          <ActionSelector 
                            onSelectAction={(action) => {
                              setSelectedRule({
                                ...selectedRule,
                                actions: [...selectedRule.actions, action]
                              });
                            }}
                          />
                        </div>
                      )}
                    </div>
                  </>
                )}
              </div>
            </DndProvider>
          ) : (
            <div className="p-6 text-center text-gray-500">
              <p>Select a rule from the list or create a new one</p>
            </div>
          )}
        </div>
      </div>
      
      {/* Confirm Delete Dialog */}
      <ConfirmDialog
        isOpen={isDeleteDialogOpen}
        title="Delete Rule"
        message={`Are you sure you want to delete the rule "${selectedRule?.name}"? This action cannot be undone.`}
        confirmText="Delete"
        cancelText="Cancel"
        onConfirm={handleDeleteRule}
        onCancel={() => setIsDeleteDialogOpen(false)}
      />
      
      {/* Notification */}
      <Notification
        show={notification.show}
        message={notification.message}
        type={notification.type}
      />
    </div>
  );
};

export default AutomationPage;