interface TaskCardProps {
  task: {
    id: string;
    title: string;
    description?: string;
    priority?: string;
    due_date?: string;
  };
  onClick: () => void;
}

export default function TaskCard({ task, onClick }: TaskCardProps) {
  const priorityColors: { [key: string]: string } = {
    high: 'border-l-4 border-red-500',
    medium: 'border-l-4 border-yellow-500',
    low: 'border-l-4 border-green-500',
  };

  return (
    <div
      onClick={onClick}
      className={`bg-white p-4 rounded-lg shadow hover:shadow-md transition-shadow cursor-pointer ${
        task.priority ? priorityColors[task.priority] : ''
      }`}
    >
      <h4 className="font-medium text-gray-900 mb-2">{task.title}</h4>
      {task.description && (
        <p className="text-sm text-gray-600 mb-2 line-clamp-2">
          {task.description}
        </p>
      )}
      <div className="flex items-center justify-between text-xs text-gray-500">
        {task.priority && (
          <span
            className={`px-2 py-1 rounded ${
              task.priority === 'high'
                ? 'bg-red-100 text-red-800'
                : task.priority === 'medium'
                ? 'bg-yellow-100 text-yellow-800'
                : 'bg-green-100 text-green-800'
            }`}
          >
            {task.priority}
          </span>
        )}
        {task.due_date && (
          <span>{new Date(task.due_date).toLocaleDateString()}</span>
        )}
      </div>
    </div>
  );
}