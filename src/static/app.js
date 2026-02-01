let sessionId = null;
const setupPanel = document.getElementById("setup-panel");
const gamePanel = document.getElementById("game-panel");
const chatLog = document.getElementById("chat-log");
const userInput = document.getElementById("user-input");

async function startSession() {
    const campaignType = document.getElementById("campaign-type").value;

    // Simulate loading state
    setupPanel.innerHTML = "<p>Generating World...</p>";

    try {
        const response = await fetch("/session/start", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ campaign_type: campaignType })
        });

        const data = await response.json();

        sessionId = data.session_id;
        setupPanel.style.display = "none";
        gamePanel.style.display = "flex";

        addMessage("dm-message", data.intro_narrative);
    } catch (error) {
        console.error("Error starting session:", error);
        alert("Failed to start session. Check console.");
    }
}

async function sendAction() {
    const text = userInput.value;
    if (!text) return;

    addMessage("user-message", text);
    userInput.value = "";

    try {
        const response = await fetch("/interact", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                user_id: "user1",
                character_id: "char1",
                session_id: sessionId,
                input_text: text
            })
        });

        const data = await response.json();

        if (data.narrative) {
            addMessage("dm-message", data.narrative);
        }
    } catch (error) {
        console.error("Error sending action:", error);
        addMessage("dm-message", "[System Error: Connection Lost]");
    }
}

function addMessage(className, text) {
    const div = document.createElement("div");
    div.className = `message ${className}`;
    div.textContent = text;
    chatLog.appendChild(div);
    chatLog.scrollTop = chatLog.scrollHeight;
}

// Allow Enter key to submit
userInput.addEventListener("keypress", function(event) {
    if (event.key === "Enter") {
        sendAction();
    }
});
