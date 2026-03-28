import React, { useState, useEffect, useCallback } from 'react';
import { taskAPI } from '../services/api';
import TaskCard from '../components/TaskCard';
import './Dashboard.css';

const PAGE_SIZE = 10;

function Dashboard() {
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [statusFilter, setStatusFilter] = useState('');
  const [pagination, setPagination] = useState({
    skip: 0,
    limit: PAGE_SIZE,
    total: 0,
  });

  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    status: 'TODO',
  });

  const fetchTasks = useCallback(
    async (skip = 0) => {
      setLoading(true);
      setError('');
      try {
        const response = await taskAPI.getTasks(skip, PAGE_SIZE, statusFilter);
        setTasks(response.data.tasks);
        setPagination((prev) => ({
          ...prev,
          skip,
          limit: PAGE_SIZE,
          total: response.data.total,
        }));
      } catch (err) {
        setError('Failed to load tasks');
        console.error(err);
      } finally {
        setLoading(false);
      }
    },
    [statusFilter]
  );

  useEffect(() => {
    fetchTasks(0);
  }, [statusFilter, fetchTasks]);

  const handleCreateTask = async (e) => {
    e.preventDefault();
    setError('');

    if (!newTask.title.trim()) {
      setError('Task title is required');
      return;
    }

    try {
      await taskAPI.createTask(
        newTask.title,
        newTask.description,
        newTask.status
      );
      setNewTask({ title: '', description: '', status: 'TODO' });
      setShowForm(false);
      fetchTasks(0);
    } catch (err) {
      setError('Failed to create task');
      console.error(err);
    }
  };

  const handleTaskUpdated = () => {
    fetchTasks(pagination.skip);
  };

  const handleTaskDeleted = () => {
    fetchTasks(pagination.skip);
  };

  const totalPages = Math.ceil(pagination.total / pagination.limit) || 1;
  const currentPage = pagination.skip / pagination.limit + 1;

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>📋 Your Tasks</h1>
        <p className="welcome-message">Welcome, {user.username}! 👋</p>
      </div>

      <div className="dashboard-controls">
        <div className="filter-section">
          <label htmlFor="status-filter">Filter by Status:</label>
          <select
            id="status-filter"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="filter-select"
          >
            <option value="">All Tasks</option>
            <option value="TODO">TODO</option>
            <option value="IN_PROGRESS">IN PROGRESS</option>
            <option value="DONE">DONE</option>
          </select>
        </div>

        <button
          type="button"
          onClick={() => setShowForm(!showForm)}
          className="btn-new-task"
        >
          {showForm ? '✕ Cancel' : '+ New Task'}
        </button>
      </div>

      {error && <div className="error-box">{error}</div>}

      {showForm && (
        <div className="new-task-form-container">
          <form onSubmit={handleCreateTask} className="new-task-form">
            <h2>Create New Task</h2>
            <div className="form-group">
              <label htmlFor="task-title">Title *</label>
              <input
                type="text"
                id="task-title"
                value={newTask.title}
                onChange={(e) =>
                  setNewTask((prev) => ({
                    ...prev,
                    title: e.target.value,
                  }))
                }
                placeholder="Enter task title"
                className="form-input"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="task-description">Description</label>
              <textarea
                id="task-description"
                value={newTask.description}
                onChange={(e) =>
                  setNewTask((prev) => ({
                    ...prev,
                    description: e.target.value,
                  }))
                }
                placeholder="Enter task description (optional)"
                className="form-textarea"
              />
            </div>

            <div className="form-group">
              <label htmlFor="task-status">Status</label>
              <select
                id="task-status"
                value={newTask.status}
                onChange={(e) =>
                  setNewTask((prev) => ({
                    ...prev,
                    status: e.target.value,
                  }))
                }
                className="form-select"
              >
                <option value="TODO">TODO</option>
                <option value="IN_PROGRESS">IN PROGRESS</option>
                <option value="DONE">DONE</option>
              </select>
            </div>

            <button type="submit" className="btn-submit">
              Create Task
            </button>
          </form>
        </div>
      )}

      <div className="tasks-container">
        {loading ? (
          <div className="loading">Loading tasks...</div>
        ) : tasks.length === 0 ? (
          <div className="empty-state">
            <p>No tasks found. Create your first task to get started! 🚀</p>
          </div>
        ) : (
          <>
            <div className="tasks-list">
              {tasks.map((task) => (
                <TaskCard
                  key={task.id}
                  task={task}
                  onTaskUpdated={handleTaskUpdated}
                  onTaskDeleted={handleTaskDeleted}
                />
              ))}
            </div>

            {totalPages > 1 && (
              <div className="pagination">
                <button
                  type="button"
                  onClick={() =>
                    fetchTasks(Math.max(0, pagination.skip - pagination.limit))
                  }
                  disabled={currentPage === 1}
                  className="pagination-btn"
                >
                  ← Previous
                </button>
                <span className="pagination-info">
                  Page {currentPage} of {totalPages}
                </span>
                <button
                  type="button"
                  onClick={() =>
                    fetchTasks(pagination.skip + pagination.limit)
                  }
                  disabled={currentPage === totalPages}
                  className="pagination-btn"
                >
                  Next →
                </button>
              </div>
            )}
          </>
        )}
      </div>

      <div className="dashboard-stats">
        <div className="stat-card">
          <span className="stat-number">{tasks.length}</span>
          <span className="stat-label">Tasks This Page</span>
        </div>
        <div className="stat-card">
          <span className="stat-number">{pagination.total}</span>
          <span className="stat-label">Total Tasks</span>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
