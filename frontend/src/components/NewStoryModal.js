import React, { useState } from 'react';
import './NewStoryModal.css';

function NewStoryModal({ onClose, onSubmit }) {
  const [topic, setTopic] = useState('');
  const [length, setLength] = useState('medium');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!topic.trim()) {
      alert('Please enter a topic!');
      return;
    }

    setIsSubmitting(true);
    
    try {
      // Create abort controller for timeout (2 minutes for GPT-5 API)
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 120000); // 2 minutes
      
      const response = await fetch('http://localhost:5001/api/generate/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topic, length }),
        signal: controller.signal
      });

      clearTimeout(timeoutId);
      const data = await response.json();
      
      if (response.ok) {
        alert(`✨ Story created! Opening session ${data.session_id}...`);
        onSubmit(data.session_id); // Pass session ID back
        onClose();
      } else {
        alert(`Error: ${data.error}`);
        setIsSubmitting(false);
      }
    } catch (error) {
      if (error.name === 'AbortError') {
        alert('⏱️ Generation is taking longer than expected. Please wait and refresh the page in a moment.');
      } else {
        alert(`Error: ${error.message}`);
      }
      setIsSubmitting(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content new-story-modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Create New Story</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>
        
        <form onSubmit={handleSubmit} className="story-form">
          <div className="form-group">
            <label htmlFor="topic">Story Topic</label>
            <textarea
              id="topic"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., a detective solving a mystery in a haunted mansion"
              rows="3"
              disabled={isSubmitting}
            />
          </div>

          <div className="form-group">
            <label htmlFor="length">Story Length</label>
            <select
              id="length"
              value={length}
              onChange={(e) => setLength(e.target.value)}
              disabled={isSubmitting}
            >
              <option value="short">Short (~5 min, 1000 words)</option>
              <option value="medium">Medium (~10 min, 2000 words)</option>
              <option value="long">Long (~15 min, 3000 words)</option>
            </select>
          </div>

          <div className="form-actions">
            <button
              type="button"
              onClick={onClose}
              className="cancel-btn"
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="submit-btn"
              disabled={isSubmitting}
            >
              {isSubmitting ? '🎨 Generating (30-60s)...' : '✨ Generate Story'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default NewStoryModal;

