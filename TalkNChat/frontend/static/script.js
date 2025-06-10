/**
 * Flask Chat Application Frontend JavaScript
 * This script handles the client-side logic for the chat application
 * including user authentication, messaging, and file uploads.
 */

// Store current user and recipient information
let currentUsername = "";
let currentRecipient = "";
let pollingInterval;

/**
 * Check if an element exists in the DOM
 * @param {string} id - Element ID to check
 * @returns {boolean} - Whether the element exists
 */
function elementExists(id) {
    return document.getElementById(id) !== null;
}

/**
 * Safely set text content on an element, only if it exists
 * @param {string} id - Element ID
 * @param {string} text - Text content to set
 * @returns {boolean} - Whether the operation succeeded
 */
function safeSetTextContent(id, text) {
    const element = document.getElementById(id);
    if (element) {
        element.textContent = text;
        return true;
    }
    console.warn(`Element with ID "${id}" not found when trying to set text: ${text}`);
    return false;
}

/**
 * Safely add an event listener to an element, only if it exists
 * @param {string} id - Element ID
 * @param {string} event - Event name
 * @param {Function} handler - Event handler function
 * @returns {boolean} - Whether the operation succeeded
 */
function safeAddEventListener(id, event, handler) {
    const element = document.getElementById(id);
    if (element) {
        element.addEventListener(event, handler);
        return true;
    }
    console.warn(`Element with ID "${id}" not found when trying to add ${event} listener`);
    return false;
}

/**
 * Fetch the current user's username from the session
 * Redirects to login page if not authenticated
 */
async function getUsername() {
    try {
        let response = await fetch("/get-username");
        let data = await response.json();

        if (response.status !== 200 || data.error) {
            alert("You need to log in first!");
            window.location.href = "/login";
            return;
        }

        currentUsername = data.username;

        loadContacts();
    } catch (error) {
        console.error("Error fetching username:", error);
        alert("An error occurred while fetching your username. Please try again.");
        window.location.href = "/login";
    }
}

/**
 * Load contacts (users the current user has messaged)
 */
async function loadContacts() {
    try {
        let response = await fetch("/get-messaged-users");
        let data = await response.json();

        if (response.status !== 200 || data.error) {
            alert(data.error || "Failed to load contacts");
            return;
        }

        const contactsDiv = document.getElementById("contacts");
        if (!contactsDiv) {
            console.error("Contacts container not found in the DOM");
            return;
        }

        contactsDiv.innerHTML = "";

        if (data.users.length === 0) {
            let noContactsElement = document.createElement("div");
            noContactsElement.textContent = "No contacts yet. Search for users to start a conversation.";
            noContactsElement.className = "no-contacts";
            contactsDiv.appendChild(noContactsElement);
            return;
        }

        data.users.forEach(user => {
            let contactElement = document.createElement("div");
            contactElement.className = "contact";
            contactElement.textContent = user;
            contactElement.onclick = () => loadMessages(user);
            contactsDiv.appendChild(contactElement);
        });
    } catch (error) {
        console.error("Error loading contacts:", error);
        alert("An error occurred while loading your contacts. Please try again.");
    }
}

/**
 * Search for users by name
 */
async function searchUsers() {
    try {
        const searchInput = document.getElementById("searchInput");
        if (!searchInput) {
            console.error("Search input element not found");
            return;
        }

        let query = searchInput.value;
        if (query.trim() === "") {
            loadContacts();
            return;
        }

        let response = await fetch(`/search-users?query=${encodeURIComponent(query)}`);
        let data = await response.json();

        if (response.status !== 200 || data.error) {
            alert(data.error || "Failed to search users");
            return;
        }

        const contactsDiv = document.getElementById("contacts");
        if (!contactsDiv) {
            console.error("Contacts container not found in the DOM");
            return;
        }

        contactsDiv.innerHTML = "";

        if (data.users.length === 0) {
            let noResultsElement = document.createElement("div");
            noResultsElement.textContent = "No users found";
            noResultsElement.className = "no-results";
            contactsDiv.appendChild(noResultsElement);
            return;
        }

        data.users.forEach(user => {
            let contactElement = document.createElement("div");
            contactElement.className = "contact";
            contactElement.textContent = user;
            contactElement.onclick = () => loadMessages(user);
            contactsDiv.appendChild(contactElement);
        });
    } catch (error) {
        console.error("Error searching users:", error);
        alert("An error occurred while searching for users. Please try again.");
    }
}

