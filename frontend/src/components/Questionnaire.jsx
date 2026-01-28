import React, { useState, useEffect } from "react";
import "./Questionnaire.css";
import { Link } from 'react-router-dom';


export default function Questionnaire({ user, questions, onSubmit }) {
  const [answers, setAnswers] = useState(() => {
    const saved = localStorage.getItem("answers");
    return saved ? JSON.parse(saved) : {};
  });

  const [customInputs, setCustomInputs] = useState(() => {
    const saved = localStorage.getItem("customInputs");
    return saved ? JSON.parse(saved) : {};
  });

  const [currentIndex, setCurrentIndex] = useState(0);

  // Save data to localStorage
  useEffect(() => {
    localStorage.setItem("answers", JSON.stringify(answers));
    localStorage.setItem("customInputs", JSON.stringify(customInputs));
  }, [answers, customInputs]);

  const handleChange = (id, value) => {
    setAnswers({ ...answers, [id]: value });
  };

  const handleCustomInput = (id, value) => {
    setCustomInputs({ ...customInputs, [id]: value });
    // Keep answers[q.id] as 'Other' for single-choice, or ensure 'Other' is in the array for multi-choice
    const qType = questions.find(q => q.id === id)?.type;
    if (qType === "single-choice") {
      if (answers[id] !== "Other") {
        setAnswers({ ...answers, [id]: "Other" });
      }
    } else if (qType === "multi-choice") {
      if (!Array.isArray(answers[id]) || !answers[id].includes("Other")) {
        setAnswers({ ...answers, [id]: [...(answers[id] || []), "Other"] });
      }
    }
  };

  const handleReset = () => {
    setAnswers({});
    setCustomInputs({});
    setCurrentIndex(0);
    localStorage.removeItem("answers");
    localStorage.removeItem("customInputs");
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(answers);
  };

  const nextQuestion = () => {
    if (currentIndex < questions.length - 1) setCurrentIndex(currentIndex + 1);
  };

  const prevQuestion = () => {
    if (currentIndex > 0) setCurrentIndex(currentIndex - 1);
  };

  const q = questions[currentIndex];

  return (
    <>
        {user ? (
          <>
            <form onSubmit={handleSubmit} className="questionnaire-form">
              <div className="App">
                <div className="question-card">
                  <label className="question-label"><b>{q.question}</b></label>
                  <br/>

                  {/* ✅ Single Choice */}
                  {q.type === "single-choice" &&
                    q.options.map((opt, i) => (
                      <React.Fragment key={i}>
                        <div
                          className={`option-box ${
                            answers[q.id] === opt ? "selected" : ""
                          }`}
                          onClick={() => handleChange(q.id, opt)}
                        >
                          {opt}
                        </div>
                        {/* Show input below the "Other" option if selected */}
                        {opt === "Other" && answers[q.id] === "Other" && (
                          <input
                            type="text"
                            placeholder="Please specify..."
                            value={customInputs[q.id] || ""}
                            onChange={(e) => handleCustomInput(q.id, e.target.value)}
                            className="custom-input"
                            style={{ marginLeft: 0, marginTop: 5, width: "calc(80%)" }}
                          />
                        )}
                      </React.Fragment>
                    ))}

                  {/* ✅ Multi Choice */}
                  {q.type === "multi-choice" &&
                    q.options.map((opt, i) => {
                      const selected = answers[q.id]?.includes(opt) || false;
                      return (
                        <React.Fragment key={i}>
                          <div
                            className={`option-box ${selected ? "selected" : ""}`}
                            onClick={() => {
                              const prev = answers[q.id] || [];
                              if (selected) {
                                handleChange(q.id, prev.filter((x) => x !== opt));
                              } else {
                                handleChange(q.id, [...prev, opt]);
                              }
                            }}
                          >
                            {opt}
                          </div>
                          {/* Show input below the "Other" option if selected */}
                          {opt === "Other" && answers[q.id]?.includes("Other") && (
                            <input
                              type="text"
                              placeholder="Please specify..."
                              value={customInputs[q.id] || ""}
                              onChange={(e) => handleCustomInput(q.id, e.target.value)}
                              className="custom-input"
                              style={{ marginLeft: 24, marginTop: 4, marginBottom: 8, width: "calc(80% - 24px)" }}
                            />
                          )}
                        </React.Fragment>
                      );
                    })}

                  {/* ✅ Text Input */}
                  {q.type === "text" && (
                    <input
                      type="text"
                      value={answers[q.id] || ""}
                      onChange={(e) => handleChange(q.id, e.target.value)}
                      className="text-input"
                    />
                  )}
                </div>
              

                <div className="progress-circles">
                  {questions.map((qItem, idx) => {
                    const answered = answers[qItem.id] && answers[qItem.id].length !== 0;
                    return (
                      <div
                        key={idx}
                        className={`circle ${answered ? "filled" : ""} ${
                          idx === currentIndex ? "current" : ""
                        }`}
                      />
                    );
                  })}
                </div>

                <div className="navigation-buttons">
                  <button
                    type="button"
                    onClick={prevQuestion}
                    disabled={currentIndex === 0}
                    className="nav-button"
                  >
                    Previous
                  </button>

                  {currentIndex < questions.length - 1 ? (
                    <button
                      type="button"
                      onClick={nextQuestion}
                      className="nav-button next"
                    >
                      Next
                    </button>
                  ) : (
                    <button type="submit" className="submit-button">
                      Submit
                    </button>
                  )}

                  <button type="button" onClick={handleReset} className="reset-button">
                    Reset
                  </button>
                </div>
              </div>
            </form>
          </>
        ):(
          <div id="not-signed-in">
            <h2 id='heading-not-signed-in'>Just a secccc.... <br />You haven't logged in yet
            </h2>
          
            <Link id='not-signed-in-link' to={'/auth'}>
                <button className='not-signed-in-btn'>
                    Log In
                </button>
            </Link>
          </div>
        )}
    </>
  );
}           