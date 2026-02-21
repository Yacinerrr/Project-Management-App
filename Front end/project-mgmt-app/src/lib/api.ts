const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

export class ApiClient {
  private baseUrl: string;
  private token: string | null;

  constructor() {
    this.baseUrl = API_URL;
    this.token = null;
  }

  setToken(token: string) {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('token', token);
    }
  }

  getToken(): string | null {
    if (typeof window !== 'undefined' && !this.token) {
      this.token = localStorage.getItem('token');
    }
    return this.token;
  }

  clearToken() {
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token');
    }
  }

  private async request(endpoint: string, options: RequestInit = {}) {
    const token = this.getToken();
    
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
      throw new Error(error.detail || 'Request failed');
    }

    if (response.status === 204) {
      return null;
    }

    return response.json();
  }

  // Auth
  async register(email: string, name: string, password: string) {
    return this.request('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, name, password }),
    });
  }

  async login(email: string, password: string) {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${this.baseUrl}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();
    this.setToken(data.access_token);
    return data;
  }

  async getCurrentUser() {
    return this.request('/auth/me');
  }

  // Projects
  async getProjects() {
    return this.request('/projects');
  }

  async createProject(name: string, description?: string) {
    return this.request('/projects', {
      method: 'POST',
      body: JSON.stringify({ name, description }),
    });
  }

  async getProject(id: string) {
    return this.request(`/projects/${id}`);
  }

  async updateProject(id: string, name: string, description?: string) {
    return this.request(`/projects/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ name, description }),
    });
  }

  async deleteProject(id: string) {
    return this.request(`/projects/${id}`, {
      method: 'DELETE',
    });
  }

  // Boards
  async getProjectBoards(projectId: string) {
    return this.request(`/boards/project/${projectId}`);
  }

  async createBoard(projectId: string, name: string, position: number) {
    return this.request('/boards', {
      method: 'POST',
      body: JSON.stringify({ project_id: projectId, name, position }),
    });
  }

  // Columns
  async getBoardColumns(boardId: string) {
    return this.request(`/columns/board/${boardId}`);
  }

  async createColumn(boardId: string, name: string, position: number) {
    return this.request('/columns', {
      method: 'POST',
      body: JSON.stringify({ board_id: boardId, name, position }),
    });
  }

  // Tasks
  async getColumnTasks(columnId: string) {
    return this.request(`/tasks/column/${columnId}`);
  }

  async createTask(data: {
    title: string;
    description?: string;
    column_id: string;
    position: number;
    priority?: string;
    due_date?: string;
    assignee_id?: string;
  }) {
    return this.request('/tasks', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updateTask(id: string, data: any) {
    return this.request(`/tasks/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async moveTask(id: string, columnId: string, position: number) {
    return this.request(`/tasks/${id}/move?new_column_id=${columnId}&new_position=${position}`, {
      method: 'POST',
    });
  }

  async deleteTask(id: string) {
    return this.request(`/tasks/${id}`, {
      method: 'DELETE',
    });
  }

  // Comments
  async getTaskComments(taskId: string) {
    return this.request(`/comments/task/${taskId}`);
  }

  async createComment(taskId: string, content: string) {
    return this.request('/comments', {
      method: 'POST',
      body: JSON.stringify({ task_id: taskId, content }),
    });
  }
}

export const api = new ApiClient();