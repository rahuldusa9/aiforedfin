/**
 * AI FOR EDUCATION – API Client
 * Centralized Axios instance for all backend communication.
 */

import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 480000, // 8 minutes for AI generation
  headers: {
    'Content-Type': 'application/json',
  },
});

// Extended timeout instance for long operations (story generation, batch) 
const apiLong = axios.create({
  baseURL: API_BASE,
  timeout: 900000, // 15 minutes for multilingual/batch operations
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => Promise.reject(error)
);

apiLong.interceptors.request.use(
  (config) => {
    console.log(`[API Long] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message;
    console.error(`[API Error] ${message}`);
    return Promise.reject(error);
  }
);

apiLong.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || error.message;
    console.error(`[API Error] ${message}`);
    return Promise.reject(error);
  }
);

// -------------------------------------------------------
// API Functions
// -------------------------------------------------------

// Auth
export const registerUser = (data) => api.post('/api/auth/register', data);
export const loginUser = (data) => api.post('/api/auth/login', data);

// Dashboard
export const getDashboardStats = (userId) => api.get(`/api/dashboard/stats/${userId}`);

// Podcast
export const generatePodcast = (topic, language = 'en', length = 'medium') => api.post('/api/podcast/generate', { topic, language, length });

// Quiz
export const generateQuiz = (topic, numQuestions, difficulty, content) =>
  api.post('/api/quiz/generate', { topic, num_questions: numQuestions, difficulty, content });
export const submitQuiz = (data) => api.post('/api/quiz/submit', data);
export const getQuizHistory = (userId) => api.get(`/api/quiz/history/${userId}`);

// Story (Multilingual Options)
export const getStoryLanguages = () => api.get('/api/story/languages');
export const generateStory = (topic, wordCount = 400) => api.post('/api/story/generate', { topic, wordCount });

// Story (Multilingual with Prosody)
export const generateMultilingualStory = (options) =>
  apiLong.post('/api/story/multilingual', {
    topic: options.topic,
    language: options.language || 'en',
    genre: options.genre || 'educational',
    age_group: options.ageGroup || 'kids',
    word_count: options.wordCount || 400,
    include_audio: options.includeAudio !== false,
    include_prosody: options.includeProsody !== false,
  });

export const generateBatchStories = (options) =>
  apiLong.post('/api/story/batch', {
    topic: options.topic,
    languages: options.languages,
    genre: options.genre || 'educational',
    age_group: options.ageGroup || 'kids',
    word_count: options.wordCount || 400,
    include_audio: options.includeAudio || false,
  });


export const getStoryVoices = (language) => api.get(`/api/story/voices/${language}`);
export const getStoryGenres = () => api.get('/api/story/genres');
export const getStoryAgeGroups = () => api.get('/api/story/age-groups');

// Tutor
export const generateLearningPath = (topic) => api.post('/api/tutor/learning-path', { topic });

// Friend
export const chatWithFriend = (message, userId) =>
  api.post('/api/friend/chat', { message, user_id: userId });
export const getEmotionalHistory = (userId) =>
  api.get(`/api/friend/emotional-history/${userId}`);

// Learning Progress
export const saveLearningProgress = (data) => api.post('/api/tutor/save-progress', data);

// ML
export const predictPerformance = (data) => api.post('/api/ml/predict-performance', data);
export const predictSentiment = (text) => api.post('/api/ml/predict-sentiment', { text });

// -------------------------------------------------------
// NEW FEATURES
// -------------------------------------------------------

// Gamification
export const getGamificationStats = (userId) => api.get(`/api/gamification/stats/${userId}`);
export const trackActivity = (userId, activityType, metadata) =>
  api.post(`/api/gamification/track/${userId}`, { activity_type: activityType, metadata });
export const updateStreak = (userId) => api.post(`/api/gamification/streak/${userId}`);
export const getLeaderboard = (limit = 10, timeframe = 'all') =>
  api.get(`/api/gamification/leaderboard?limit=${limit}&timeframe=${timeframe}`);
export const getAvailableBadges = () => api.get('/api/gamification/badges');

// Flashcards
export const createFlashcardDeck = (userId, data) => api.post(`/api/flashcards/decks/${userId}`, data);
export const getUserDecks = (userId) => api.get(`/api/flashcards/decks/${userId}`);
export const getDeck = (deckId, userId) => api.get(`/api/flashcards/deck/${deckId}/${userId}`);
export const deleteDeck = (deckId, userId) => api.delete(`/api/flashcards/deck/${deckId}/${userId}`);
export const addFlashcard = (deckId, userId, data) => api.post(`/api/flashcards/card/${deckId}/${userId}`, data);
export const getCardsForReview = (deckId, userId, limit = 20) =>
  api.get(`/api/flashcards/review/${deckId}/${userId}?limit=${limit}`);
export const reviewCard = (cardId, userId, difficulty, timeMs = 0) =>
  api.post(`/api/flashcards/review/${cardId}/${userId}`, { difficulty, time_ms: timeMs });
export const generateFlashcards = (deckId, userId, options) =>
  apiLong.post(`/api/flashcards/generate/${deckId}/${userId}`, options);
export const generateFlashcardDeck = (userId, options) =>
  apiLong.post(`/api/flashcards/generate-deck/${userId}`, options);
export const getFlashcardStats = (userId) => api.get(`/api/flashcards/stats/${userId}`);

// Analytics
export const logActivity = (userId, data) => api.post(`/api/analytics/log/${userId}`, data);
export const getLearningSummary = (userId, days = 30) =>
  api.get(`/api/analytics/summary/${userId}?days=${days}`);
export const getStrengthWeakness = (userId) => api.get(`/api/analytics/strengths/${userId}`);
export const getLearningVelocity = (userId) => api.get(`/api/analytics/velocity/${userId}`);
export const getTimeAnalytics = (userId, days = 7) =>
  api.get(`/api/analytics/time/${userId}?days=${days}`);
export const getRecommendations = (userId) => api.get(`/api/analytics/recommendations/${userId}`);

// Study Notes
export const generateNotes = (userId, options) =>
  apiLong.post(`/api/notes/generate/${userId}`, options);
export const createNote = (userId, data) => api.post(`/api/notes/${userId}`, data);
export const getUserNotes = (userId, folderId = null, tag = null) => {
  let url = `/api/notes/${userId}`;
  const params = [];
  if (folderId) params.push(`folder_id=${folderId}`);
  if (tag) params.push(`tag=${tag}`);
  if (params.length) url += '?' + params.join('&');
  return api.get(url);
};
export const getNote = (noteId, userId) => api.get(`/api/notes/note/${noteId}/${userId}`);
export const updateNote = (noteId, userId, data) => api.put(`/api/notes/note/${noteId}/${userId}`, data);
export const deleteNote = (noteId, userId) => api.delete(`/api/notes/note/${noteId}/${userId}`);
export const generateMindMap = (topic, depth = 2) =>
  api.post('/api/notes/mind-map', { topic, depth });
export const explainConcept = (concept, level = 'simple') =>
  api.post('/api/notes/explain', { concept, level, use_analogy: true });
export const summarizeText = (text, length = 'medium') =>
  api.post('/api/notes/summarize', { text, length });
export const searchNotes = (userId, query) =>
  api.get(`/api/notes/search/${userId}?query=${encodeURIComponent(query)}`);
export const createNoteFolder = (userId, data) => api.post(`/api/notes/folders/${userId}`, data);
export const getNoteFolders = (userId) => api.get(`/api/notes/folders/${userId}`);

// Voice Learning
export const processVoiceInput = (userId, text, language = 'en') =>
  api.post(`/api/voice/process/${userId}`, { text, language });
export const parseVoiceCommand = (text) => api.post('/api/voice/parse', { text });
export const generateOralPractice = (options) => api.post('/api/voice/oral-practice', options);
export const checkPronunciation = (expected, spoken, language = 'en') =>
  api.post('/api/voice/pronunciation-check', { expected, spoken, language });
export const getVoiceTips = (language = 'en') => api.get(`/api/voice/tips?language=${language}`);
export const getVoiceCommands = () => api.get('/api/voice/commands');

// Learning Paths
export const getAssessment = () => api.get('/api/learning-paths/assessment');
export const submitAssessment = (userId, answers) =>
  api.post(`/api/learning-paths/assessment/${userId}`, { answers });
export const getLearningProfile = (userId) => api.get(`/api/learning-paths/profile/${userId}`);
export const updateLearningProfile = (userId, data) =>
  api.put(`/api/learning-paths/profile/${userId}`, data);
export const getRecommendedDifficulty = (userId, topic = null) => {
  let url = `/api/learning-paths/difficulty/${userId}`;
  if (topic) url += `?topic=${encodeURIComponent(topic)}`;
  return api.get(url);
};
export const getAvailablePaths = (difficulty = null, subject = null) => {
  let url = '/api/learning-paths/available';
  const params = [];
  if (difficulty) params.push(`difficulty=${difficulty}`);
  if (subject) params.push(`subject=${encodeURIComponent(subject)}`);
  if (params.length) url += '?' + params.join('&');
  return api.get(url);
};
export const generateLearningPathAI = (userId, options) =>
  apiLong.post(`/api/learning-paths/generate/${userId}`, options);
export const enrollInPath = (pathId, userId) =>
  api.post(`/api/learning-paths/enroll/${pathId}/${userId}`);
export const getUserPaths = (userId) => api.get(`/api/learning-paths/my-paths/${userId}`);
export const completeLesson = (pathId, userId, lessonNumber, score = null) =>
  api.post(`/api/learning-paths/complete-lesson/${pathId}/${userId}`, {
    lesson_number: lessonNumber,
    score,
  });

// Study Buddy
export const chatWithBuddy = (userId, message, context = null) =>
  api.post(`/api/buddy/chat/${userId}`, { message, context });
export const getBuddyCheckIn = (userId) => api.get(`/api/buddy/check-in/${userId}`);
export const createStudyPlan = (userId, goals, minutes = 60, days = 7) =>
  apiLong.post(`/api/buddy/study-plan/${userId}`, {
    goals,
    available_time_minutes: minutes,
    days,
  });
export const getStudyPlan = (userId) => api.get(`/api/buddy/study-plan/${userId}`);
export const getTodaysTasks = (userId) => api.get(`/api/buddy/today/${userId}`);
export const getMotivation = (userId, context = '') =>
  api.get(`/api/buddy/motivation/${userId}?context=${encodeURIComponent(context)}`);
export const explainSimply = (topic, level = 'eli5') =>
  api.post('/api/buddy/explain', { topic, level });
export const setBuddyPersonality = (userId, personality) =>
  api.post(`/api/buddy/personality/${userId}`, { personality });
export const getBuddyPersonalities = () => api.get('/api/buddy/personalities');

export default api;
