import { useState, useRef, useEffect } from 'react';

const RubricatedReply = ({ content }) => {
  const first = content.charAt(0);
  const rest = content.slice(1);
  return (
    <p className="font-serif text-ink text-lg leading-relaxed whitespace-pre-wrap">
      <span className="drop-cap" aria-hidden="true">{first}</span>
      {rest}
    </p>
  );
};

const ChatWidget = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
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

    const userMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'My child, St. Isaac teaches that tears are a gift from God...',
          citation: 'Homily 34, St. Isaac of Nineveh',
        },
      ]);
      setIsLoading(false);
    }, 1200);
  };

  const handlePromptClick = (prompt) => {
    setInput(prompt);
    setTimeout(() => {
      const fakeEvent = { preventDefault: () => {} };
      handleSubmit(fakeEvent);
    }, 100);
  };

  return (
    <div className="flex flex-col h-[600px]">
      <div className="spiritual-title">✦ Spiritual Conversation ✦</div>

      <div className="flex flex-1 gap-4 min-h-0">
        <div className="hidden md:block w-48 flex-shrink-0 border-r border-gold/20 pr-4 overflow-y-auto">
          <p className="text-sm font-serif italic text-ink-soft/50 mb-3">Questions to ponder...</p>
          <div className="space-y-2">
            {prompts.map((p, i) => (
              <button
                key={i}
                onClick={() => handlePromptClick(p)}
                className="suggestion-chip w-full text-left"
              >
                {p}
              </button>
            ))}
          </div>
        </div>

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto manuscript-scroll space-y-4 pr-2">
          {messages.length === 0 ? (
            <div className="text-center text-ink-soft mt-16 px-4">
              <p className="text-xl font-serif italic">Ask me anything about the spiritual life&hellip;</p>
              <div className="w-10 h-px bg-gold/30 mx-auto my-5"></div>
              <p className="text-base font-serif italic text-ink-soft/70">
                &ldquo;Be at peace with your own soul, and heaven and earth will be at peace with you.&rdquo;
              </p>
              <p className="text-sm mt-2 font-display tracking-wide text-ink-soft/50">— St. Isaac of Nineveh</p>
            </div>
          ) : (
            messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} bubble-enter`}
              >
                <div
                  className={`max-w-[85%] ${msg.role === 'user' ? 'user-bubble' : 'assistant-bubble'}`}
                >
                  {msg.role === 'assistant' ? (
                    <RubricatedReply content={msg.content} />
                  ) : (
                    <p className="font-serif text-ink text-lg leading-relaxed whitespace-pre-wrap">
                      {msg.content}
                    </p>
                  )}
                  {msg.citation && (
                    <p className="text-sm text-ink-soft italic mt-3 pt-2 border-t border-gold/20 clear-left">
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
                <p className="text-sm text-ink-soft mt-2 font-serif italic">Searching the Homilies in stillness&hellip;</p>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="mt-4 pt-4 border-t border-gold/20 flex gap-3">
        <div className="input-wrapper">
          <span className="input-icon">✧</span>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask St. Isaac..."
            className="input-field"
            disabled={isLoading}
          />
        </div>
        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          className="seek-button"
        >
          Ask
        </button>
      </form>
    </div>
  );
};

export default ChatWidget;