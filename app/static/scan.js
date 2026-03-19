document.addEventListener('DOMContentLoaded', function () {
    const dropZone = document.getElementById('fileDropZone');
    const fileInput = document.getElementById('fileInput');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const fileRemoveBtn = document.getElementById('fileRemoveBtn');
    const dropZoneContent = document.getElementById('dropZoneContent');
    const scanForm = document.getElementById('scanForm');

    if (!dropZone || !fileInput) return;

    dropZone.addEventListener('click', function (e) {
        if (e.target !== fileRemoveBtn) {
            fileInput.click();
        }
    });

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    function highlight() {
        dropZone.classList.add('dragover');
    }

    function unhighlight() {
        dropZone.classList.remove('dragover');
    }

    dropZone.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;

        if (files.length > 0) {
            fileInput.files = files;
            updateFileInfo(files[0]);
        }
    }

    fileInput.addEventListener('change', function () {
        if (this.files.length > 0) {
            updateFileInfo(this.files[0]);
        }
    });

    function updateFileInfo(file) {
        fileName.textContent = file.name;
        dropZoneContent.style.display = 'none';
        fileInfo.style.display = 'flex';
    }

    if (fileRemoveBtn) {
        fileRemoveBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            fileInput.value = '';
            dropZoneContent.style.display = 'block';
            fileInfo.style.display = 'none';
        });
    }

    // Индикатор загрузки при отправке формы
    if (scanForm) {
        scanForm.addEventListener('submit', function () {
            const submitBtn = scanForm.querySelector('input[type="submit"], button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.dataset.originalText = submitBtn.value || submitBtn.textContent;
                if (submitBtn.tagName === 'INPUT') {
                    submitBtn.value = '⏳ Сканирование...';
                } else {
                    submitBtn.textContent = '⏳ Сканирование...';
                }
                submitBtn.style.opacity = '0.7';
                submitBtn.style.cursor = 'wait';
            }
        });
    }
});