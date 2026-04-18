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
        if (e.target !== fileRemoveBtn && e.target !== fileInput) {
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
        handleFiles(files);
    }

    fileInput.addEventListener('change', function () {
        handleFiles(this.files);
    });

    function handleFiles(files) {
        if (files.length > 0) {
            if (fileInput.files !== files) {
                fileInput.files = files;
            }
            
            if (files.length > 5) {
                alert("Максимум 5 файлов.");
                fileInput.value = "";
                return;
            }

            updateFileInfo(files);
        }
    }

    function updateFileInfo(files) {
        if (files.length === 1) {
            fileName.textContent = files[0].name;
        } else {
            fileName.textContent = `Выбрано файлов: ${files.length}`;
        }
        
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