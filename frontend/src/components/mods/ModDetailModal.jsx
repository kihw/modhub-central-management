import React, { useState, useEffect } from "react";
import { Dialog, Transition } from "@headlessui/react";
import { Fragment } from "react";
import { XMarkIcon, PencilIcon, ClipboardDocumentCheckIcon } from "@heroicons/react/24/outline";
import Toggle from "../ui/Toggle";
import Slider from "../ui/Slider";
import ProcessList from "./ProcessList";
import ModRulesList from "./ModRulesList";
import ModSchedule from "./ModSchedule";
import { Tab } from "@headlessui/react";

function classNames(...classes) {
  return classes.filter(Boolean).join(" ");
}

const ModDetailModal = ({ isOpen, onClose, mod }) => {
  const [localMod, setLocalMod] = useState(mod);
  const [isEditing, setIsEditing] = useState(false);
  
  useEffect(() => {
    setLocalMod(mod);
  }, [mod]);

  const handleSave = () => {
    // TODO: Save mod to backend
    setIsEditing(false);
    onClose(localMod);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setLocalMod({ ...localMod, [name]: value });
  };

  const handleToggleChange = (key) => {
    setLocalMod({ ...localMod, [key]: !localMod[key] });
  };

  const handleSliderChange = (key, value) => {
    setLocalMod({ ...localMod, [key]: value });
  };

  const tabs = [
    { name: "Details", key: "details" },
    { name: "Rules", key: "rules" },
    { name: "Triggers", key: "triggers" },
    { name: "Schedule", key: "schedule" },
    { name: "Log", key: "log" },
  ];

  if (!mod) return null;

  return (
    <Transition appear show={isOpen} as={Fragment}>
      <Dialog as="div" className="relative z-50" onClose={() => onClose(null)}>
        <Transition.Child
          as={Fragment}
          enter="ease-out duration-300"
          enterFrom="opacity-0"
          enterTo="opacity-100"
          leave="ease-in duration-200"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <div className="fixed inset-0 bg-black/25" />
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
              <Dialog.Panel className="w-full max-w-4xl transform overflow-hidden rounded-xl bg-white dark:bg-gray-800 p-6 text-left align-middle shadow-xl transition-all">
                <div className="flex justify-between items-center mb-4">
                  <div className="flex items-center space-x-4">
                    <div className={`p-3 rounded-lg ${localMod.color}`}>
                      <localMod.icon className="h-6 w-6 text-white" aria-hidden="true" />
                    </div>
                    {isEditing ? (
                      <input
                        type="text"
                        name="name"
                        value={localMod.name}
                        onChange={handleInputChange}
                        className="text-xl font-semibold dark:bg-gray-700 dark:text-white rounded px-2 py-1"
                      />
                    ) : (
                      <Dialog.Title as="h3" className="text-xl font-semibold dark:text-white">
                        {localMod.name}
                      </Dialog.Title>
                    )}
                    <Toggle
                      enabled={localMod.active}
                      onChange={() => handleToggleChange("active")}
                      label=""
                    />
                  </div>
                  <div className="flex items-center space-x-2">
                    {isEditing ? (
                      <button
                        type="button"
                        onClick={handleSave}
                        className="rounded-md bg-emerald-500 p-1.5 text-white hover:bg-emerald-600"
                      >
                        <ClipboardDocumentCheckIcon className="h-5 w-5" />
                      </button>
                    ) : (
                      <button
                        type="button"
                        onClick={() => setIsEditing(true)}
                        className="rounded-md bg-blue-500 p-1.5 text-white hover:bg-blue-600"
                      >
                        <PencilIcon className="h-5 w-5" />
                      </button>
                    )}
                    <button
                      type="button"
                      onClick={() => onClose(null)}
                      className="rounded-md bg-gray-200 dark:bg-gray-700 p-1.5 text-gray-600 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600"
                    >
                      <XMarkIcon className="h-5 w-5" />
                    </button>
                  </div>
                </div>

                {isEditing ? (
                  <div className="mb-4">
                    <label className="block text-sm font-medium dark:text-gray-300 mb-1">Description</label>
                    <textarea
                      name="description"
                      value={localMod.description}
                      onChange={handleInputChange}
                      className="w-full rounded-md dark:bg-gray-700 dark:text-white text-sm p-2"
                      rows={3}
                    />
                  </div>
                ) : (
                  <p className="mb-4 text-sm dark:text-gray-300">{localMod.description}</p>
                )}

                <Tab.Group>
                  <Tab.List className="flex space-x-1 rounded-xl bg-gray-100 dark:bg-gray-700 p-1">
                    {tabs.map((tab) => (
                      <Tab
                        key={tab.key}
                        className={({ selected }) =>
                          classNames(
                            "w-full rounded-lg py-2.5 text-sm font-medium leading-5",
                            "ring-white/60 ring-offset-2 ring-offset-blue-400 focus:outline-none focus:ring-2",
                            selected
                              ? "bg-white dark:bg-gray-800 text-blue-600 dark:text-blue-400 shadow"
                              : "text-gray-600 dark:text-gray-400 hover:bg-white/[0.12] hover:text-gray-700"
                          )
                        }
                      >
                        {tab.name}
                      </Tab>
                    ))}
                  </Tab.List>
                  <Tab.Panels className="mt-4">
                    <Tab.Panel className="rounded-xl p-3">
                      <div className="space-y-4">
                        <div>
                          <h4 className="text-sm font-medium dark:text-gray-300 mb-2">Priority</h4>
                          <Slider
                            min={1}
                            max={10}
                            value={localMod.priority}
                            onChange={(value) => handleSliderChange("priority", value)}
                            disabled={!isEditing}
                          />
                          <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400 mt-1">
                            <span>Low</span>
                            <span>High</span>
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-2 gap-4">
                          <div>
                            <h4 className="text-sm font-medium dark:text-gray-300 mb-2">Options</h4>
                            <div className="space-y-2 bg-gray-50 dark:bg-gray-700 p-3 rounded-lg">
                              <div className="flex justify-between items-center">
                                <span className="text-sm dark:text-gray-300">Auto-start</span>
                                <Toggle
                                  enabled={localMod.autoStart}
                                  onChange={() => handleToggleChange("autoStart")}
                                  disabled={!isEditing}
                                />
                              </div>
                              <div className="flex justify-between items-center">
                                <span className="text-sm dark:text-gray-300">Notifications</span>
                                <Toggle
                                  enabled={localMod.notifications}
                                  onChange={() => handleToggleChange("notifications")}
                                  disabled={!isEditing}
                                />
                              </div>
                              <div className="flex justify-between items-center">
                                <span className="text-sm dark:text-gray-300">Log activities</span>
                                <Toggle
                                  enabled={localMod.logActivities}
                                  onChange={() => handleToggleChange("logActivities")}
                                  disabled={!isEditing}
                                />
                              </div>
                            </div>
                          </div>
                          
                          <div>
                            <h4 className="text-sm font-medium dark:text-gray-300 mb-2">Statistics</h4>
                            <div className="space-y-2 bg-gray-50 dark:bg-gray-700 p-3 rounded-lg">
                              <div className="flex justify-between">
                                <span className="text-sm dark:text-gray-300">Times activated</span>
                                <span className="text-sm font-medium dark:text-gray-200">{localMod.stats?.timesActivated || 0}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-sm dark:text-gray-300">Last activated</span>
                                <span className="text-sm font-medium dark:text-gray-200">{localMod.stats?.lastActivated || 'Never'}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-sm dark:text-gray-300">Total time active</span>
                                <span className="text-sm font-medium dark:text-gray-200">{localMod.stats?.totalTimeActive || '0h'}</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </Tab.Panel>
                    
                    <Tab.Panel className="rounded-xl p-3">
                      <ModRulesList rules={localMod.rules} editable={isEditing} onChange={(rules) => setLocalMod({...localMod, rules})} />
                    </Tab.Panel>
                    
                    <Tab.Panel className="rounded-xl p-3">
                      <ProcessList 
                        processes={localMod.processes} 
                        editable={isEditing} 
                        onChange={(processes) => setLocalMod({...localMod, processes})} 
                      />
                    </Tab.Panel>
                    
                    <Tab.Panel className="rounded-xl p-3">
                      <ModSchedule 
                        schedule={localMod.schedule} 
                        editable={isEditing} 
                        onChange={(schedule) => setLocalMod({...localMod, schedule})} 
                      />
                    </Tab.Panel>
                    
                    <Tab.Panel className="rounded-xl p-3">
                      <div className="max-h-80 overflow-y-auto space-y-2">
                        {localMod.logs && localMod.logs.length > 0 ? (
                          localMod.logs.map((log, index) => (
                            <div key={index} className="text-sm p-2 border-l-4 border-blue-400 bg-gray-50 dark:bg-gray-700 dark:text-gray-300">
                              <div className="flex justify-between">
                                <span className="font-medium">{log.action}</span>
                                <span className="text-xs text-gray-500 dark:text-gray-400">{log.timestamp}</span>
                              </div>
                              <p className="text-gray-600 dark:text-gray-400 text-xs mt-1">{log.details}</p>
                            </div>
                          ))
                        ) : (
                          <div className="text-center py-4 text-gray-500 dark:text-gray-400">
                            No activity logs available
                          </div>
                        )}
                      </div>
                    </Tab.Panel>
                  </Tab.Panels>
                </Tab.Group>

                <div className="mt-6 flex justify-end space-x-3">
                  <button
                    type="button"
                    className="inline-flex justify-center rounded-md border border-transparent bg-red-100 px-4 py-2 text-sm font-medium text-red-900 hover:bg-red-200 focus:outline-none"
                  >
                    Delete Mod
                  </button>
                  <button
                    type="button"
                    className="inline-flex justify-center rounded-md border border-transparent bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 focus:outline-none"
                    onClick={isEditing ? handleSave : () => onClose(null)}
                  >
                    {isEditing ? 'Save Changes' : 'Close'}
                  </button>
                </div>
              </Dialog.Panel>
            </Transition.Child>
          </div>
        </div>
      </Dialog>
    </Transition>
  );
};

export default ModDetailModal;