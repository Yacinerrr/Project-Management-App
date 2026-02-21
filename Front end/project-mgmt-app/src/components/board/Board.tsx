'use client';

import { useState, useEffect } from 'react';
import Column from './Column';
import { api } from '@/src/lib/api';

interface BoardProps {
  boardId: string;
}

interface Task {
  id: string;
  title: string;
  description?: string;
  priority?: string;
  due_date?: string;
  position: number;
  column_id: string;
}

interface BoardColumn {
  id: string;
  name: string;
  position: number;
}

export default function Board({ boardId }: BoardProps) {
  const [columns, setColumns] = useState<BoardColumn[]>([]);
  const [tasks, setTasks] = useState<{ [columnId: string]: Task[] }>({});
  const [loading, setLoading] = useState(true);
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [selectedColumn, setSelectedColumn] = useState<string | null>(null);
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [newTaskDescription, setNewTaskDescription] = useState('');
  const [newTaskPriority, setNewTaskPriority] = useState('');

  useEffect(() => {
    loadBoard();
  }, [boardId]);

  const loadBoard = async () => {
    try {
      const columnsData = await api.getBoardColumns(boardId);
      setColumns(columnsData.sort((a: BoardColumn, b: BoardColumn) => a.position - b.position));

      const tasksData: { [columnId: string]: Task[] } = {};
      await Promise.all(
        columnsData.map(async (column: BoardColumn) => {
          const columnTasks = await api.getColumnTasks(column.id);
          tasksData[column.id] = columnTasks;
        })
      );
      setTasks(tasksData);
    } catch (err) {
      console.error('Failed to load board:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddTask = (columnId: string) => {
    setSelectedColumn(columnId);
    setShowTaskModal(true);
  };

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedColumn) return;

    try {
      const columnTasks = tasks[selectedColumn] || [];
      const position = columnTasks.length;

      await api.createTask({
        title: newTaskTitle,
        description: newTaskDescription,
        column_id: selectedColumn,
        position,
        priority: newTaskPriority || undefined,
      });

      setShowTaskModal(false);
      setNewTaskTitle('');
      setNewTaskDescription('');
      setNewTaskPriority('');
      setSelectedColumn(null);
      loadBoard();
    } catch (err) {
      console.error('Failed to create task:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-gray-600">Loading board...</p>
      </div>
    );
  }

  return (
    <div className="relative">
      <div className="flex gap-4 overflow-x-auto pb-4">
        {columns.map((column) => (
          <Column
            key={column.id}
            column={column}
            tasks={tasks[column.id] || []}
            onTaskClick={(task) => console.log('Task clicked:', task)}
            onAddTask={() => handleAddTask(column.id)}
          />
        ))}
      </div>

      {/* Create Task Modal */}
      {showTaskModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium leading-6 text-gray-900 mb-4">
                Create New Task
              </h3>
              <form onSubmit={handleCreateTask}>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Title
                  </label>
                  <input
                    type="text"
                    required
                    value={newTaskTitle}
                    onChange={(e) => setNewTaskTitle(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter task title"
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <textarea
                    value={newTaskDescription}
                    onChange={(e) => setNewTaskDescription(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Enter task description"
                    rows={3}
                  />
                </div>
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Priority
                  </label>
                  <select
                    value={newTaskPriority}
                    onChange={(e) => setNewTaskPriority(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="">No priority</option>
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                </div>
                <div className="flex justify-end gap-3">
                  <button
                    type="button"
                    onClick={() => {
                      setShowTaskModal(false);
                      setNewTaskTitle('');
                      setNewTaskDescription('');
                      setNewTaskPriority('');
                      setSelectedColumn(null);
                    }}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
                  >
                    Create
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}