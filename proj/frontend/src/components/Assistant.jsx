/**
 * Assistant.jsx  ─  AI-REA conversational assistant
 */

import React, { useState, useRef, useEffect, useCallback } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import "./Assistant.css";

const API = import.meta.env.VITE_BACKEND_URL || "http://localhost:8000";

// ── Routes ────────────────────────────────────────────
const ROUTE_TO_PAGE = {
    "/": "home",
    "/dashboard": "dashboard",
    "/results": "results",
    "/marketplace": "marketplace",
    "/marketplace/sell": "marketplace_sell",
    "/marketplace/buy": "marketplace_buy",
    "/about": "about",
};

const PAGE_TO_ROUTE = {
    home: "/",
    dashboard: "/dashboard",
    results: "/results",
    marketplace: "/marketplace",
    marketplace_sell: "/marketplace/sell",
    marketplace_buy: "/marketplace/buy",
    about: "/about",
};

// ── Tool badges ───────────────────────────────────────
const BADGE = {
    run_property_analysis: { color: "#10b981", label: "🏠 Analysis" },
    guide_to_page: { color: "#6366f1", label: "🗺️ Navigate" },
    fill_query_input: { color: "#14b8a6", label: "✏️ Filled" },
    fill_sell_property_form: { color: "#8b5cf6", label: "📝 Form filled" },
    generate_property_description: { color: "#f59e0b", label: "✍️ Description" },
};

const uuid = () => crypto.randomUUID?.() ?? Math.random().toString(36).slice(2, 15);

// ══════════════════════════════════════════════════════
// COMPONENT
// ══════════════════════════════════════════════════════
export default function Assistant() {
    const { t, i18n } = useTranslation();
    const loc = useLocation();
    const navigate = useNavigate();
    const page = ROUTE_TO_PAGE[loc.pathname] || "home";

    const getGreeting = (page) => t(`assistant.greetings.${page}`);

    const [open, setOpen] = useState(false);
    const [msgs, setMsgs] = useState([]);
    const [input, setInput] = useState("");
    const [loading, setLoading] = useState(false);
    const [threadId, setThreadId] = useState(() => uuid());

    const bottomRef = useRef(null);
    const inputRef = useRef(null);

    // Reset on page change
    useEffect(() => {
        setMsgs([{ role: "assistant", text: getGreeting(page), badge: null }]);
        setThreadId(uuid());
    }, [page, i18n.language]);

    // Auto-scroll
    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [msgs, loading]);

    // Focus input
    useEffect(() => {
        if (open) setTimeout(() => inputRef.current?.focus(), 150);
    }, [open]);

    // Execute UI actions
    const executeUIActions = useCallback((actions) => {
        actions.forEach((a) => {
            if (a.ui_action === "guide") {
                const route = PAGE_TO_ROUTE[a.page];
                if (route && route !== loc.pathname) navigate(route);
            }

            if (a.ui_action === "fill_query") {
                window.dispatchEvent(
                    new CustomEvent("assistant-fill-query", { detail: { query: a.query } })
                );
            }

            if (a.ui_action === "fill_sell_form") {
                window.dispatchEvent(
                    new CustomEvent("assistant-fill-sell-form", { detail: a.fields })
                );
            }
        });
    }, [loc.pathname, navigate]);

    // Send message
    const send = async () => {
        const text = input.trim();
        if (!text || loading) return;

        setMsgs(prev => [...prev, { role: "user", text, badge: null }]);
        setInput("");
        setLoading(true);

        try {
            const res = await fetch(`${API}/api/assistant/chat`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: text,
                    thread_id: threadId,
                    current_page: page,
                    page_context: { language: i18n.language }
                }),
            });

            if (!res.ok) throw new Error(`Server ${res.status}`);
            const data = await res.json();

            setThreadId(data.thread_id);
            if (data.ui_actions?.length) executeUIActions(data.ui_actions);

            const badge = data.tools_called?.length
                ? data.tools_called[data.tools_called.length - 1]
                : null;

            setMsgs(prev => [...prev, { role: "assistant", text: data.reply, badge }]);
        } catch (e) {
            setMsgs(prev => [...prev, {
                role: "assistant",
                text: t("assistant.error"),
                badge: null
            }]);
        } finally {
            setLoading(false);
        }
    };

    const onKey = (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            send();
        }
    };

    const reset = () => {
        setThreadId(uuid());
        setMsgs([{ role: "assistant", text: getGreeting(page), badge: null }]);
    };

    // ══════════════════════════════════════════════════
    // RENDER
    // ══════════════════════════════════════════════════
    return (
        <div className="airea-assistant">
            <button
                className={`airea-toggle ${open ? "airea-toggle--open" : ""}`}
                onClick={() => setOpen(o => !o)}
                aria-label="AI Assistant"
            >
                <span className="airea-toggle__icon">{open ? "✕" : "🤖"}</span>
                {!open && <span className="airea-toggle__pulse" />}
            </button>

            {open && (
                <div className="airea-panel">
                    <div className="airea-panel__header">
                        <div className="airea-panel__header-left">
                            <span className="airea-panel__avatar">🏠</span>
                            <div>
                                <div className="airea-panel__title">{t("assistant.title")}</div>
                                <div className="airea-panel__subtitle">
                                    <span className="airea-panel__dot" />
                                    Online · {t(`pages.${page}`)}
                                </div>
                            </div>
                        </div>
                        <button className="airea-panel__reset" onClick={reset} title={t("assistant.newChat")}>
                            ↺
                        </button>
                    </div>

                    <div className="airea-panel__messages">
                        {msgs.map((m, i) => (
                            <div key={i} className={`airea-msg airea-msg--${m.role}`}>
                                {m.badge && BADGE[m.badge] && (
                                    <span className="airea-badge" style={{ background: BADGE[m.badge].color }}>
                                        {BADGE[m.badge].label}
                                    </span>
                                )}
                                <div className="airea-bubble">
                                    {m.text.split("\n").map((line, j) => (
                                        <React.Fragment key={j}>{line}<br /></React.Fragment>
                                    ))}
                                </div>
                            </div>
                        ))}
                        {loading && (
                            <div className="airea-msg airea-msg--assistant">
                                <div className="airea-bubble airea-bubble--typing">
                                    <span className="airea-dot" />
                                    <span className="airea-dot" />
                                    <span className="airea-dot" />
                                </div>
                            </div>
                        )}
                        <div ref={bottomRef} />
                    </div>

                    <div className="airea-panel__input-wrap">
                        <textarea
                            ref={inputRef}
                            className="airea-panel__input"
                            placeholder={t("assistant.placeholder")}
                            value={input}
                            onChange={e => setInput(e.target.value)}
                            onKeyDown={onKey}
                            rows={2}
                            disabled={loading}
                        />
                        <button
                            className="airea-panel__send"
                            onClick={send}
                            disabled={loading || !input.trim()}
                        >
                            {loading ? "…" : "↗"}
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
