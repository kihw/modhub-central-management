import React, { useState } from "react";
import { Draggable } from "react-beautiful-dnd";
import {
  FaEdit,
  FaTrash,
  FaPause,
  FaPlay,
  FaChevronDown,
  FaChevronUp,
} from "react-icons/fa";
import { GiAutoRepair } from "react-icons/gi";
import { Badge, Tooltip } from "../../ui";
import { formatDistance } from "date-fns";

const AutomationCard = ({
  automation,
  index,
  onEdit,
  onDelete,
  onToggleActive,
  systemProcesses = [],
}) => {
  const [expanded, setExpanded] = useState(false);

  const isActive = automation.active;
  const isRunning = automation.isRunning;

  const lastTriggered = automation.lastTriggered
    ? formatDistance(new Date(automation.lastTriggered), new Date(), {
        addSuffix: true,
      })
    : "Never";

  const rulesMetCount =
    automation.conditions?.filter((condition) => {
      // Simple check for process conditions
      if (condition.type === "process" && condition.operation === "running") {
        return systemProcesses.some((proc) => proc.name === condition.value);
      }
      return false; // Other condition types would need specific checkers
    }).length || 0;

  const totalRules = automation.conditions?.length || 0;

  return (
    <Draggable draggableId={automation.id} index={index}>
      {(provided, snapshot) => (
        <div
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          className={`mb-4 rounded-lg shadow-md overflow-hidden transition-all duration-200 ${
            snapshot.isDragging ? "shadow-lg scale-102" : ""
          } ${
            isActive
              ? "bg-white dark:bg-gray-800"
              : "bg-gray-100 dark:bg-gray-900 opacity-75"
          }`}
        >
          <div className="p-4">
            <div className="flex justify-between items-center">
              <div className="flex items-center">
                <GiAutoRepair
                  className={`text-xl mr-2 ${
                    isActive ? "text-blue-500" : "text-gray-400"
                  }`}
                />
                <h3 className="font-medium text-lg">{automation.name}</h3>
                <div className="ml-2 flex gap-1">
                  {isActive && (
                    <Badge color={isRunning ? "green" : "gray"}>
                      {isRunning ? "Running" : "Waiting"}
                    </Badge>
                  )}
                  {automation.priority && (
                    <Tooltip content={`Priority: ${automation.priority}`}>
                      <Badge color="purple">P{automation.priority}</Badge>
                    </Tooltip>
                  )}
                </div>
              </div>

              <div className="flex space-x-2">
                <button
                  onClick={() => onToggleActive(automation.id)}
                  className={`p-2 rounded-full ${
                    isActive
                      ? "text-yellow-500 hover:bg-yellow-100 dark:hover:bg-yellow-900"
                      : "text-green-500 hover:bg-green-100 dark:hover:bg-green-900"
                  }`}
                >
                  {isActive ? <FaPause /> : <FaPlay />}
                </button>
                <button
                  onClick={() => onEdit(automation)}
                  className="p-2 rounded-full text-blue-500 hover:bg-blue-100 dark:hover:bg-blue-900"
                >
                  <FaEdit />
                </button>
                <button
                  onClick={() => onDelete(automation.id)}
                  className="p-2 rounded-full text-red-500 hover:bg-red-100 dark:hover:bg-red-900"
                >
                  <FaTrash />
                </button>
                <button
                  onClick={() => setExpanded(!expanded)}
                  className="p-2 rounded-full text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  {expanded ? <FaChevronUp /> : <FaChevronDown />}
                </button>
              </div>
            </div>

            <div className="mt-2 text-sm text-gray-600 dark:text-gray-400">
              <p>{automation.description || "No description provided"}</p>
              <div className="mt-1 flex justify-between">
                <div>
                  <span>Conditions met: </span>
                  <span
                    className={`font-medium ${
                      rulesMetCount === 0
                        ? "text-red-500"
                        : rulesMetCount === totalRules
                        ? "text-green-500"
                        : "text-yellow-500"
                    }`}
                  >
                    {rulesMetCount}/{totalRules}
                  </span>
                </div>
                <div>Last triggered: {lastTriggered}</div>
              </div>
            </div>
          </div>

          {expanded && (
            <div className="px-4 pb-4 pt-0 border-t border-gray-200 dark:border-gray-700">
              <div className="mt-3">
                <h4 className="font-medium mb-2">Conditions</h4>
                {automation.conditions && automation.conditions.length > 0 ? (
                  <ul className="space-y-1 text-sm">
                    {automation.conditions.map((condition, idx) => {
                      const isConditionMet =
                        condition.type === "process" &&
                        systemProcesses.some(
                          (proc) => proc.name === condition.value
                        );

                      return (
                        <li
                          key={idx}
                          className={`py-1 px-2 rounded ${
                            isConditionMet
                              ? "bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200"
                              : "bg-gray-100 dark:bg-gray-800"
                          }`}
                        >
                          {condition.type === "process" && (
                            <>
                              Process <b>{condition.value}</b> is{" "}
                              {condition.operation}
                            </>
                          )}
                          {condition.type === "time" && (
                            <>
                              Time is {condition.operation}{" "}
                              <b>{condition.value}</b>
                            </>
                          )}
                          {condition.type === "custom" && (
                            <>{condition.description || "Custom condition"}</>
                          )}
                        </li>
                      );
                    })}
                  </ul>
                ) : (
                  <p className="text-sm text-gray-500 italic">
                    No conditions defined
                  </p>
                )}
              </div>

              <div className="mt-3">
                <h4 className="font-medium mb-2">Actions</h4>
                {automation.actions && automation.actions.length > 0 ? (
                  <ul className="space-y-1 text-sm">
                    {automation.actions.map((action, idx) => (
                      <li
                        key={idx}
                        className="py-1 px-2 rounded bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-200"
                      >
                        {action.type === "mod" && (
                          <>
                            Activate mod <b>{action.target}</b>
                          </>
                        )}
                        {action.type === "setting" && (
                          <>
                            Set <b>{action.target}</b> to <b>{action.value}</b>
                          </>
                        )}
                        {action.type === "custom" && (
                          <>{action.description || "Custom action"}</>
                        )}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-gray-500 italic">
                    No actions defined
                  </p>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </Draggable>
  );
};

export default AutomationCard;
