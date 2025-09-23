"use client";

import React, { useState } from "react";
import { ExternalLink, ChevronDown, ChevronRight, BookOpen } from "lucide-react";
import { Button } from "@/components/ui/button";
import styles from "./ReferencesDisplay.module.scss";

interface Reference {
  url: string;
  title: string;
  score?: number;
  published_date?: string;
}

interface ReferencesDisplayProps {
  references: Reference[];
  title?: string;
}

export const ReferencesDisplay = React.memo<ReferencesDisplayProps>(
  ({ references, title = "References" }) => {
    const [isExpanded, setIsExpanded] = useState(false);

    if (!references || references.length === 0) {
      return null;
    }

    const toggleExpanded = () => {
      setIsExpanded(!isExpanded);
    };

    const formatDate = (dateString: string | null | undefined) => {
      if (!dateString) return null;
      try {
        return new Date(dateString).toLocaleDateString();
      } catch {
        return dateString;
      }
    };

    return (
      <div className={styles.container}>
        <Button
          variant="ghost"
          size="sm"
          onClick={toggleExpanded}
          className={styles.header}
        >
          <div className={styles.headerLeft}>
            {isExpanded ? (
              <ChevronDown size={14} />
            ) : (
              <ChevronRight size={14} />
            )}
            <BookOpen size={14} className={styles.icon} />
            <span className={styles.title}>
              {title} ({references.length})
            </span>
          </div>
        </Button>

        {isExpanded && (
          <div className={styles.content}>
            <div className={styles.referencesList}>
              {references.map((reference, index) => (
                <div key={index} className={styles.reference}>
                  <div className={styles.referenceHeader}>
                    <a
                      href={reference.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className={styles.referenceLink}
                    >
                      <span className={styles.referenceTitle}>
                        {reference.title}
                      </span>
                      <ExternalLink size={12} className={styles.externalIcon} />
                    </a>
                  </div>
                  <div className={styles.referenceMetadata}>
                    <span className={styles.url}>{reference.url}</span>
                    {reference.score && (
                      <span className={styles.score}>
                        Score: {reference.score.toFixed(2)}
                      </span>
                    )}
                    {reference.published_date && (
                      <span className={styles.date}>
                        Published: {formatDate(reference.published_date)}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }
);

ReferencesDisplay.displayName = "ReferencesDisplay";