/**
 * Escape HTML to prevent XSS attacks
 * @param {string} text - The text to escape
 * @returns {string} - The escaped text
 */
function escapeHTML(text) {
    let element = document.createElement('div');
    element.innerText = text;
    return element.innerHTML;
}

/**
 * Convert URLs in text to clickable links
 * @param {string} text - The text to convert
 * @returns {string} - The text with URLs converted to clickable links
 */
function linkify(text) {
    const urlPattern = /(\b(https?|ftp|file):\/\/[-A-Z0-9+&@#\/%?=~_|!:,.;]*[-A-Z0-9+&@#\/%=~_|])/ig;
    return text.replace(urlPattern, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');
}

/**
 * Format timestamp to local time
 * @param {string} timestamp - ISO timestamp string
 * @returns {string} - Formatted timestamp
 */
function formatTimestamp(timestamp) {
    try {
        const date = new Date(timestamp);
        return date.toLocaleString();
    } catch (error) {
        console.error("Error formatting timestamp:", error);
        return timestamp; // Return original timestamp if formatting fails
    }
}

/**
 * Load messages for a specific user
 * @param {string} recipient - Username of the recipient
 */
async function loadMessages(recipient) {
    try {
        currentRecipient = recipient;

        // Safely set recipient input value
        const recipientInput = document.getElementById("recipientInput");
        if (recipientInput) {
            recipientInput.value = recipient;
        } else {
            console.error("Recipient input element not found");
        }

        const response = await fetch(`/get-messages/${encodeURIComponent(recipient)}`);
        const data = await response.json();

        if (response.status !== 200 || data.error) {
            alert(data.error || "Failed to load messages");
            return;
        }

        displayMessages(data.messages);

        // Start polling for new messages
        startPolling();
    } catch (error) {
        console.error("Error loading messages:", error);
        alert("An error occurred while loading messages. Please try again.");
    }
}

/**
 * Display messages in the chat box
 * @param {Array} messages - Array of message objects
 */
function displayMessages(messages) {
    const chatBox = document.getElementById("messages");
    if (!chatBox) {
        console.error("Chat box element not found");
        return;
    }

    chatBox.innerHTML = "";

    if (messages.length === 0) {
        const emptyMessageElement = document.createElement("div");
        emptyMessageElement.className = "empty-messages";
        emptyMessageElement.textContent = "No messages yet. Start a conversation!";
        chatBox.appendChild(emptyMessageElement);
        return;
    }

    messages.forEach(messageData => {
        const messageElement = document.createElement("div");
        messageElement.classList.add("chat-message");
        messageElement.classList.add(messageData.username === currentUsername ? "user" : "other");

        // Process message text (escape HTML and linkify URLs)
        let messageText = escapeHTML(messageData.message);
        messageText = linkify(messageText);

        // Include file download button if a file is attached
        let fileButton = "";
        if (messageData.file_url) {
            const fileName = messageData.file_url.split('/').pop(); // Extract file name
            fileButton = `
                <br>
                <a href="${messageData.file_url}" target="_blank" download>
                    <button class="download-button">📥 Download ${fileName}</button>
                </a>
            `;
        }

        // Create message content
        messageElement.innerHTML = `
            <span>
                <div class="text">${messageText}${fileButton}</div>
                <div class="username">${messageData.username} - ${formatTimestamp(messageData.timestamp)}</div>
            </span>
        `;

        chatBox.appendChild(messageElement);
    });

    // Auto-scroll to latest message
    chatBox.scrollTop = chatBox.scrollHeight;
}


/**
 * Start polling for new messages
 */
function startPolling() {
    if (pollingInterval) {
        clearInterval(pollingInterval);
    }

    pollingInterval = setInterval(async () => {
        if (currentRecipient) {
            try {
                const response = await fetch(`/poll-messages/${encodeURIComponent(currentRecipient)}`);
                const data = await response.json();

                if (response.status !== 200 || data.error) {
                    console.error("Polling error:", data.error);
                    return;
                }

                displayMessages(data.messages);
            } catch (error) {
                console.error("Error polling messages:", error);
            }
        }
    }, 5000); // Poll every 5 seconds
}

/**
 * Send a message to the current recipient
 */
async function sendMessage() {
    try {
        const messageInput = document.getElementById("messageInput");
        const recipientInput = document.getElementById("recipientInput");
        const fileInput = document.getElementById("fileInput");
        const sendButton = document.getElementById("sendButton");

        // Check if elements exist
        if (!messageInput) {
            console.error("Message input element not found");
            alert("Error: Message input field not found");
            return;
        }

        if (!recipientInput) {
            console.error("Recipient input element not found");
            alert("Error: Recipient field not found");
            return;
        }

        // Validate inputs
        if (!recipientInput.value.trim()) {
            alert("Please select a recipient");
            return;
        }

        // Check if file input exists before checking files
        let hasFile = false;
        if (fileInput && fileInput.files.length > 0) {
            hasFile = true;
        }

        if (!messageInput.value.trim() && !hasFile) {
            alert("Please enter a message or select a file");
            return;
        }

        currentRecipient = recipientInput.value.trim();

        // Create form data
        const formData = new FormData();
        formData.append("message", messageInput.value);

        if (hasFile) {
            formData.append("file", fileInput.files[0]);
        }

        // Show sending indicator if button exists
        let originalText = "Send";
        if (sendButton) {
            originalText = sendButton.textContent;
            sendButton.textContent = "Sending...";
            sendButton.disabled = true;
        }

        // Send the message
        const response = await fetch(`/send-message?recipient=${encodeURIComponent(currentRecipient)}`, {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        // Reset button state if it exists
        if (sendButton) {
            sendButton.textContent = originalText;
            sendButton.disabled = false;
        }

        if (response.status !== 200 || data.error) {
            alert(data.error || "Failed to send message");
            return;
        }

        // Clear inputs
        messageInput.value = "";
        if (fileInput) {
            fileInput.value = "";
        }

        // Reload messages to show the new message
        loadMessages(currentRecipient);
    } catch (error) {
        console.error("Error sending message:", error);
        alert("An error occurred while sending your message. Please try again.");

        // Reset button state if it exists
        const sendButton = document.getElementById("sendButton");
        if (sendButton) {
            sendButton.textContent = "Send";
            sendButton.disabled = false;
        }
    }
}

/**
 * Handle file input change
 */
function handleFileInputChange() {
    const fileInput = document.getElementById("fileInput");

    if (!fileInput) {
        console.error("File input element not found");
        return;
    }

    if (fileInput.files.length > 0) {
        console.log(`File selected: ${fileInput.files[0].name}`);
    } else {
        console.log("No file selected");
    }
}

/**
 * Handle message input key press
 * @param {KeyboardEvent} event - The keyboard event
 */
function handleMessageKeyPress(event) {
    if (event.key === "Enter" && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

/**
 * Logout function
/**
 * Logout function
 */
function logout() {
    window.location.href = "/logout";
}

/**
 * Initialize the chat application
 */
function initChat() {
    // Set up event listeners
    document.getElementById("searchInput").addEventListener("input", searchUsers);
    document.getElementById("messageInput").addEventListener("keypress", handleMessageKeyPress);
    document.getElementById("fileInput").addEventListener("change", handleFileInputChange);

    // Initialize application state
    getUsername();

    // Clean up when navigating away
    window.addEventListener("beforeunload", () => {
        if (pollingInterval) {
            clearInterval(pollingInterval);
        }
    });
}

// Initialize on page load
document.addEventListener("DOMContentLoaded", initChat);