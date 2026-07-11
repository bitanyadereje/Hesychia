import { useState, useRef, useEffect } from 'react';

const RubricatedReply = ({ content }) => {
  const first = content.charAt(0);
  const rest = content.slice(1);
  return (
    <p className="font-serif text-ink text-base sm:text-lg leading-relaxed whitespace-pre-wrap">
      <span className="drop-cap" aria-hidden="true">{first}</span>
      {rest}
    </p>
  );
};

const ChatWidget = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [conversationStarted, setConversationStarted] = useState(false);
  const messagesEndRef = useRef(null);

  const prompts = [
    "How do I find inner stillness?",
    "What is the purpose of suffering?",
    "How should I pray?",
    "What does he say about the heart?",
    "How do I overcome despair?",
  ];

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    // Hide chips immediately when user sends a message
    setConversationStarted(true);

    const userMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const API_URL = import.meta.env.PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: input }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();

      const assistantMessage = {
        role: 'assistant',
        content: data.answer || 'No answer returned.',
        citation: data.homily_citation || 'St. Isaac of Nineveh',
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error calling backend:', error);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'I am having trouble reaching the wisdom of St. Isaac. Please try again.',
          citation: '— Connection Error',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePromptClick = (prompt) => {
    setInput(prompt);
    setTimeout(() => {
      const fakeEvent = { preventDefault: () => {} };
      handleSubmit(fakeEvent);
    }, 100);
  };

  // Reset conversation (optional — add a clear button)
  const resetConversation = () => {
    setMessages([]);
    setConversationStarted(false);
  };

  return (
    <div className="flex flex-col h-[500px] sm:h-[550px] md:h-[600px]">
      {/* Spiritual Conversation Title */}
      <div className="spiritual-title text-xs sm:text-sm">✦ Spiritual Conversation ✦</div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto manuscript-scroll space-y-3 sm:space-y-4 pr-1 sm:pr-2">
        {messages.length === 0 ? (
          <div className="text-center text-ink-soft mt-8 sm:mt-12 md:mt-16 px-2 sm:px-4">
            <p className="text-base sm:text-lg md:text-xl font-serif italic">
              Ask me anything about the spiritual life...
            </p>
            <div className="w-8 sm:w-10 h-px bg-gold/30 mx-auto my-3 sm:my-5"></div>
            <p className="text-sm sm:text-base font-serif italic text-ink-soft/70">
              &ldquo;Be at peace with your own soul, and heaven and earth will be at peace with you.&rdquo;
            </p>
            <p className="text-xs sm:text-sm mt-2 font-display tracking-wide text-ink-soft/50">
              — St. Isaac of Nineveh
            </p>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} bubble-enter`}
            >
              <div
                className={`max-w-[88%] sm:max-w-[85%] ${
                  msg.role === 'user' ? 'user-bubble' : 'assistant-bubble'
                }`}
              >
                {msg.role === 'assistant' ? (
                  <RubricatedReply content={msg.content} />
                ) : (
                  <p className="font-serif text-ink text-base sm:text-lg leading-relaxed whitespace-pre-wrap">
                    {msg.content}
                  </p>
                )}
                {msg.citation && (
                  <p className="text-xs sm:text-sm text-ink-soft italic mt-2 sm:mt-3 pt-2 border-t border-gold/20 clear-left">
                    — {msg.citation}
                  </p>
                )}
              </div>
            </div>
          ))
        )}

        {isLoading && (
          <div className="flex justify-start bubble-enter">
            <div className="assistant-bubble">
              <div className="flex items-end gap-1.5 h-4">
                <span className="flame w-1 h-3 bg-candle rounded-full [animation-delay:-0.3s]"></span>
                <span className="flame w-1 h-4 bg-gold-bright rounded-full [animation-delay:-0.15s]"></span>
                <span className="flame w-1 h-3 bg-candle rounded-full"></span>
              </div>
              <p className="text-xs sm:text-sm text-ink-soft mt-2 font-serif italic">
                Searching the Homilies in stillness...
              </p>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Prompt Chips — Hide once conversation has started */}
      {!conversationStarted && (
        <div className="mt-2 sm:mt-3">
          <p className="text-xs font-serif italic text-ink-soft/40 mb-1.5 text-center">
            Try asking...
          </p>
          <div className="flex flex-nowrap sm:flex-wrap gap-1.5 sm:gap-2 overflow-x-auto sm:overflow-x-visible pb-1 sm:pb-0 justify-start sm:justify-center">
            {prompts.map((p, i) => (
              <button
                key={i}
                onClick={() => handlePromptClick(p)}
                className="suggestion-chip text-xs sm:text-sm whitespace-nowrap"
              >
                {p}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="mt-3 sm:mt-4 pt-3 sm:pt-4 border-t border-gold/20 flex flex-col sm:flex-row gap-2">
        <div className="input-wrapper flex-1">
          <span className="input-icon text-sm sm:text-base">✧</span>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask St. Isaac..."
            className="input-field text-base sm:text-lg"
            disabled={isLoading}
          />
        </div>
        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          className="seek-button w-full sm:w-auto flex justify-center text-base sm:text-lg"
        >
          Ask
        </button>
      </form>
    </div>
  );
};

export default ChatWidget;