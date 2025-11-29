import React, { useState, useEffect } from 'react';
import './StoryWizard.css';

const STEPS = [
  { id: 1, name: 'Initial Book Spec', file: '1_initial_book_spec.txt' },
  { id: 2, name: 'Enhanced Book Spec', file: '2_enhanced_book_spec.txt' },
  { id: 3, name: 'Initial Plot', file: '3_initial_plot.json' },
  { id: 4, name: 'Enhanced Plot', file: '4_enhanced_plot.json' },
  { id: 5, name: 'Scene Plan', file: '5_scene_plan.json' }
];

function StoryWizard({ session, onComplete }) {
  // Determine the current step based on what files exist
  const getInitialStep = (sessionPlans) => {
    const plans = sessionPlans || {};
    // Find the last completed step
    for (let i = STEPS.length; i >= 1; i--) {
      const stepFile = STEPS.find(s => s.id === i)?.file;
      if (stepFile && plans[stepFile]) {
        // If this step exists, continue from here (stay on this step)
        return i;
      }
    }
    // If no files exist, start at step 1
    return 1;
  };

  const [currentStep, setCurrentStep] = useState(() => getInitialStep(session.plans));
  const [content, setContent] = useState('');
  const [originalContent, setOriginalContent] = useState('');
  const [hasChanges, setHasChanges] = useState(false);
  const [saving, setSaving] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);

  // Recalculate step when session changes (e.g., after reload)
  useEffect(() => {
    const newStep = getInitialStep(session.plans);
    if (newStep !== currentStep && !generating) {
      setCurrentStep(newStep);
    }
  }, [session.plans]);

  // Load content for current step
  useEffect(() => {
    const stepInfo = STEPS.find(s => s.id === currentStep);
    if (!stepInfo) return;

    // Try to load from session plans
    const planData = session.plans?.[stepInfo.file];
    
    if (planData) {
      const text = typeof planData === 'string' 
        ? planData 
        : JSON.stringify(planData, null, 2);
      setContent(text);
      setOriginalContent(text);
      setHasChanges(false);
    } else {
      // No data yet for this step
      setContent('');
      setOriginalContent('');
    }
  }, [currentStep, session]);

  const handleContentChange = (e) => {
    setContent(e.target.value);
    setHasChanges(e.target.value !== originalContent);
  };

  const saveChanges = async () => {
    setSaving(true);
    setError(null);

    try {
      const stepInfo = STEPS.find(s => s.id === currentStep);
      
      const response = await fetch(
        `http://localhost:5001/api/session/${session.id}/save-plan`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            filename: stepInfo.file,
            content: content
          })
        }
      );

      if (!response.ok) {
        throw new Error('Failed to save');
      }

      setOriginalContent(content);
      setHasChanges(false);
      alert('✓ Saved!');
    } catch (err) {
      setError('Error saving: ' + err.message);
    } finally {
      setSaving(false);
    }
  };

  const generateNext = async () => {
    if (hasChanges) {
      alert('Please save your changes first!');
      return;
    }

    setGenerating(true);
    setError(null);

    try {
      const response = await fetch(
        `http://localhost:5001/api/session/${session.id}/generate-next`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ current_step: currentStep })
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Generation failed');
      }

      // Move to next step and set the generated content
      setCurrentStep(data.next_step);
      setContent(data.result || '');
      setOriginalContent(data.result || '');
      setHasChanges(false);

      // Refresh parent's session data so sidebar updates
      if (onComplete) {
        onComplete();
      }

      // If this was the last step, notify parent
      if (data.next_step > 5) {
        if (onComplete) onComplete();
      }
    } catch (err) {
      setError('Error generating: ' + err.message);
    } finally {
      setGenerating(false);
    }
  };

  const currentStepInfo = STEPS.find(s => s.id === currentStep);
  const isFirstStep = currentStep === 1;
  const isLastStep = currentStep === 5;

  return (
    <div className="story-wizard">
      <div className="wizard-header">
        <h2>📝 Story Planning Wizard</h2>
        <div className="step-indicator">
          Step {currentStep} of {STEPS.length}: {currentStepInfo?.name}
        </div>
        <div className="progress-bar">
          {STEPS.map(step => (
            <div
              key={step.id}
              className={`progress-step ${step.id < currentStep ? 'completed' : ''} ${step.id === currentStep ? 'current' : ''}`}
              title={step.name}
            />
          ))}
        </div>
      </div>

      <div className="wizard-content">
        <textarea
          className="plan-editor"
          value={content}
          onChange={handleContentChange}
          disabled={generating}
          placeholder={generating ? 'Generating...' : 'Edit your plan here...'}
        />
      </div>

      {error && (
        <div className="error-message">
          ⚠️ {error}
        </div>
      )}

      <div className="wizard-actions">
        <div className="action-left">
          {hasChanges && (
            <span className="unsaved-indicator">● Unsaved changes</span>
          )}
        </div>
        
        <div className="action-right">
          <button
            className="save-btn"
            onClick={saveChanges}
            disabled={!hasChanges || saving || generating}
          >
            {saving ? '💾 Saving...' : '💾 Save Changes'}
          </button>

          <button
            className="next-btn"
            onClick={generateNext}
            disabled={hasChanges || generating || !content}
          >
            {generating ? (
              '⏳ Generating...'
            ) : isLastStep ? (
              '🚀 Generate Full Story'
            ) : (
              `→ Next: ${STEPS.find(s => s.id === currentStep + 1)?.name}`
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

export default StoryWizard;


