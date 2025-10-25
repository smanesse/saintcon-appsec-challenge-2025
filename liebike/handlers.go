package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
)

// ScoreSubmission represents the payload sent by the client when the game ends
type ScoreSubmission struct {
	SessionID     string     `json:"session_id"`
	FinalPosition Position   `json:"final_position"`
	Score         int        `json:"score"`
}

// ScoreResponse represents the server's response to a score submission
type ScoreResponse struct {
	Message         string `json:"message"`
	ChallengePoints int    `json:"challenge_points"`
	NewHighScore    bool   `json:"new_high_score"`
	HighScore       int    `json:"high_score"`
	Status          string `json:"status"`
}

func (s *Server) HandleSubmitScore(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	var submission ScoreSubmission
	if err := json.NewDecoder(r.Body).Decode(&submission); err != nil {
		http.Error(w, `{"error": "Invalid JSON payload"}`, http.StatusBadRequest)
		return
	}

	// Validate session exists
	s.sessionMutex.RLock()
	session, exists := s.sessions[submission.SessionID]
	s.sessionMutex.RUnlock()

	if !exists {
		logMsg := fmt.Sprintf("Invalid session ID in score submission: %s", submission.SessionID)
		log.Print(logMsg)
		s.addToLogBuffer(logMsg)
		http.Error(w, `{"error": "Invalid session ID"}`, http.StatusBadRequest)
		return
	}

	if !session.Active {
		logMsg := fmt.Sprintf("Attempt to submit score for inactive session: %s", submission.SessionID)
		log.Print(logMsg)
		s.addToLogBuffer(logMsg)
		http.Error(w, `{"error": "Session is no longer active"}`, http.StatusBadRequest)
		return
	}

	logMsg := fmt.Sprintf("Score submission received: SessionID: %s, Position(%d,%d), Trail length: %d, Score: %d",
		submission.SessionID, submission.FinalPosition.X, submission.FinalPosition.Y,
		len(session.Trail), submission.Score)
	log.Print(logMsg)
	s.addToLogBuffer(logMsg)

	// Validate minimum trail length (at least some moves were made)
	if len(session.Trail) < 3 {
		logMsg := fmt.Sprintf("Invalid submission: Trail too short (%d moves)", len(session.Trail))
		log.Print(logMsg)
		s.addToLogBuffer(logMsg)
		http.Error(w, `{"error": "Trail too short - play the game first"}`, http.StatusBadRequest)
		return
	}

	// Validate the crash using the server-side tracked trail
	if !s.isValidCrash(submission.FinalPosition, session.Trail) {
		logMsg := fmt.Sprintf("Invalid crash detected: Position(%d,%d) not in trail or bounds",
			submission.FinalPosition.X, submission.FinalPosition.Y)
		log.Print(logMsg)
		s.addToLogBuffer(logMsg)
		response := ScoreResponse{
			Message: "Invalid game over state - crash location not valid",
			Status:  "rejected",
		}
		w.WriteHeader(http.StatusBadRequest)
		json.NewEncoder(w).Encode(response)
		return
	}

	// Mark session as inactive
	s.sessionMutex.Lock()
	session.Active = false
	s.sessionMutex.Unlock()

	newHighScore := false

	calculatedScore := len(session.Trail)
	if calculatedScore > s.gameState.HighScore {
		s.gameState.HighScore = calculatedScore
		s.gameState.TopPlayer = "CHALLENGER"
		newHighScore = true
		logMsg := fmt.Sprintf("New high score achieved: %d", calculatedScore)
		log.Print(logMsg)
		s.addToLogBuffer(logMsg)
	}

	response := ScoreResponse{
		Message:      "Score processed successfully",
		NewHighScore: newHighScore,
		HighScore:    s.gameState.HighScore,
		Status:       "accepted",
	}

	json.NewEncoder(w).Encode(response)
}

// isValidCrash checks if the final position represents a legitimate game over condition
func (s *Server) isValidCrash(head Position, trail []Position) bool {
	// Check for wall collision
	if head.X < 0 || head.X >= GridSize || head.Y < 0 || head.Y >= GridSize {
		logMsg := fmt.Sprintf("Wall collision detected at (%d,%d)", head.X, head.Y)
		log.Print(logMsg)
		s.addToLogBuffer(logMsg)
		return true
	}

	// Check for trail collision
	for _, segment := range trail {
		if segment.X == head.X && segment.Y == head.Y {
			logMsg := fmt.Sprintf("Trail collision detected at (%d,%d)", head.X, head.Y)
			log.Print(logMsg)
			s.addToLogBuffer(logMsg)
			return true
		}
	}

	logMsg := fmt.Sprintf("No valid crash found at (%d,%d)", head.X, head.Y)
	log.Print(logMsg)
	s.addToLogBuffer(logMsg)
	return false
}

