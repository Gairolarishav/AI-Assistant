let currentUserId = '';

function openTranscriptModal(userId) {
  currentUserId = userId;
  console.log('currentUserId==', currentUserId)
  fetchTranscript(userId);           // Show latest by default

  const panel = document.getElementById("transcriptPanel");
  panel.style.display = "flex";
  setTimeout(() => panel.classList.add("show"), 10);
}

function fetchTranscript(userId, sessionId = "") {
  const contentContainer = document.getElementById("transcriptContent");
  contentContainer.innerHTML = "Loading...";

  const url = `/fastpromos/transcript/?user_id=${userId}`;

  fetch(url)
    .then(res => res.json())
    .then(data => displayTranscript(data.transcript || []))
    .catch(err => {
      contentContainer.innerHTML = "Error loading transcript.";
      console.error("Transcript error:", err);
    });
}

function displayTranscript(transcript) {
  const contentContainer = document.getElementById("transcriptContent");
  contentContainer.innerHTML = "";

  if (transcript.length === 0) {
    contentContainer.innerHTML = "<p>No messages for this session.</p>";
    return;
  }

  transcript.forEach(entry => {
    const msgDiv = document.createElement("div");
    
    // ✅ Check if this is a session separator message
    if (entry.source === 'system' && entry.text.includes('New Chat Session Started')) {
      msgDiv.className = 'chat-message session-separator';
      msgDiv.textContent = entry.text;
    } else {
      msgDiv.className = `chat-message ${entry.source}`;
      msgDiv.textContent = entry.text;
    }
    
    contentContainer.appendChild(msgDiv);
  });
}

function closeTranscriptPanel() {
  const panel = document.getElementById("transcriptPanel");
  panel.classList.remove("show");
  setTimeout(() => panel.style.display = "none", 300);
}
