import React, { useState } from 'react';
import { taskAPI } from '../services/api';
import './TaskCard.css';

function TaskCard({ task, onTaskUpdated, onTaskDeleted }) {
  const [isEditing, setIsEditing] = useState(false);
  const [title, setTitle] = useState(task.title);
  const [description, setDescription] = useState(task.description || '');
  const [status, setStatus] = useState(task.status);
  const [isCompleted, setIsCompleted] = useState(task.is_completed);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleUpdate = async () => {
    setLoading(true);
    setError('');
    try {
      await taskAPI.updateTask(task.id, title, description, status, isCompleted);
      setIsEditing(false);
      onTaskUpdated();
    } catch (err) {
      setError('Failed to update task');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      setLoading(true);
      try {
        await taskAPI.deleteTask(task.id);
        onTaskDeleted();
      } catch (err) {
        setError('Failed to delete task');
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
  };

  if (isEditing) {
    return (
      <div className="task-card task-card-edit">
        <div className="task-edit-form">
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Task title"
            className="task-input"
          />
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Task description"
            className="task-textarea"
          />
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="task-select"
          >
            <option value="TODO">TODO</option>
            <option value="IN_PROGRESS">IN PROGRESS</option>
            <option value="DONE">DONE</option>
          </select>
          <label className="task-checkbox">
            <input
              type="checkbox"
              checked={isCompleted}
              onChange={(e) => setIsCompleted(e.target.checked)}
            />
            Mark as completed
          </label>
          {error && <p className="error-message">{error}</p>}
          <div className="task-edit-actions">
            <button
              type="button"
              onClick={handleUpdate}
              disabled={loading}
              className="btn btn-primary"
            >
              {loading ? 'Saving...' : 'Save'}
            </button>
            <button
              type="button"
              onClick={() => setIsEditing(false)}
              className="btn btn-secondary"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`task-card status-${status.toLowerCase()}`}>
      <div className="task-header">
        <h3>{title}</h3>
        <span className={`task-status status-${status.toLowerCase()}`}>
          {status.replace('_', ' ')}
        </span>
      </div>
      {description && <p className="task-description">{description}</p>}
      <div className="task-meta">
        <span className="task-date">
          {new Date(task.created_at).toLocaleDateString()}
        </span>
        {isCompleted && <span className="task-completed">✓ Completed</span>}
      </div>
      <div className="task-actions">
        <button
          type="button"
          onClick={() => setIsEditing(true)}
          className="btn btn-small btn-primary"
        >
          Edit
        </button>
        <button
          type="button"
          onClick={handleDelete}
          disabled={loading}
          className="btn btn-small btn-danger"
        >
          Delete
        </button>
      </div>
    </div>
  );
}

export default TaskCard;
