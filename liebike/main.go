package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"sync"
	"time"

	"github.com/google/uuid"
	"github.com/gorilla/handlers"
	"github.com/gorilla/mux"
)

const (
	GridSize        = 40
	Port            = ":6008"
	SessionTimeout  = 10 * time.Minute
	MinMoveDuration = 30 * time.Millisecond // Game loop runs at 100ms, allow some tolerance
	MaxMoveDuration = 2 * time.Second       // Maximum time between moves before considering suspicious
)

type Server struct {
	router       *mux.Router
	gameState    *GameState
	sessions     map[string]*GameSession
	sessionMutex sync.RWMutex
	logBuffer    []string
	logMutex     sync.RWMutex
}

type GameState struct {
	HighScore int    `json:"high_score"`
	TopPlayer string `json:"top_player"`
}

type GameSession struct {
	ID           string
	Trail        []Position
	StartTime    time.Time
	LastMoveTime time.Time
	Active       bool
}

type Position struct {
	X int `json:"x"`
	Y int `json:"y"`
}

func NewServer() *Server {
	s := &Server{
		router: mux.NewRouter(),
		gameState: &GameState{
			HighScore: 500,
			TopPlayer: "ARC",
		},
		sessions:  make(map[string]*GameSession),
		logBuffer: make([]string, 0, 100), // Buffer last 100 log entries
	}

	s.routes()
	go s.cleanupExpiredSessions()
	return s
}

func (s *Server) routes() {
	// API routes
	api := s.router.PathPrefix("/api").Subrouter()
	api.HandleFunc("/start_game", s.handleStartGame).Methods("POST")
	api.HandleFunc("/move", s.handleMove).Methods("POST")
	api.HandleFunc("/submit_score", s.HandleSubmitScore).Methods("POST")
	api.HandleFunc("/success", s.handleSuccess).Methods("GET")
	api.HandleFunc("/leaderboard", s.handleLeaderboard).Methods("GET")
	api.HandleFunc("/logs", s.handleLogs).Methods("GET")

	// Static file serving
	s.router.PathPrefix("/static/").Handler(http.StripPrefix("/static/", http.FileServer(http.Dir("./static/"))))

	// Root route serves the game
	s.router.HandleFunc("/", s.handleIndex).Methods("GET")
}

func (s *Server) handleIndex(w http.ResponseWriter, r *http.Request) {
	logMsg := fmt.Sprintf("Player accessed game from IP: %s", r.RemoteAddr)
	log.Print(logMsg)
	s.addToLogBuffer(logMsg)
	http.ServeFile(w, r, "./static/index.html")
}

func (s *Server) handleLeaderboard(w http.ResponseWriter, r *http.Request) {
	logMsg := "Leaderboard requested"
	log.Print(logMsg)
	s.addToLogBuffer(logMsg)
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(s.gameState)
}

func (s *Server) handleSuccess(w http.ResponseWriter, r *http.Request) {
	logMsg := "SUCCESS ENDPOINT ACCESSED - Challenge completed!"
	log.Print(logMsg)
	s.addToLogBuffer(logMsg)
	w.Header().Set("Content-Type", "application/json")
	response := map[string]interface{}{
		"message": "Challenge completed successfully!",
		"flag":    "SAINTCON{cl13nt_s1d3_trust_1s_d4ng3r0us}",
		"status":  "success",
	}
	json.NewEncoder(w).Encode(response)
}

func (s *Server) handleLogs(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	s.logMutex.RLock()
	logs := make([]string, len(s.logBuffer))
	copy(logs, s.logBuffer)
	s.logMutex.RUnlock()

	response := map[string]interface{}{
		"logs": logs,
	}
	json.NewEncoder(w).Encode(response)
}

func (s *Server) addToLogBuffer(message string) {
	s.logMutex.Lock()
	defer s.logMutex.Unlock()

	s.logBuffer = append(s.logBuffer, message)

	// Keep only last 100 log entries
	if len(s.logBuffer) > 100 {
		s.logBuffer = s.logBuffer[1:]
	}
}

