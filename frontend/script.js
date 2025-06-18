const chatDiv = document.getElementById("chat");
const form    = document.getElementById("chat-form");
const promptI = document.getElementById("prompt");

function escapeHtml(str) {
  return str.replace(/&/g,"&amp;")
            .replace(/</g,"&lt;")
            .replace(/>/g,"&gt;");
}

function appendMessage(role, text, snippets) {
  const m = document.createElement("div");
  m.className = "message " + role;

  // Meta line
  const meta = document.createElement("div");
  meta.className = "meta";
  meta.textContent = role === "user" ? "You" : "Assistant";
  m.appendChild(meta);

  // Content container
  const content = document.createElement("div");
  content.className = "content";
  const parts = text.split(/(\[\d+\.\d+s→\d+\.\d+s\])/g);
  for (let part of parts) {
    if (!part) continue;
    if (/^\[\d+\.\d+s→\d+\.\d+s\]$/.test(part) && snippets[part]) {
      const btn = document.createElement("button");
      btn.className = "snippet-link";
      btn.textContent = part;
      btn.onclick = () => playSnippet(part, snippets[part], m);
      content.appendChild(btn);
    } else {
      const span = document.createElement("span");
      span.innerHTML = escapeHtml(part);
      content.appendChild(span);
    }
  }
  m.appendChild(content);

  // Audio container (initially empty, will be filled by playSnippet)
  const audioContainer = document.createElement("div");
  audioContainer.className = "audio-container";
  m.appendChild(audioContainer);

  chatDiv.appendChild(m);
  chatDiv.scrollTop = chatDiv.scrollHeight;
}

function playSnippet(token, url, messageEl) {
  const audioContainer = messageEl.querySelector(".audio-container");
  audioContainer.innerHTML = "";  // clear any previous player

  const mediaSource = new MediaSource();
  const audio = document.createElement("audio");
  audio.controls = true;
  audio.src = URL.createObjectURL(mediaSource);
  audioContainer.appendChild(audio);

  mediaSource.addEventListener("sourceopen", () => {
    const sb = mediaSource.addSourceBuffer("audio/mpeg");
    const ws = new WebSocket("ws://localhost:8000/ws-snippet");
    ws.binaryType = "arraybuffer";
    ws.onopen = () => {
      const params = new URL(url).searchParams;
      ws.send(JSON.stringify({
        path:  params.get("path"),
        start: parseFloat(params.get("start")),
        end:   parseFloat(params.get("end"))
      }));
    };
    ws.onmessage = evt => {
      sb.appendBuffer(new Uint8Array(evt.data));
      if (audio.paused) audio.play();
    };
    ws.onclose = () => mediaSource.endOfStream();
  });
}

form.addEventListener("submit", async e => {
  e.preventDefault();
  const prompt = promptI.value.trim();
  if (!prompt) return;
  appendMessage("user", prompt, {});
  promptI.value = "";

  const res = await fetch("/chat", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({ prompt })
  });
  const { response, snippets } = await res.json();
  appendMessage("assistant", response, snippets);
});