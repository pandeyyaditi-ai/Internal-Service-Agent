import React from 'react';
import { BookOpen } from 'lucide-react';

export default function SourceReference({ sources }) {
  if (!sources || sources.length === 0) return null;

  return (
    <div className="sources-box">
      <div className="sources-box-title">
        <BookOpen size={14} />
        <span>Verified Knowledge Sources</span>
      </div>
      <div className="sources-list">
        {sources.map((source, idx) => (
          <div key={idx} className="source-item">
            <span>
              {source.title || source.document || source.source || 'IT Policy Base'}
            </span>
            {source.relevance && (
              <span className="source-badge">
                {Math.round(source.relevance * 100)}% match
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
