import React, { useEffect, useState } from "react";
import SentimentChart from "./SentimentChart";
import ProsConsChart from "./ProsConsChart";
import "./ReviewSection.css";
import { MessageSquare, ThumbsUp, ThumbsDown, Loader2 } from "lucide-react";

function ReviewSection({ model }) {
  const [reviewAnalysis, setReviewAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [retryCount, setRetryCount] = useState(0);
  const [selectedGroup, setSelectedGroup] = useState("Gamers");

  useEffect(() => {
    if (!model) return;

    const formattedModelName = model.replace(/ /g, "_");
    const fetchUrl = `http://localhost:5000/api/reviews/analysis/${formattedModelName}`;

    let isMounted = true;

    const fetchData = () => {
      fetch(fetchUrl)
        .then(res => {
          if (res.status === 404) throw new Error("File not found");
          if (!res.ok) throw new Error("Network response not ok");
          return res.json();
        })
        .then(data => {
          if (isMounted) {
            setReviewAnalysis(data);
            setLoading(false);
          }
        })
        .catch(err => {
          console.error("Fetch error or file not ready:", err);
          if (isMounted) {
            setTimeout(() => setRetryCount(prev => prev + 1), 3000);
          }
        });
    };

    setLoading(true);
    fetchData();

    return () => { isMounted = false; };
  }, [model, retryCount]);

  // Transform data logic
  const sentimentData = reviewAnalysis
    ? Object.entries(reviewAnalysis.group_analysis.sentiment_by_group).map(([user, stats]) => ({
        user,
        positive: stats.positive,
        neutral: stats.neutral,
        negative: stats.negative,
      }))
    : [];

  const currentGroupKeywords = reviewAnalysis?.group_analysis?.keywords_by_group[selectedGroup];
  const currentGroupSnippets = reviewAnalysis?.group_analysis?.snippets_by_group[selectedGroup];

  // --- RENDER ---
  return (
    <div className="reviews-section">
      {/* 1. Header always visible */}
      <div className="review-header">
        <h2>User Reviews & Sentiments</h2>
        {!loading && reviewAnalysis && (
          <span className="review-badge">
            <MessageSquare size={16} style={{ marginRight: '5px' }} />
            {reviewAnalysis.total_reviews} Reviews
          </span>
        )}
      </div>

      {/* 2. Conditional Loading State */}
      {loading ? (
        <div className="reviews-section-subhead loading-state">
          <div className="review-loader-container">
            <div className="review-loader"></div>
          </div>
          <p style={{textAlign: 'center', marginTop: '10px', color: '#666'}}>
            Analyzing Reddit & YouTube reviews...
          </p>
        </div>
      ) : reviewAnalysis ? (
        <>
          {/* 3. Loaded Content */}
          <div className="reviews-section-subhead">
            <h3>Sentiment Overview by Group</h3>
            <SentimentChart data={sentimentData} />
          </div>

          <div className="group-tabs-container">
            <h3>Deep Dive: What do specific users say?</h3>
            <div className="group-tabs">
              {Object.keys(reviewAnalysis.group_analysis.sentiment_by_group).map((group) => (
                <button
                  key={group}
                  className={`group-tab ${selectedGroup === group ? "active" : ""}`}
                  onClick={() => setSelectedGroup(group)}
                >
                  {group}
                </button>
              ))}
            </div>
          </div>

          <div className="details-grid">
            <div className="details-card">
              <h4>Top Pros & Cons for {selectedGroup}</h4>
              <div style={{ width: "100%", height: "350px" }}>
                <ProsConsChart keywordsData={currentGroupKeywords} />
              </div>
            </div>

            <div className="details-card">
              <h4>What they are actually saying...</h4>
              <div className="snippet-box positive">
                <div className="snippet-header"><ThumbsUp size={16} /> Positive</div>
                <p>"{currentGroupSnippets?.positive[0] || "No specific data."}"</p>
              </div>
              <div className="snippet-box negative">
                <div className="snippet-header"><ThumbsDown size={16} /> Negative</div>
                <p>"{currentGroupSnippets?.negative[0] || "No major complaints found."}"</p>
              </div>
            </div>
          </div>
        </>
      ) : (
        <div className="reviews-section-subhead">
          <p style={{ textAlign: 'center', padding: '20px' }}>Data unavailable.</p>
        </div>
      )}
    </div>
  );
}

export default ReviewSection;