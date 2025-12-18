const aiButton = document.getElementById("AiAssist");
const explainBtn = document.getElementById("explainBtn");
const fixBtn = document.getElementById("fixBtn");
const improveBtn = document.getElementById("improveBtn");
const popup = document.getElementById("popup");
const closeBtn = document.getElementById("close");
const overlay = document.getElementById("overlay");

// Открытие попапа
aiButton.addEventListener("click", () => {
    popup.classList.add("show");
    overlay.classList.add("show");
});

// Закрытие попапа
closeBtn.addEventListener("click", () => {
    popup.classList.remove("show");
    overlay.classList.remove("show");
});

// Закрытие при клике на overlay
overlay.addEventListener("click", (e) => {
    if (e.target === overlay) {
        popup.classList.remove("show");
        overlay.classList.remove("show");
    }
});

// Функция для сбора данных об уязвимостях
function collectVulnerabilities() {
    const vulnerabilities = [];
    const vulnCards = document.querySelectorAll('.vulnerability-card');
    
    vulnCards.forEach((card, index) => {
        const title = card.querySelector('.vulnerability-title')?.textContent.trim() || `Уязвимость #${index + 1}`;
        const severity = card.querySelector('.severity-badge')?.textContent.trim() || 'unknown';
        const meta = card.querySelector('.vulnerability-meta')?.textContent.trim() || '';
        const description = card.querySelector('.vulnerability-description')?.textContent.trim() || '';
        const code = card.querySelector('pre')?.textContent.trim() || '';
        
        vulnerabilities.push({
            title,
            severity,
            meta,
            description,
            code
        });
    });

    return vulnerabilities.map((v, i) => 
        `\n=== Уязвимость ${i + 1} ===\n` +
        `Название: ${v.title}\n` +
        `Уровень: ${v.severity}\n` +
        `${v.meta}\n` +
        `${v.description}\n` +
        (v.code ? `Код:\n${v.code}\n` : '')
    ).join('\n');
}

// Функция для отправки запроса к ИИ
async function sendToAI(command, buttonElement) {
    try {
        // Показываем индикатор загрузки
        const originalText = buttonElement.textContent;
        buttonElement.disabled = true;
        buttonElement.textContent = "⏳ Обработка...";

        // Собираем все найденные уязвимости
        const vulnerabilitiesText = collectVulnerabilities();
        const codeSnippet = `Найдены следующие уязвимости:\n${vulnerabilitiesText}`;

        // Отправляем запрос к API
        const response = await fetch('/api/ai', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                user_command: command,
                AI_lang: 'ru',
                code_snippet: codeSnippet
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Ошибка при обращении к API');
        }

        const data = await response.json();
        
        // Закрываем попап
        popup.classList.remove("show");
        overlay.classList.remove("show");

        // Показываем результат
        displayAIResponse(data.reply, command);

    } catch (error) {
        console.error('Ошибка:', error);
        alert(`Ошибка при анализе: ${error.message}`);
    } finally {
        // Возвращаем кнопку в исходное состояние
        buttonElement.disabled = false;
        buttonElement.textContent = originalText;
    }
}

// Обработчики для каждой кнопки
explainBtn.addEventListener("click", () => sendToAI('/explain', explainBtn));
fixBtn.addEventListener("click", () => sendToAI('/fix', fixBtn));
improveBtn.addEventListener("click", () => sendToAI('/improve', improveBtn));

// Функция для отображения ответа ИИ
function displayAIResponse(aiReply, command) {
    // Определяем заголовок в зависимости от команды
    let title = '🤖 Анализ ИИ-помощника';
    if (command === '/explain') {
        title = '📖 Объяснение уязвимостей';
    } else if (command === '/fix') {
        title = '🔧 Предложения по исправлению';
    } else if (command === '/improve') {
        title = '⚡ Улучшения кода';
    }

    // Создаем новый блок для отображения ответа ИИ
    const aiResultDiv = document.createElement('div');
    aiResultDiv.className = 'result-section ai-result-section';
    aiResultDiv.style.marginTop = '2rem';
    aiResultDiv.innerHTML = `
        <h2>${title}</h2>
        <div style="background: var(--bg-secondary); padding: 1.5rem; border-radius: 8px; border: 1px solid var(--border-color); white-space: pre-wrap; line-height: 1.8; color: var(--text-primary);">
            ${escapeHtml(aiReply)}
        </div>
    `;

    // Удаляем предыдущий результат ИИ, если есть
    const oldResult = document.querySelector('.ai-result-section');
    if (oldResult) {
        oldResult.remove();
    }

    // Вставляем перед кнопкой "Новое сканирование"
    const backButton = document.querySelector('.back-button');
    if (backButton) {
        backButton.parentNode.insertBefore(aiResultDiv, backButton);
    } else {
        document.querySelector('.results-container').appendChild(aiResultDiv);
    }

    // Плавная прокрутка к результату
    aiResultDiv.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// Функция для экранирования HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
