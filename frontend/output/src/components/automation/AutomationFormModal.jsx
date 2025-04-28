import { useState, useEffect } from 'react';
import { Dialog, Transition } from '@headlessui/react';
import { Fragment } from 'react';
import { XMarkIcon } from '@heroicons/react/24/outline';
import ProcessSelector from './ProcessSelector';
import TimeRangeSelector from './TimeRangeSelector';
import ActionSelector from './ActionSelector';
import PrioritySelector from './PrioritySelector';

const AutomationFormModal = ({ isOpen, closeModal, onSave, automationToEdit }) => {
  const [automation, setAutomation] = useState({
    id: null,
    name: '',
    description: '',
    enabled: true,
    conditions: {
      processes: [],
      timeRanges: [],
      inactivityTrigger: false,
      inactivityMinutes: 15,
    },
    actions: [],
    priority: 5, // Default priority (1-10)
  });

  const [errors, setErrors] = useState({});
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    if (automationToEdit) {
      setAutomation(automationToEdit);
      setIsEditing(true);
    } else {
      resetForm();
      setIsEditing(false);
    }
  }, [automationToEdit, isOpen]);

  const resetForm = () => {
    setAutomation({
      id: null,
      name: '',
      description: '',
      enabled: true,
      conditions: {
        processes: [],
        timeRanges: [],
        inactivityTrigger: false,
        inactivityMinutes: 15,
      },
      actions: [],
      priority: 5,
    });
    setErrors({});
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    const inputValue = type === 'checkbox' ? checked : value;
    
    setAutomation({
      ...automation,
      [name]: inputValue,
    });
    
    // Clear error for this field if it exists
    if (errors[name]) {
      setErrors({
        ...errors,
        [name]: null,
      });
    }
  };

  const handleInactivityChange = (e) => {
    const { name, value, type, checked } = e.target;
    const inputValue = type === 'checkbox' ? checked : value;
    
    setAutomation({
      ...automation,
      conditions: {
        ...automation.conditions,
        [name]: inputValue,
      }
    });
  };

  const handleProcessSelection = (selectedProcesses) => {
    setAutomation({
      ...automation,
      conditions: {
        ...automation.conditions,
        processes: selectedProcesses,
      }
    });
  };

  const handleTimeRangeSelection = (timeRanges) => {
    setAutomation({
      ...automation,
      conditions: {
        ...automation.conditions,
        timeRanges,
      }
    });
  };

  const handleActionSelection = (actions) => {
    setAutomation({
      ...automation,
      actions,
    });
    
    if (errors.actions) {
      setErrors({
        ...errors,
        actions: null,
      });
    }
  };

  const handlePriorityChange = (priority) => {
    setAutomation({
      ...automation,
      priority,
    });
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!automation.name.trim()) {
      newErrors.name = "Le nom est requis";
    }
    
    if (automation.actions.length === 0) {
      newErrors.actions = "Au moins une action est requise";
    }
    
    // Check if at least one condition type is set
    const hasCondition = 
      automation.conditions.processes.length > 0 || 
      automation.conditions.timeRanges.length > 0 ||
      automation.conditions.inactivityTrigger;
      
    if (!hasCondition) {
      newErrors.conditions = "Au moins une condition est requise";
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (validateForm()) {
      const automationToSave = {
        ...automation,
        id: automation.id || Date.now(), // Generate ID if it's a new automation
      };
      
      onSave(automationToSave);
      closeModal();
      resetForm();
    }
  };

  const handleCancel = () => {
    closeModal();
    resetForm();
  };

  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={closeModal}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/30" />
        </Transition.Child>

        <div className="fixed inset-0 overflow-y-auto">
          <div className="flex min-h-full items-center justify-center p-4">
            <Transition.Child
              as={Fragment}
              enter="ease-out duration-300"
              enterFrom="opacity-0 scale-95"
              enterTo="opacity-100 scale-100"
              leave="ease-in duration-200"
              leaveFrom="opacity-100 scale-100"
              leaveTo="opacity-0 scale-95"
            >
              <Dialog.Panel className="w-full max-w-3xl transform overflow-hidden rounded-lg bg-white p-6 shadow-xl transition-all">
                <div className="flex items-center justify-between mb-4">
                  <Dialog.Title as="h3" className="text-lg font-medium leading-6 text-gray-900">
                    {isEditing ? 'Modifier l\'automatisation' : 'Créer une nouvelle automatisation'}
                  </Dialog.Title>
                  <button
                    type="button"
                    className="text-gray-400 hover:text-gray-500"
                    onClick={closeModal}
                  >
                    <span className="sr-only">Fermer</span>
                    <XMarkIcon className="h-6 w-6" aria-hidden="true" />
                  </button>
                </div>

                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="space-y-4">
                    <div>
                      <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                        Nom de l'automatisation
                      </label>
                      <input
                        type="text"
                        id="name"
                        name="name"
                        value={automation.name}
                        onChange={handleInputChange}
                        className={`mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm ${
                          errors.name ? 'border-red-500' : ''
                        }`}
                        placeholder="Ex: Mode Gaming pour Battlefield"
                      />
                      {errors.name && (
                        <p className="mt-1 text-sm text-red-600">{errors.name}</p>
                      )}
                    </div>

                    <div>
                      <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                        Description (optionnelle)
                      </label>
                      <textarea
                        id="description"
                        name="description"
                        rows={2}
                        value={automation.description}
                        onChange={handleInputChange}
                        className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                        placeholder="Décrivez brièvement cette automatisation..."
                      />
                    </div>

                    <div className="flex items-center">
                      <input
                        id="enabled"
                        name="enabled"
                        type="checkbox"
                        checked={automation.enabled}
                        onChange={handleInputChange}
                        className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                      />
                      <label htmlFor="enabled" className="ml-2 block text-sm text-gray-700">
                        Activer cette automatisation
                      </label>
                    </div>

                    <div className="border-t border-gray-200 pt-4">
                      <h4 className="text-md font-medium text-gray-700 mb-2">Conditions</h4>
                      {errors.conditions && (
                        <p className="mt-1 text-sm text-red-600 mb-2">{errors.conditions}</p>
                      )}
                      
                      <div className="space-y-4">
                        <ProcessSelector
                          selectedProcesses={automation.conditions.processes}
                          onChange={handleProcessSelection}
                        />

                        <TimeRangeSelector
                          timeRanges={automation.conditions.timeRanges}
                          onChange={handleTimeRangeSelection}
                        />

                        <div>
                          <div className="flex items-center">
                            <input
                              id="inactivityTrigger"
                              name="inactivityTrigger"
                              type="checkbox"
                              checked={automation.conditions.inactivityTrigger}
                              onChange={handleInactivityChange}
                              className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                            />
                            <label htmlFor="inactivityTrigger" className="ml-2 block text-sm text-gray-700">
                              Déclencher après une période d'inactivité
                            </label>
                          </div>
                          
                          {automation.conditions.inactivityTrigger && (
                            <div className="mt-2 ml-6">
                              <label htmlFor="inactivityMinutes" className="block text-sm text-gray-700">
                                Minutes d'inactivité avant déclenchement
                              </label>
                              <input
                                type="number"
                                id="inactivityMinutes"
                                name="inactivityMinutes"
                                min="1"
                                max="120"
                                value={automation.conditions.inactivityMinutes}
                                onChange={handleInactivityChange}
                                className="mt-1 block w-32 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                              />
                            </div>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="border-t border-gray-200 pt-4">
                      <h4 className="text-md font-medium text-gray-700 mb-2">Actions</h4>
                      <ActionSelector
                        selectedActions={automation.actions}
                        onChange={handleActionSelection}
                      />
                      {errors.actions && (
                        <p className="mt-1 text-sm text-red-600">{errors.actions}</p>
                      )}
                    </div>

                    <div className="border-t border-gray-200 pt-4">
                      <h4 className="text-md font-medium text-gray-700 mb-2">Priorité</h4>
                      <PrioritySelector 
                        priority={automation.priority} 
                        onChange={handlePriorityChange} 
                      />
                      <p className="text-sm text-gray-500 mt-1">
                        Les automatisations avec une priorité plus élevée s'exécuteront en premier en cas de conflit.
                      </p>
                    </div>
                  </div>

                  <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
                    <button
                      type="button"
                      onClick={handleCancel}
                      className="inline-flex items-center px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                      Annuler
                    </button>
                    <button
                      type="submit"
                      className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md shadow-sm hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                    >
                      {isEditing ? 'Mettre à jour' : 'Créer'}
                    </button>
                  </div>
                </form>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
};

export default AutomationFormModal;