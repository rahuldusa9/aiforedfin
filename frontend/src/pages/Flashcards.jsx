/**
 * AI FOR EDUCATION – Flashcards Page
 * Spaced repetition flashcard learning with AI generation.
 */

import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import {
  getUserDecks,
  getDeck,
  generateFlashcardDeck,
  getCardsForReview,
  reviewCard,
  getFlashcardStats,
} from '../api';

// Icons
const PlusIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
  </svg>
);

const PlayIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
  </svg>
);

const SparklesIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
  </svg>
);

export default function Flashcards() {
  const { user } = useAuth();
  const { showToast } = useToast();

  const [decks, setDecks] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  // Study mode state
  const [studyMode, setStudyMode] = useState(false);
  const [currentDeck, setCurrentDeck] = useState(null);
  const [cards, setCards] = useState([]);
  const [currentCardIndex, setCurrentCardIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [sessionStats, setSessionStats] = useState({ correct: 0, total: 0 });

  // Create deck modal
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newTopic, setNewTopic] = useState('');
  const [cardCount, setCardCount] = useState(10);
  const [difficulty, setDifficulty] = useState('medium');

  useEffect(() => {
    if (user) {
      loadDecks();
      loadStats();
    }
  }, [user]);

  const loadDecks = async () => {
    try {
      const res = await getUserDecks(user.id);
      setDecks(res.data.decks || []);
    } catch (err) {
      console.error('Failed to load decks:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const res = await getFlashcardStats(user.id);
      setStats(res.data);
    } catch (err) {
      console.error('Failed to load stats:', err);
    }
  };

  const handleCreateDeck = async () => {
    if (!newTopic.trim()) {
      showToast('Please enter a topic', 'error');
      return;
    }

    setGenerating(true);
    try {
      const res = await generateFlashcardDeck(user.id, {
        topic: newTopic,
        card_count: cardCount,
        difficulty,
      });

      showToast(`Created deck with ${res.data.cards?.length || 0} cards!`, 'success');
      setShowCreateModal(false);
      setNewTopic('');
      loadDecks();
      loadStats();
    } catch (err) {
      showToast('Failed to create deck', 'error');
    } finally {
      setGenerating(false);
    }
  };

  const startStudy = async (deck) => {
    try {
      const res = await getCardsForReview(deck.deck_id, user.id);
      if (res.data.cards.length === 0) {
        showToast('No cards due for review!', 'info');
        return;
      }

      setCurrentDeck(deck);
      setCards(res.data.cards);
      setCurrentCardIndex(0);
      setShowAnswer(false);
      setSessionStats({ correct: 0, total: 0 });
      setStudyMode(true);
    } catch (err) {
      showToast('Failed to start study session', 'error');
    }
  };

  const handleReview = async (difficulty) => {
    const card = cards[currentCardIndex];
    const isCorrect = ['good', 'easy'].includes(difficulty);

    try {
      await reviewCard(card.card_id, user.id, difficulty);

      setSessionStats(prev => ({
        correct: prev.correct + (isCorrect ? 1 : 0),
        total: prev.total + 1,
      }));

      // Move to next card
      if (currentCardIndex < cards.length - 1) {
        setCurrentCardIndex(prev => prev + 1);
        setShowAnswer(false);
      } else {
        // Session complete
        showToast(`Session complete! ${sessionStats.correct + (isCorrect ? 1 : 0)}/${sessionStats.total + 1} correct`, 'success');
        setStudyMode(false);
        loadDecks();
        loadStats();
      }
    } catch (err) {
      showToast('Failed to save review', 'error');
    }
  };

  // Study Mode UI
  if (studyMode && cards.length > 0) {
    const card = cards[currentCardIndex];

    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 p-6">
        <div className="max-w-2xl mx-auto">
          {/* Progress */}
          <div className="mb-6">
            <div className="flex justify-between text-white/70 text-sm mb-2">
              <span>Card {currentCardIndex + 1} of {cards.length}</span>
              <span>{sessionStats.correct}/{sessionStats.total} correct</span>
            </div>
            <div className="h-2 bg-white/20 rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-green-400 to-emerald-500 transition-all"
                style={{ width: `${((currentCardIndex + 1) / cards.length) * 100}%` }}
              />
            </div>
          </div>

          {/* Card */}
          <div
            className="bg-white rounded-2xl shadow-2xl p-8 min-h-[300px] cursor-pointer transform transition-all hover:scale-[1.02]"
            onClick={() => setShowAnswer(!showAnswer)}
          >
            <div className="text-center">
              <div className="text-xs uppercase tracking-wider text-gray-400 mb-4">
                {showAnswer ? 'Answer' : 'Question'}
              </div>

              <div className="text-2xl font-semibold text-gray-800 mb-4">
                {showAnswer ? card.back : card.front}
              </div>

              {!showAnswer && card.hint && (
                <div className="text-sm text-gray-500 mt-4">
                  💡 Hint: {card.hint}
                </div>
              )}

              {showAnswer && card.example && (
                <div className="text-sm text-gray-600 mt-4 p-3 bg-gray-50 rounded-lg">
                  📝 {card.example}
                </div>
              )}

              {!showAnswer && (
                <div className="text-sm text-gray-400 mt-8">
                  Tap to reveal answer
                </div>
              )}
            </div>
          </div>

          {/* Answer buttons */}
          {showAnswer && (
            <div className="grid grid-cols-4 gap-3 mt-6">
              <button
                onClick={() => handleReview('again')}
                className="p-4 bg-red-500 hover:bg-red-600 text-white rounded-xl font-medium transition-all"
              >
                Again
                <div className="text-xs opacity-70">Reset</div>
              </button>
              <button
                onClick={() => handleReview('hard')}
                className="p-4 bg-orange-500 hover:bg-orange-600 text-white rounded-xl font-medium transition-all"
              >
                Hard
                <div className="text-xs opacity-70">Soon</div>
              </button>
              <button
                onClick={() => handleReview('good')}
                className="p-4 bg-green-500 hover:bg-green-600 text-white rounded-xl font-medium transition-all"
              >
                Good
                <div className="text-xs opacity-70">Normal</div>
              </button>
              <button
                onClick={() => handleReview('easy')}
                className="p-4 bg-blue-500 hover:bg-blue-600 text-white rounded-xl font-medium transition-all"
              >
                Easy
                <div className="text-xs opacity-70">Later</div>
              </button>
            </div>
          )}

          {/* Exit button */}
          <button
            onClick={() => setStudyMode(false)}
            className="mt-6 text-white/70 hover:text-white transition-colors"
          >
            ← Exit Study Mode
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Flashcards</h1>
          <p className="text-white/70">Master any topic with spaced repetition</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg hover:opacity-90 transition-all"
        >
          <SparklesIcon />
          <span>Generate Deck</span>
        </button>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20">
            <div className="text-3xl font-bold text-white">{stats.total_cards}</div>
            <div className="text-white/70 text-sm">Total Cards</div>
          </div>
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20">
            <div className="text-3xl font-bold text-green-400">{stats.cards_due}</div>
            <div className="text-white/70 text-sm">Due Today</div>
          </div>
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20">
            <div className="text-3xl font-bold text-blue-400">{stats.accuracy?.toFixed(0) || 0}%</div>
            <div className="text-white/70 text-sm">Accuracy</div>
          </div>
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-4 border border-white/20">
            <div className="text-3xl font-bold text-purple-400">{stats.mastery_rate?.toFixed(0) || 0}%</div>
            <div className="text-white/70 text-sm">Mastered</div>
          </div>
        </div>
      )}

      {/* Decks */}
      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin w-8 h-8 border-4 border-white/30 border-t-white rounded-full mx-auto"></div>
          <p className="text-white/70 mt-4">Loading decks...</p>
        </div>
      ) : decks.length === 0 ? (
        <div className="text-center py-12 bg-white/10 backdrop-blur-md rounded-xl border border-white/20">
          <div className="text-6xl mb-4">🃏</div>
          <h3 className="text-xl font-semibold text-white mb-2">No Decks Yet</h3>
          <p className="text-white/70 mb-4">Create your first AI-powered flashcard deck!</p>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-6 py-2 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg"
          >
            Create Deck
          </button>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
          {decks.map((deck) => (
            <div
              key={deck.deck_id}
              className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20 hover:bg-white/20 transition-all"
            >
              <h3 className="text-lg font-semibold text-white mb-2">{deck.name}</h3>
              <p className="text-white/60 text-sm mb-4">{deck.description || deck.topic}</p>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-2 mb-4 text-center">
                <div className="bg-white/10 rounded-lg p-2">
                  <div className="text-lg font-bold text-white">{deck.stats?.total || deck.card_count || 0}</div>
                  <div className="text-xs text-white/60">Cards</div>
                </div>
                <div className="bg-white/10 rounded-lg p-2">
                  <div className="text-lg font-bold text-green-400">{deck.stats?.due_today || 0}</div>
                  <div className="text-xs text-white/60">Due</div>
                </div>
                <div className="bg-white/10 rounded-lg p-2">
                  <div className="text-lg font-bold text-purple-400">{deck.stats?.mastered || 0}</div>
                  <div className="text-xs text-white/60">Mastered</div>
                </div>
              </div>

              <button
                onClick={() => startStudy(deck)}
                className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-lg hover:opacity-90 transition-all"
              >
                <PlayIcon />
                <span>Study Now</span>
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Create Deck Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-gray-900 rounded-2xl p-6 w-full max-w-md border border-white/20">
            <h2 className="text-xl font-bold text-white mb-4">Generate Flashcard Deck</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-white/70 text-sm mb-1">Topic</label>
                <input
                  type="text"
                  value={newTopic}
                  onChange={(e) => setNewTopic(e.target.value)}
                  placeholder="e.g., Spanish vocabulary, Biology, History..."
                  className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/40 focus:outline-none focus:border-indigo-500"
                />
              </div>

              <div>
                <label className="block text-white/70 text-sm mb-1">Number of Cards: {cardCount}</label>
                <input
                  type="range"
                  min="5"
                  max="30"
                  value={cardCount}
                  onChange={(e) => setCardCount(parseInt(e.target.value))}
                  className="w-full"
                />
              </div>

              <div>
                <label className="block text-white/70 text-sm mb-1">Difficulty</label>
                <select
                  value={difficulty}
                  onChange={(e) => setDifficulty(e.target.value)}
                  className="w-full px-4 py-2 bg-white/10 border border-white/20 rounded-lg text-white focus:outline-none focus:border-indigo-500"
                >
                  <option value="easy">Easy</option>
                  <option value="medium">Medium</option>
                  <option value="hard">Hard</option>
                </select>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button
                onClick={() => setShowCreateModal(false)}
                className="flex-1 px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-all"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateDeck}
                disabled={generating}
                className="flex-1 px-4 py-2 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg hover:opacity-90 transition-all disabled:opacity-50"
              >
                {generating ? (
                  <span className="flex items-center justify-center gap-2">
                    <div className="animate-spin w-4 h-4 border-2 border-white/30 border-t-white rounded-full"></div>
                    Generating...
                  </span>
                ) : (
                  'Generate'
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
