document.addEventListener('DOMContentLoaded', function() {
    const fileUploadArea = document.getElementById('fileUploadArea');
    const fileInput = document.getElementById('file');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const uploadForm = document.getElementById('uploadForm');
    const submitBtn = document.getElementById('submitBtn');
    const submitText = document.getElementById('submitText');
    const loadingText = document.getElementById('loadingText');
    const progressSection = document.getElementById('progressSection');
    const progressBar = document.getElementById('progressBar');
    const progressText = document.getElementById('progressText');
    
    // Camera elements
    const fileUploadRadio = document.getElementById('fileUpload');
    const cameraRadio = document.getElementById('cameraCapture');
    const fileUploadSection = document.getElementById('fileUploadSection');
    const cameraSection = document.getElementById('cameraSection');
    const startCameraBtn = document.getElementById('startCamera');
    const capturePhotoBtn = document.getElementById('capturePhoto');
    const retakePhotoBtn = document.getElementById('retakePhoto');
    const cameraVideo = document.getElementById('cameraVideo');
    const captureCanvas = document.getElementById('captureCanvas');
    const previewImage = document.getElementById('previewImage');
    const capturedImagePreview = document.getElementById('capturedImagePreview');
    const capturedImageData = document.getElementById('capturedImageData');
    
    let currentStream = null;

    // Drag and drop functionality
    fileUploadArea.addEventListener('dragover', function(e) {
        e.preventDefault();
        fileUploadArea.classList.add('dragover');
    });

    fileUploadArea.addEventListener('dragleave', function(e) {
        e.preventDefault();
        fileUploadArea.classList.remove('dragover');
    });

    fileUploadArea.addEventListener('drop', function(e) {
        e.preventDefault();
        fileUploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            updateFileInfo(files[0]);
        }
    });

    // File input change
    fileInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            updateFileInfo(e.target.files[0]);
        }
    });

    // Upload method toggle
    fileUploadRadio.addEventListener('change', function() {
        if (this.checked) {
            fileUploadSection.style.display = 'block';
            cameraSection.style.display = 'none';
            fileInput.required = true;
            capturedImageData.value = '';
            stopCamera();
        }
    });

    cameraRadio.addEventListener('change', function() {
        if (this.checked) {
            fileUploadSection.style.display = 'none';
            cameraSection.style.display = 'block';
            fileInput.required = false;
            fileInput.value = '';
            fileInfo.style.display = 'none';
        }
    });

    // Camera functionality
    startCameraBtn.addEventListener('click', async function() {
        try {
            currentStream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: 'environment' } // Use back camera on mobile
            });
            
            cameraVideo.srcObject = currentStream;
            cameraVideo.style.display = 'block';
            startCameraBtn.style.display = 'none';
            capturePhotoBtn.style.display = 'inline-block';
            
        } catch (err) {
            console.error('Error accessing camera:', err);
            alert('Unable to access camera. Please ensure camera permissions are granted.');
        }
    });

    capturePhotoBtn.addEventListener('click', function() {
        const context = captureCanvas.getContext('2d');
        captureCanvas.width = cameraVideo.videoWidth;
        captureCanvas.height = cameraVideo.videoHeight;
        
        context.drawImage(cameraVideo, 0, 0);
        
        // Convert canvas to base64 image
        const imageData = captureCanvas.toDataURL('image/jpeg', 0.8);
        capturedImageData.value = imageData;
        
        // Show preview
        previewImage.src = imageData;
        capturedImagePreview.style.display = 'block';
        
        // Hide camera and show retake button
        cameraVideo.style.display = 'none';
        capturePhotoBtn.style.display = 'none';
        retakePhotoBtn.style.display = 'inline-block';
        
        stopCamera();
    });

    retakePhotoBtn.addEventListener('click', function() {
        capturedImagePreview.style.display = 'none';
        capturedImageData.value = '';
        retakePhotoBtn.style.display = 'none';
        startCameraBtn.style.display = 'inline-block';
    });

    function stopCamera() {
        if (currentStream) {
            currentStream.getTracks().forEach(track => track.stop());
            currentStream = null;
        }
    }

    // Update file info display
    function updateFileInfo(file) {
        fileName.textContent = file.name;
        fileSize.textContent = ` (${formatFileSize(file.size)})`;
        fileInfo.style.display = 'block';
    }

    // Format file size
    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // Form submission with progress animation
    uploadForm.addEventListener('submit', function(e) {
        const isFileUpload = fileUploadRadio.checked;
        const isCameraCapture = cameraRadio.checked;
        
        if (isFileUpload && !fileInput.files.length) {
            e.preventDefault();
            alert('Please select a file first.');
            return;
        }
        
        if (isCameraCapture && !capturedImageData.value) {
            e.preventDefault();
            alert('Please capture a photo first.');
            return;
        }

        // Show loading state
        submitBtn.disabled = true;
        submitText.style.display = 'none';
        loadingText.style.display = 'inline';
        
        // Show progress section
        progressSection.style.display = 'block';
        
        // Animate progress bar
        animateProgress();
    });

    // Animate progress bar
    function animateProgress() {
        const stages = [
            { width: 20, text: 'Uploading file...' },
            { width: 40, text: 'Extracting text from document...' },
            { width: 70, text: 'Analyzing document content...' },
            { width: 90, text: 'Generating AI summary...' },
            { width: 100, text: 'Finalizing results...' }
        ];

        let currentStage = 0;
        
        function updateProgress() {
            if (currentStage < stages.length) {
                const stage = stages[currentStage];
                progressBar.style.width = stage.width + '%';
                progressText.textContent = stage.text;
                currentStage++;
                
                // Random delay between stages
                setTimeout(updateProgress, 800 + Math.random() * 400);
            }
        }
        
        updateProgress();
    }

    // Explain clause functionality
    const explainButtons = document.querySelectorAll('.explain-btn');
    const explainModal = document.getElementById('explainModal');
    const explanationContent = document.getElementById('explanationContent');

    explainButtons.forEach(button => {
        button.addEventListener('click', function() {
            const clauseText = this.getAttribute('data-clause');
            
            // Reset modal content
            explanationContent.innerHTML = `
                <div class="text-center">
                    <i class="fas fa-spinner fa-spin fa-2x"></i>
                    <p class="mt-2">Getting explanation...</p>
                </div>
            `;

            // Make AJAX request to explain endpoint
            fetch('/explain', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: 'clause_text=' + encodeURIComponent(clauseText)
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    explanationContent.innerHTML = `
                        <div class="alert alert-danger">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            ${data.error}
                        </div>
                    `;
                } else {
                    explanationContent.innerHTML = `
                        <div class="alert alert-info">
                            <h6><i class="fas fa-info-circle me-2"></i>Plain English Explanation:</h6>
                            <p class="mb-0">${data.explanation}</p>
                        </div>
                    `;
                }
            })
            .catch(error => {
                explanationContent.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Error getting explanation. Please try again.
                    </div>
                `;
            });
        });
    });

    // File type validation
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
            const fileExtension = file.name.split('.').pop().toLowerCase();
            const allowedExtensions = ['pdf', 'docx', 'txt'];
            
            if (!allowedExtensions.includes(fileExtension)) {
                alert('Please upload only PDF, DOCX, or TXT files.');
                e.target.value = '';
                fileInfo.style.display = 'none';
                return;
            }
            
            // Check file size (16MB limit)
            if (file.size > 16 * 1024 * 1024) {
                alert('File size must be less than 16MB.');
                e.target.value = '';
                fileInfo.style.display = 'none';
                return;
            }
            
            updateFileInfo(file);
        }
    });
});
