// DOM references for the chat UI
// chatContainer: holds all chat message elements
// userInput: text input where the user types their message
// loading: visual indicator shown while waiting for the model response

const chatContainer = document.getElementById('chatContainer');
const userInput = document.getElementById('userInput');
const loading = document.getElementById('loading');

const completeSetupBtn = document.getElementById('completeSetupBtn');
const setupLastPeriodInput = document.getElementById('setupLastPeriod');
const setupCycleLengthInput = document.getElementById('setupCycleLength');
const setupScreen = document.getElementById('setupScreen');

let userLastPeriodDate = null;
let userCycleLength = 28;

completeSetupBtn.addEventListener('click', () => {
    const lastPeriod = setupLastPeriodInput.value;
    const cycleLength = setupCycleLengthInput.value || 28;

    if (!lastPeriod) {
        alert("Please enter the start date of your last period.");
        return;
    }

    userLastPeriodDate = lastPeriod;
    userCycleLength = Number(cycleLength);

    // Persist so refresh doesn’t wipe state
    localStorage.setItem('lastPeriodDate', lastPeriod);
    localStorage.setItem('cycleLength', userCycleLength);

    // Hide setup screen
    setupScreen.style.display = 'none';
});



async function calculateCyclePhase(lastPeriodDate, cycleLength) {
    const response = await fetch('http://127.0.0.1:5000/api/calculate-cycle', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            last_period_date: lastPeriodDate,
            cycle_length: cycleLength,
            current_date: new Date().toISOString().split('T')[0]
        })
    });
    
    if (!response.ok) {
        throw new Error('Failed to calculate cycle phase');
    }
    
    const data = await response.json();
    
    if (!data.success) {
        throw new Error(data.error || 'Unknown error occurred');
    }
    console.log(data);
    return data;
}


// Main function triggered when the user sends a message
// Handles input validation, API communication, and UI updates
async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    // Render the user's message in the chat UI
    addMessage(message, 'user');
    // Clear the input field for better UX
    userInput.value = '';
    // Display loading indicator while waiting for the LLM response
    loading.style.display = 'block';

    try {
        // Wait for cycle info from backend
        if (!userLastPeriodDate) {
            addMessage("Please complete the setup so I can understand your cycle 💕", "assistant");
            loading.style.display = "none";
            return;
        }
        
        const cycleInfo = await calculateCyclePhase(
            userLastPeriodDate,
            userCycleLength
        );
        
        // const cycleInfo = await calculateCyclePhase("2025-12-16", 28);
        const cycleInfoText = `The user is currently on cycle day ${cycleInfo.cycle_day}, in the ${cycleInfo.phase}.`;
        console.log("Cycle info being sent:", cycleInfoText);

        // Send user message to OpenRouter's Chat Completions API
        const response = await fetch("https://openrouter.ai/api/v1/chat/completions",
        {
            method: 'POST',
            headers: {
                // API authentication
                Authorization: 'Bearer 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',
                "HTTP-Referer": "https://www.menstrual-health-chatbot.com",
                "X-Title": "menstrual-health-chatbot",
                // JSON request body
                "Content-Type": "application/json",},
            body: JSON.stringify({
                model: "mistralai/mistral-7b-instruct:free",
                max_tokens: 1000,
                // Single-turn prompt that:
                    // 1. Sets system-level persona and behavioral constraints
                    // 2. Injects the user's message for contextual response
                messages: [{
                    role: 'user',
                    content: `You are Luna, a compassionate AI health companion specializing in menstrual health and hormonal science. A user is sharing their symptoms or experiences. 
                    Provide validation and scientifically-backed insights about how their symptoms relate to hormonal cycles. Be warm, supportive, and informative. Keep responses concise but meaningful. Avoid medical diagnosis. 
                    ${cycleInfoText}
                    User message: ${message}`}]})});
        // Parse the JSON response from the API
        const data = await response.json();
        // Safely extract the assistant's reply using optional chaining
        // Fallback message ensures UI never breaks on malformed responses
        let markdownText =
            data.choices?.[0]?.message?.content ||
            "I'm sorry — I couldn't generate a response.";
        
        markdownText = markdownText.replace(/~~/g, '');
        // Render the assistant's reply in the chat UI
        addMessage(markdownText, 'assistant');
    } catch (error) {
        // Display error message in the chat UI
        addMessage("Error: " + error.message, 'assistant');
    } finally {
        // Hide loading indicator when response is complete or in case of error
        loading.style.display = "none";
    }
}

// Helper function to append a message to the chat container
// sender: 'user' or 'assistant' (used for styling and rendering logic)
function addMessage(text, sender) {
    // Create a new message container element
    // Outer message wrapper (controls alignment and spacing)
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    // Inner message bubble (contains actual content)
    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'message-bubble';
    
    // Render assistant messages as Markdown if the marked library is available
    // User messages are rendered as plain text to prevent injection
    if (sender === 'assistant' && typeof marked !== 'undefined') {
        // marked library is used to render Markdown content in the chat UI
        bubbleDiv.innerHTML = marked.parse(text);
    } else {
        bubbleDiv.textContent = text;
    }
    // Append bubble to message wrapper, then to the chat container
    messageDiv.appendChild(bubbleDiv);
    chatContainer.appendChild(messageDiv);
    // Auto-scroll to the newest message
    chatContainer.scrollTop = chatContainer.scrollHeight;
}
