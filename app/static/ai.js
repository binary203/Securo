document.addEventListener('DOMContentLoaded', () => {
    let currentLanguage = 'ru';
    let attachedCode = null;
    let conversationHistory = [];

    const overlay = document.getElementById('overlay');
    const chatContainer = document.getElementById('chatContainer');
    const chatMessages = document.getElementById('chatMessages');
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const closeChat = document.getElementById('closeChat');
    const aiAssistBtn = document.getElementById('AiAssist');
    const loadingMessage = document.getElementById('loadingMessage');
    const codePreview = document.getElementById('codePreview');
    const codePreviewContent = document.getElementById('codePreviewContent');
    const removeSnippet = document.getElementById('removeSnippet');
    const errorBubble = document.getElementById('errorBubble');
    const chatStatus = document.getElementById('chatStatus');

    if (!overlay || !chatContainer || !aiAssistBtn) return;

    // Выбор языка
    const langButtons = document.querySelectorAll('.lang-btn');
    langButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            langButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentLanguage = btn.dataset.lang;
            updatePlaceholder();
        });
    });

    function updatePlaceholder() {
        if (currentLanguage === 'ru') {
            chatInput.placeholder = '/explain, /fix, /improve или задай вопрос...';
        } else {
            chatInput.placeholder = 'Type /explain, /fix, /improve or ask a question...';
        }
    }

    // Кнопки команд
    const commandButtons = document.querySelectorAll('.command-btn');
    commandButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const command = btn.dataset.command;
            chatInput.value = command + ' ';
            chatInput.focus();
            commandButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });

    chatInput.addEventListener('input', () => {
        if (!chatInput.value.startsWith('/explain') &&
            !chatInput.value.startsWith('/fix') &&
            !chatInput.value.startsWith('/improve')) {
            commandButtons.forEach(b => b.classList.remove('active'));
        }
        chatInput.style.height = 'auto';
        chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
    });

    // Открытие чата
    aiAssistBtn.addEventListener('click', () => {
        overlay.classList.add('show');
        chatContainer.classList.add('show');
        chatInput.focus();
        extractVulnerabilityCode();
    });

    // Закрытие чата
    closeChat.addEventListener('click', closeAIChat);
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) closeAIChat();
    });

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && overlay.classList.contains('show')) {
            closeAIChat();
        }
    });

    function closeAIChat() {
        overlay.classList.remove('show');
        chatContainer.classList.remove('show');
    }

    function extractVulnerabilityCode() {
        if (attachedCode) return;
        const vulnerabilityCards = document.querySelectorAll('.vulnerability-card');
        if (vulnerabilityCards.length === 0) return;

        let allCode = '';
        vulnerabilityCards.forEach((card, index) => {
            const codeElement = card.querySelector('.vulnerability-code');
            if (codeElement) {
                allCode += `// Уязвимость #${index + 1}\n${codeElement.textContent}\n\n`;
            }
        });

        if (allCode.trim()) {
            attachedCode = allCode.trim();
            showCodePreview(attachedCode);
        }
    }

    function showCodePreview(code) {
        codePreviewContent.textContent = code;
        codePreview.classList.add('show');
    }

    removeSnippet.addEventListener('click', () => {
        attachedCode = null;
        codePreview.classList.remove('show');
    });

    // Отправка сообщения
    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    async function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        errorBubble.classList.remove('show');
        addMessage(message, 'user');

        chatInput.value = '';
        chatInput.style.height = 'auto';

        loadingMessage.classList.add('show');
        chatMessages.scrollTop = chatMessages.scrollHeight;
        sendBtn.disabled = true;
        chatStatus.textContent = 'Думаю...';

        try {
            let userCommand = message;
            let isCommand = message.startsWith('/explain') ||
                            message.startsWith('/fix') ||
                            message.startsWith('/improve');

            let codeSnippetToSend = attachedCode || '';

            if (isCommand) {
                const spaceIndex = message.indexOf(' ');
                if (spaceIndex !== -1) {
                    userCommand = message.substring(0, spaceIndex);
                    const manualCode = message.substring(spaceIndex + 1).trim();
                    if (!codeSnippetToSend && manualCode.length > 0) {
                        codeSnippetToSend = manualCode;
                    }
                }
            }

            const requestData = {
                user_command: userCommand,
                AI_lang: currentLanguage,
                code_snippet: codeSnippetToSend
            };

            const response = await fetch('/api/ai', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(requestData)
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Ошибка сервера');
            }

            const data = await response.json();
            addMessage(data.reply, 'ai');

            conversationHistory.push({ user: message, ai: data.reply });
            chatStatus.textContent = 'Готов к работе';

        } catch (error) {
            console.error('Error:', error);
            showError(error.message);
            chatStatus.textContent = 'Ошибка!';
        } finally {
            loadingMessage.classList.remove('show');
            sendBtn.disabled = false;
            chatInput.focus();
        }
    }

    function addMessage(text, type) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = type === 'user' ? '👤' : '🤖';

        const content = document.createElement('div');
        content.className = 'message-content';

        const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g;
        let lastIndex = 0;
        let match;

        while ((match = codeBlockRegex.exec(text)) !== null) {
            if (match.index > lastIndex) {
                const span = document.createElement('span');
                span.textContent = text.substring(lastIndex, match.index);
                span.innerHTML = span.innerHTML.replace(/\n/g, '<br>');
                content.appendChild(span);
            }
            const pre = document.createElement('pre');
            const code = document.createElement('code');
            code.textContent = match[2];
            pre.appendChild(code);
            content.appendChild(pre);
            lastIndex = match.index + match[0].length;
        }

        if (lastIndex < text.length) {
            const span = document.createElement('span');
            span.textContent = text.substring(lastIndex);
            span.innerHTML = span.innerHTML.replace(/\n/g, '<br>');
            content.appendChild(span);
        }

        const time = document.createElement('div');
        time.className = 'message-time';
        time.textContent = new Date().toLocaleTimeString('ru-RU', {
            hour: '2-digit',
            minute: '2-digit'
        });
        content.appendChild(time);

        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);

        chatMessages.insertBefore(messageDiv, loadingMessage);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function showError(message) {
        errorBubble.textContent = `❌ ${message}`;
        errorBubble.classList.add('show');
        setTimeout(() => errorBubble.classList.remove('show'), 5000);
    }
});
