import TaskCard from './TaskCard';

interface Task {
  id: string;
  title: string;
  description?: string;
  priority?: string;
  due_date?: string;
  position: number;
}

interface ColumnProps {
  column: {
    id: string;
    name: string;
  };
  tasks: Task[];
  onTaskClick: (task: Task) => void;
  onAddTask: () => void;
}

export default function Column({ column, tasks, onTaskClick, onAddTask }: ColumnProps) {
  return (
    <div className="bg-gray-100 rounded-lg p-4 min-w-[300px] max-w-[300px]">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-gray-900">
          {column.name}
          <span className="ml-2 text-sm text-gray-500">({tasks.length})</span>
        </h3>
        <button
          onClick={onAddTask}
          className="text-gray-500 hover:text-gray-700"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 4v16m8-8H4"
            />
          </svg>
        </button>
      </div>
      <div className="space-y-3">
        {tasks
          .sort((a, b) => a.position - b.position)
          .map((task) => (
            <TaskCard
              key={task.id}
              task={task}
              onClick={() => onTaskClick(task)}
            />
          ))}
      </div>
    </div>
  );
}