func (s *Server) handleStartGame(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	sessionID := uuid.New().String()

	session := &GameSession{
		ID:           sessionID,
		Trail:        make([]Position, 0),
		StartTime:    time.Now(),
		LastMoveTime: time.Now(),
		Active:       true,
	}

	s.sessionMutex.Lock()
	s.sessions[sessionID] = session
	s.sessionMutex.Unlock()

	logMsg := fmt.Sprintf("New game session started: %s", sessionID)
	log.Print(logMsg)
	s.addToLogBuffer(logMsg)

	response := map[string]string{
		"session_id": sessionID,
		"status":     "started",
	}
	json.NewEncoder(w).Encode(response)
}

func (s *Server) handleMove(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "application/json")

	var moveData struct {
		SessionID string   `json:"session_id"`
		Position  Position `json:"position"`
	}

	if err := json.NewDecoder(r.Body).Decode(&moveData); err != nil {
		http.Error(w, `{"error": "Invalid JSON payload"}`, http.StatusBadRequest)
		return
	}

	s.sessionMutex.Lock()
	session, exists := s.sessions[moveData.SessionID]
	s.sessionMutex.Unlock()

	if !exists {
		http.Error(w, `{"error": "Invalid session ID"}`, http.StatusNotFound)
		return
	}

	if !session.Active {
		http.Error(w, `{"error": "Session is no longer active"}`, http.StatusBadRequest)
		return
	}

	now := time.Now()

	// Validate move timing (only after first move)
	if len(session.Trail) > 0 {
		timeSinceLastMove := now.Sub(session.LastMoveTime)

		if timeSinceLastMove < MinMoveDuration {
			logMsg := fmt.Sprintf("Move too fast for session %s: %v", moveData.SessionID, timeSinceLastMove)
			log.Print(logMsg)
			s.addToLogBuffer(logMsg)
			http.Error(w, `{"error": "Moves are too fast"}`, http.StatusBadRequest)
			return
		}

		if timeSinceLastMove > MaxMoveDuration {
			logMsg := fmt.Sprintf("Move too slow for session %s: %v", moveData.SessionID, timeSinceLastMove)
			log.Print(logMsg)
			s.addToLogBuffer(logMsg)
			http.Error(w, `{"error": "Moves are too slow"}`, http.StatusBadRequest)
			return
		}
	}

	s.sessionMutex.Lock()
	session.Trail = append(session.Trail, moveData.Position)
	session.LastMoveTime = now
	s.sessionMutex.Unlock()

	response := map[string]string{
		"status": "recorded",
	}
	json.NewEncoder(w).Encode(response)
}

func (s *Server) cleanupExpiredSessions() {
	ticker := time.NewTicker(1 * time.Minute)
	defer ticker.Stop()

	for range ticker.C {
		now := time.Now()
		s.sessionMutex.Lock()
		for id, session := range s.sessions {
			if now.Sub(session.LastMoveTime) > SessionTimeout {
				delete(s.sessions, id)
				logMsg := fmt.Sprintf("Expired session cleaned up: %s", id)
				log.Print(logMsg)
				s.addToLogBuffer(logMsg)
			}
		}
		s.sessionMutex.Unlock()
	}
}

func main() {
	server := NewServer()

	// Enable CORS for development
	corsHandler := handlers.CORS(
		handlers.AllowedOrigins([]string{"*"}),
		handlers.AllowedMethods([]string{"GET", "POST", "PUT", "DELETE", "OPTIONS"}),
		handlers.AllowedHeaders([]string{"Content-Type", "Authorization"}),
	)(server.router)

	startMsg := fmt.Sprintf("Light Cycle Racer server starting on port %s", Port)
	availMsg := fmt.Sprintf("Game available at: http://localhost%s", Port)
	log.Print(startMsg)
	log.Print(availMsg)
	server.addToLogBuffer(startMsg)
	server.addToLogBuffer(availMsg)

	// Ensure static directory exists
	if err := os.MkdirAll("static", 0755); err != nil {
		log.Fatal("Failed to create static directory:", err)
	}

	log.Fatal(http.ListenAndServe(Port, corsHandler))
}
