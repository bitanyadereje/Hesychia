import { useState } from 'react';

// Splits an assistant reply so the first letter can be set as a rubricated
// (illuminated) initial, the way a scribe would mark the start of a homily.
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'This is a test response. The manuscript theme is working!',
          citation: 'Homily 34, St. Isaac of Nineveh',
        },
      ]);
      setIsLoading(false);
    }, 1000);
  };

  return (
    <div className="flex flex-col h-[600px]">
      <div className="flex-1 overflow-y-auto manuscript-scroll space-y-5 pr-2">
        {messages.length === 0 ? (
          <div className="text-center text-ink-soft mt-16 px-4">
            <p className="text-xl font-serif italic">Ask me anything about the spiritual life&hellip;</p>
            <div className="w-10 h-px bg-gold/50 mx-auto my-5"></div>
            <p className="text-base font-serif italic text-ink-soft/80">
              &ldquo;Be at peace with your own soul, and heaven and earth will be at peace with you.&rdquo;
            </p>
            <p className="text-sm mt-2 font-display tracking-wide text-ink-soft/70">— St. Isaac of Nineveh</p>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[82%] p-4 md:p-5 rounded-sm ${
                  msg.role === 'user'
                    ? 'bg-vellum border-l-2 border-porphyry/70'
                    : 'bg-vellum-card border-l-2 border-gold shadow-[0_2px_10px_rgba(42,29,20,0.08)]'
                }`}
              >
                {msg.role === 'assistant' ? (
                  <RubricatedReply content={msg.content} />
                ) : (
                  <p className="font-serif text-ink text-lg leading-relaxed whitespace-pre-wrap">
                    {msg.content}
                  </p>
                )}
                {msg.citation && (
                  <p className="text-sm text-ink-soft italic mt-3 pt-2 border-t border-gold/25 clear-left">
                    — {msg.citation}
                  </p>
                )}
              </div>
            </div>
          ))
        )}

        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-vellum-card p-4 rounded-sm border-l-2 border-gold">
              <div className="flex items-end gap-1.5 h-4">
                <span className="flame w-1 h-3 bg-candle rounded-full [animation-delay:-0.3s]"></span>
                <span className="flame w-1 h-4 bg-gold-bright rounded-full [animation-delay:-0.15s]"></span>
                <span className="flame w-1 h-3 bg-candle rounded-full"></span>
              </div>
              <p className="text-sm text-ink-soft mt-2 font-serif italic">Searching the Homilies in stillness&hellip;</p>
            </div>
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="mt-4 pt-4 border-t border-gold/25 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask St. Isaac..."
          className="flex-1 px-4 py-3 rounded-sm border border-gold/40 bg-vellum-card font-serif text-lg text-ink placeholder:text-ink-soft/50 focus:outline-none focus:border-gold-bright focus:ring-2 focus:ring-gold/20 transition-colors"
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          className="px-6 py-3 bg-porphyry hover:bg-porphyry-deep text-vellum-card font-display font-semibold tracking-wide rounded-sm transition-colors disabled:opacity-40 disabled:cursor-not-allowed shadow-[0_2px_8px_rgba(78,20,29,0.35)]"
        >
          Ask
        </button>
      </form>
    </div>
  );
};

export default ChatWidget;