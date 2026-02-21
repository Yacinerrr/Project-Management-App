'use client';

import { useState, useEffect, use } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/src/lib/api';
import Board from '@/src/components/board/Board';

interface PageProps {
  params: Promise<{ id: string }>;
}

export default function ProjectDetailPage({ params }: PageProps) {
  const { id } = use(params);
  const router = useRouter();
  const [project, setProject] = useState<any>(null);
  const [boards, setBoards] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProject();
  }, [id]);

  const loadProject = async () => {
    try {
      const [projectData, boardsData] = await Promise.all([
        api.getProject(id),
        api.getProjectBoards(id),
      ]);
      setProject(projectData);
      setBoards(boardsData);

      if (boardsData.length === 0) {
        await createDefaultBoard();
      }
    } catch (err) {
      console.error('Failed to load project:', err);
      router.push('/projects');
    } finally {
      setLoading(false);
    }
  };

  const createDefaultBoard = async () => {
    try {
      const board = await api.createBoard(id, 'Main Board', 0);
      
      await Promise.all([
        api.createColumn(board.id, 'To Do', 0),
        api.createColumn(board.id, 'In Progress', 1),
        api.createColumn(board.id, 'Done', 2),
      ]);

      loadProject();
    } catch (err) {
      console.error('Failed to create default board:', err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-gray-600">Loading...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => router.push('/projects')}
                className="text-gray-600 hover:text-gray-900"
              >
                ← Back
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  {project?.name}
                </h1>
                {project?.description && (
                  <p className="text-sm text-gray-600 mt-1">
                    {project.description}
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {boards.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-500">Creating your board...</p>
          </div>
        ) : (
          <Board boardId={boards[0].id} />
        )}
      </main>
    </div>
  );
}