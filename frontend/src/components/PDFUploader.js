import React, { useState, useRef } from 'react';
import axios from 'axios';

export default function PDFUploader({ onUpload }) {
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState('');
  const inputRef = useRef();

  const handleFile = async (file) => {
    if (!file) return;
    if (file.type !== 'application/pdf') {
      setError('Only PDF files are supported.');
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      setError('File size must be under 10MB.');
      return;
    }

    setError('');
    setUploading(true);
    setProgress(0);

    const formData = new FormData();
    formData.append('pdf', file);

    try {
      const res = await axios.post('/api/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        onUploadProgress: (e) => {
          setProgress(Math.round((e.loaded * 100) / e.total));
        },
      });
      onUpload(res.data);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to upload PDF. Please try again.');
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    handleFile(file);
  };

  return (
    <div>
      {error && <div className="error-bar">{error}</div>}

      <div
        className={`upload-zone ${dragging ? 'drag' : ''}`}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        onClick={() => !uploading && inputRef.current?.click()}
      >
        <input
          ref={inputRef}
          type="file"
          accept=".pdf"
          onChange={(e) => handleFile(e.target.files[0])}
          disabled={uploading}
        />
        <div className="upload-icon">📄</div>
        <div className="upload-title">{uploading ? 'Processing PDF...' : 'Upload a PDF'}</div>
        <div className="upload-sub">{uploading ? 'Extracting text...' : 'Drag & drop or click to browse · Max 10MB'}</div>

        {uploading && (
          <div className="upload-progress" onClick={(e) => e.stopPropagation()}>
            <div className="progress-bar-bg">
              <div className="progress-bar-fill" style={{ width: `${progress}%` }} />
            </div>
            <div className="upload-status">{progress < 100 ? `Uploading... ${progress}%` : 'Extracting text from PDF...'}</div>
          </div>
        )}
      </div>
    </div>
  );
}
