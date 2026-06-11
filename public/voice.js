/**
 * Sole Syntax Voice Interface
 * Uses browser-native Web Speech API — no API keys required.
 * Injected into Chainlit via public/ folder.
 */

(function () {
  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    console.warn("Web Speech API not supported in this browser.");
    return;
  }

  let recognition = null;
  let isListening = false;
  let btn = null;

  function speak(text) {
    if (!window.speechSynthesis) return;
    window.speechSynthesis.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.lang = "en-US";
    // Pick a natural voice if available
    const voices = window.speechSynthesis.getVoices();
    const preferred = voices.find(
      (v) => v.name.includes("Samantha") || v.name.includes("Google US English")
    );
    if (preferred) utterance.voice = preferred;
    window.speechSynthesis.speak(utterance);
  }

  function injectButton() {
    // Wait for Chainlit's input area to render
    const inputArea = document.querySelector(".MuiStack-root");
    if (!inputArea || document.getElementById("sole-voice-btn")) return;

    btn = document.createElement("button");
    btn.id = "sole-voice-btn";
    btn.title = "Speak your request";
    btn.innerHTML = "🎤";
    btn.style.cssText = `
      background: #1a1a2e;
      border: 1.5px solid #7c3aed;
      border-radius: 50%;
      width: 38px;
      height: 38px;
      font-size: 18px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-left: 6px;
      transition: background 0.2s;
      flex-shrink: 0;
    `;

    btn.addEventListener("click", toggleListening);
    inputArea.appendChild(btn);
  }

  function toggleListening() {
    if (isListening) {
      recognition.stop();
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
      if (btn) {
        btn.innerHTML = "🔴";
        btn.style.borderColor = "#ef4444";
      }
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      fillAndSubmit(transcript);
    };

    recognition.onerror = (event) => {
      console.error("Speech recognition error:", event.error);
      resetBtn();
    };

    recognition.onend = () => {
      resetBtn();
    };

    recognition.start();
  }

  function resetBtn() {
    isListening = false;
    if (btn) {
      btn.innerHTML = "🎤";
      btn.style.borderColor = "#7c3aed";
    }
  }

  function fillAndSubmit(text) {
    // Find Chainlit's textarea and submit button
    const textarea = document.querySelector("#chat-input");
    const submitBtn = document.querySelector('[data-testid="send-button"]');

    if (textarea) {
      // React-controlled input — need to trigger synthetic event
      const nativeInputSetter = Object.getOwnPropertyDescriptor(
        window.HTMLTextAreaElement.prototype,
        "value"
      ).set;
      nativeInputSetter.call(textarea, text);
      textarea.dispatchEvent(new Event("input", { bubbles: true }));

      // Small delay then submit
      setTimeout(() => {
        if (submitBtn) submitBtn.click();
      }, 150);
    }
  }

  // Watch for new assistant messages and read them aloud
  function observeMessages() {
    const observer = new MutationObserver(() => {
      const messages = document.querySelectorAll(".message-content p");
      if (messages.length === 0) return;
      const last = messages[messages.length - 1];
      if (last && last.dataset.spoken !== "true") {
        last.dataset.spoken = "true";
        // Only speak assistant messages (not the welcome message on load)
        const isAssistant = last.closest(".assistant");
        if (isAssistant) speak(last.innerText);
      }
    });

    const chatContainer = document.querySelector("#chat-messages");
    if (chatContainer) {
      observer.observe(chatContainer, { childList: true, subtree: true });
    }
  }

  // Poll until Chainlit renders
  const interval = setInterval(() => {
    injectButton();
    if (document.getElementById("sole-voice-btn")) {
      observeMessages();
      clearInterval(interval);
    }
  }, 800);
})();
