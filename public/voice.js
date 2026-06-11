/**
 * Sole Syntax Voice Interface — floating mic button
 * Uses browser Web Speech API (STT) + speechSynthesis (TTS). Zero cost.
 */
(function () {
  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;

  // ── Floating mic button ────────────────────────────────────────────────────
  function createFloatingButton() {
    if (document.getElementById("sole-mic-fab")) return;

    const fab = document.createElement("button");
    fab.id = "sole-mic-fab";
    fab.title = "Speak your request (Web Speech API)";
    fab.innerHTML = "🎤";
    fab.style.cssText = `
      position: fixed;
      bottom: 110px;
      right: 24px;
      z-index: 9999;
      width: 52px;
      height: 52px;
      border-radius: 50%;
      background: linear-gradient(135deg, #7c3aed, #4f46e5);
      border: none;
      color: white;
      font-size: 22px;
      cursor: pointer;
      box-shadow: 0 4px 14px rgba(124,58,237,0.5);
      display: flex;
      align-items: center;
      justify-content: center;
      transition: transform 0.15s, box-shadow 0.15s;
    `;
    fab.addEventListener("mouseenter", () => {
      fab.style.transform = "scale(1.1)";
      fab.style.boxShadow = "0 6px 20px rgba(124,58,237,0.7)";
    });
    fab.addEventListener("mouseleave", () => {
      fab.style.transform = "scale(1)";
      fab.style.boxShadow = "0 4px 14px rgba(124,58,237,0.5)";
    });

    if (!SpeechRecognition) {
      fab.title = "Voice not supported in this browser";
      fab.style.opacity = "0.4";
      fab.style.cursor = "not-allowed";
    } else {
      fab.addEventListener("click", toggleListening);
    }

    document.body.appendChild(fab);
  }

  // ── Speech recognition ─────────────────────────────────────────────────────
  let recognition = null;
  let isListening = false;

  function toggleListening() {
    if (isListening) {
      recognition && recognition.stop();
    } else {
      startListening();
    }
  }

  function startListening() {
    recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      isListening = true;
      const fab = document.getElementById("sole-mic-fab");
      if (fab) {
        fab.innerHTML = "🔴";
        fab.style.background = "linear-gradient(135deg, #ef4444, #dc2626)";
        fab.style.boxShadow = "0 4px 14px rgba(239,68,68,0.6)";
      }
    };

    recognition.onresult = (e) => {
      const transcript = e.results[0][0].transcript;
      fillAndSubmit(transcript);
    };

    recognition.onerror = () => resetFab();
    recognition.onend = () => resetFab();
    recognition.start();
  }

  function resetFab() {
    isListening = false;
    const fab = document.getElementById("sole-mic-fab");
    if (fab) {
      fab.innerHTML = "🎤";
      fab.style.background = "linear-gradient(135deg, #7c3aed, #4f46e5)";
      fab.style.boxShadow = "0 4px 14px rgba(124,58,237,0.5)";
    }
  }

  function fillAndSubmit(text) {
    // Find Chainlit's textarea by placeholder or tag
    const textarea =
      document.querySelector('textarea[placeholder]') ||
      document.querySelector("textarea");

    if (!textarea) return;

    // Trigger React's synthetic input event
    const nativeSetter = Object.getOwnPropertyDescriptor(
      window.HTMLTextAreaElement.prototype,
      "value"
    ).set;
    nativeSetter.call(textarea, text);
    textarea.dispatchEvent(new Event("input", { bubbles: true }));

    // Give React a moment to update state then click submit
    setTimeout(() => {
      const submitBtn =
        document.querySelector('button[type="submit"]') ||
        document.querySelector("button[data-testid='send-button']") ||
        [...document.querySelectorAll("button")].find(
          (b) => b.querySelector("svg") && b.style.background?.includes("rgb")
        );
      if (submitBtn) submitBtn.click();
    }, 200);
  }

  // ── Text-to-Speech for assistant replies ───────────────────────────────────
  let lastSpokenText = "";

  function observeAndSpeak() {
    const target = document.querySelector("#chat-messages") || document.body;
    const observer = new MutationObserver(() => {
      // Find all assistant message paragraphs
      const paras = document.querySelectorAll(
        '.message[data-author="assistant"] p, .assistant p, [class*="assistant"] p'
      );
      if (!paras.length) return;
      const last = paras[paras.length - 1];
      const text = last.innerText?.trim();
      if (text && text !== lastSpokenText) {
        lastSpokenText = text;
        speak(text);
      }
    });
    observer.observe(target, { childList: true, subtree: true });
  }

  function speak(text) {
    if (!window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const utt = new SpeechSynthesisUtterance(text);
    utt.lang = "en-US";
    utt.rate = 1.05;
    const voices = window.speechSynthesis.getVoices();
    const preferred = voices.find(
      (v) =>
        v.name.includes("Samantha") ||
        v.name.includes("Google US English") ||
        v.name.includes("Microsoft Aria")
    );
    if (preferred) utt.voice = preferred;
    window.speechSynthesis.speak(utt);
  }

  // ── Boot ───────────────────────────────────────────────────────────────────
  function boot() {
    createFloatingButton();
    observeAndSpeak();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    // Chainlit is a SPA — wait a tick for React to mount
    setTimeout(boot, 800);
  }
})();
