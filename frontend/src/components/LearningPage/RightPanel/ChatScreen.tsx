import { useEffect, useRef, useState } from "react";
import { SendHorizonal, Loader2, Sparkles } from "lucide-react";
import ReactMarkdown from "react-markdown";
import toast from "react-hot-toast";
import { useGlobalContext } from "@/context/GlobalContext";

function ChatScreen() {
  const { authUser, chatMessages, setChatMessages } = useGlobalContext();
  const [input, setInput] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const lastMessageRef = useRef<HTMLDivElement | null>(null);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    const userQuestion = input.trim();
    setChatMessages((prev) => [...prev, { from: "user", text: userQuestion }]);
    setInput("");
    setIsLoading(true);

    try {
      const res = await fetch(
        `${import.meta.env.VITE_BACKEND_URI}/api/video/chat`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + authUser?.token,
          },
          body: JSON.stringify({ question: userQuestion }),
        }
      );
      const data = await res.json();
      if (data.error) {
        throw new Error(data.error);
      }
      setChatMessages((prev) => [...prev, { from: "bot", text: data.answer }]);
    } catch (error) {
      if (error instanceof Error) {
        toast.error(error.message);
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    setTimeout(() => {
      lastMessageRef.current?.scrollIntoView({ behavior: "smooth" });
    }, 100);
  }, [chatMessages, isLoading]);

  return (
    <div className="flex flex-col bg-white text-gray-900 h-full overflow-hidden">
      <div className="overflow-y-auto p-4 space-y-4 h-[90vh]">
        {chatMessages.map((msg, i) => {
          if (msg.from === "user") {
            return (
              <div
                key={i}
                className="bg-[#F3F3F3] p-3 rounded-lg max-w-[65%] ml-auto text-lg"
              >
                {msg.text}
              </div>
            );
          } else {
            return (
              <div
                key={i}
                className="prose prose-base max-w-none p-4 leading-snug text-[1.1rem]"
              >
                <ReactMarkdown>{msg.text}</ReactMarkdown>
              </div>
            );
          }
        })}

        {/* AI Thinking / Loading Indicator */}
        {isLoading && (
          <div className="flex items-center gap-2.5 p-3.5 bg-slate-50 border border-slate-200/70 rounded-xl max-w-[70%] text-slate-700 shadow-xs">
            <Sparkles size={16} className="text-amber-500 animate-pulse shrink-0" />
            <span className="text-sm font-medium text-slate-600">Thinking</span>
            <div className="flex items-center gap-1 ml-0.5">
              <span className="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce [animation-delay:-0.3s]"></span>
              <span className="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce [animation-delay:-0.15s]"></span>
              <span className="w-1.5 h-1.5 rounded-full bg-slate-400 animate-bounce"></span>
            </div>
          </div>
        )}

        <div ref={lastMessageRef}></div>
      </div>

      <div className="p-4 bg-white flex items-center gap-2 border-t border-slate-100">
        <input
          type="text"
          value={input}
          disabled={isLoading}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !isLoading) {
              handleSend();
            }
          }}
          placeholder={isLoading ? "Thinking..." : "Ask anything about the video..."}
          className="flex-1 p-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-slate-400 disabled:bg-slate-50 disabled:cursor-not-allowed"
        />
        <button
          onClick={handleSend}
          disabled={isLoading || !input.trim()}
          className={`p-2 rounded-lg text-white transition-all duration-150 flex items-center justify-center ${
            isLoading || !input.trim()
              ? "bg-slate-300 text-slate-500 cursor-not-allowed"
              : "bg-slate-700 hover:bg-slate-900 cursor-pointer shadow-xs"
          }`}
        >
          {isLoading ? (
            <Loader2 size={18} className="animate-spin text-white" />
          ) : (
            <SendHorizonal size={18} />
          )}
        </button>
      </div>
    </div>
  );
}

export default ChatScreen;
