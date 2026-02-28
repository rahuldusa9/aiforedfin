/**
 * AI FOR EDUCATION – API Client
 * Centralized Axios instance for all backend communication.
 */

import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000, // 2 minutes for AI generation
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

// Response interceptor
api.interceptors.response.use(
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
export const generatePodcast = (topic) => api.post('/api/podcast/generate', { topic });

// Quiz
export const generateQuiz = (topic, numQuestions, difficulty) =>
  api.post('/api/quiz/generate', { topic, num_questions: numQuestions, difficulty });
export const submitQuiz = (data) => api.post('/api/quiz/submit', data);
export const getQuizHistory = (userId) => api.get(`/api/quiz/history/${userId}`);

// Story
export const generateStory = (topic) => api.post('/api/story/generate', { topic });

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

export default api;
