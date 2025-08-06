// App functionality
document.addEventListener('DOMContentLoaded', function() {
    initializeSidebar();
    initializeUploadPage();
    initializeNavigation();
});

// Sidebar functionality
function initializeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const mobileSidebarToggle = document.getElementById('mobileSidebarToggle');
    const sidebarOverlay = document.getElementById('sidebarOverlay');

    // Check if sidebar elements exist
    if (!sidebar || !sidebarOverlay) {
        return; // Exit if not on authenticated pages
    }

    // Mobile sidebar toggle
    if (mobileSidebarToggle) {
        mobileSidebarToggle.addEventListener('click', function() {
            toggleSidebar();
        });
    }

    // Sidebar close button
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            closeSidebar();
        });
    }

    // Overlay click to close
    sidebarOverlay.addEventListener('click', function() {
        closeSidebar();
    });

    // Close sidebar on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && sidebar.classList.contains('mobile-open')) {
            closeSidebar();
        }
    });

    function toggleSidebar() {
        sidebar.classList.toggle('mobile-open');
        sidebarOverlay.classList.toggle('active');
    }

    function closeSidebar() {
        sidebar.classList.remove('mobile-open');
        sidebarOverlay.classList.remove('active');
    }
}

function initializeUploadPage() {
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('fileInput');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    const submitBtn = document.getElementById('submitBtn');
    const uploadForm = document.getElementById('uploadForm');
    const submitText = document.getElementById('submitText');
    const uploadSpinner = document.getElementById('uploadSpinner');

    // Check if we're on the upload page
    if (!uploadZone || !fileInput) {
        return; // Exit if not on upload page
    }

    // Click to upload
    uploadZone.addEventListener('click', () => {
        fileInput.click();
    });

    // Drag and drop functionality
    uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadZone.classList.add('drag-over');
    });

    uploadZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('drag-over');
    });

    uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadZone.classList.remove('drag-over');

        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            if (isValidVideoFile(file)) {
                fileInput.files = files;
                displayFileInfo(file);
            } else {
                showError('Please select a valid video file (MP4, AVI, MOV, WMV, FLV, WebM)');
            }
        }
    });

    // File input change
    fileInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            if (isValidVideoFile(file)) {
                displayFileInfo(file);
            } else {
                showError('Please select a valid video file (MP4, AVI, MOV, WMV, FLV, WebM)');
                clearFile();
            }
        }
    });

    // Form submission
    uploadForm.addEventListener('submit', (e) => {
        if (!fileInput.files[0]) {
            e.preventDefault();
            showError('Please select a video file first');
            return;
        }

        // Show loading state
        submitBtn.disabled = true;
        submitText.textContent = 'Processing...';
        uploadSpinner.classList.remove('d-none');

        // Add progress simulation
        simulateProgress();
    });

    function isValidVideoFile(file) {
        const validTypes = ['video/mp4', 'video/avi', 'video/quicktime', 'video/x-ms-wmv', 'video/x-flv', 'video/webm'];
        const validExtensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm'];

        return validTypes.includes(file.type) ||
               validExtensions.some(ext => file.name.toLowerCase().endsWith(ext));
    }

    function displayFileInfo(file) {
        fileName.textContent = file.name;
        fileSize.textContent = formatFileSize(file.size);
        fileInfo.classList.remove('d-none');
        submitBtn.disabled = false;

        // Add success animation
        fileInfo.style.animation = 'slideInDown 0.5s ease';
    }

    function formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    function showError(message) {
        // Create temporary error alert
        const errorDiv = document.createElement('div');
        errorDiv.className = 'alert alert-danger alert-dismissible fade show mt-3';
        errorDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        uploadZone.parentNode.insertBefore(errorDiv, uploadZone.nextSibling);

        // Auto dismiss after 5 seconds
        setTimeout(() => {
            if (errorDiv.parentNode) {
                errorDiv.remove();
            }
        }, 5000);
    }

    function simulateProgress() {
        // Create progress bar
        const progressDiv = document.createElement('div');
        progressDiv.className = 'mt-3';
        progressDiv.innerHTML = `
            <div class="progress" style="height: 8px;">
                <div class="progress-bar progress-bar-striped progress-bar-animated"
                     role="progressbar" style="width: 0%"></div>
            </div>
            <small class="text-muted mt-2 d-block text-center">Uploading and processing your video...</small>
        `;

        submitBtn.parentNode.appendChild(progressDiv);

        const progressBar = progressDiv.querySelector('.progress-bar');
        let progress = 0;

        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 90) progress = 90;
            progressBar.style.width = progress + '%';
        }, 500);

        // Clear interval on form submit completion
        uploadForm.addEventListener('beforeunload', () => {
            clearInterval(interval);
        });
    }

    // Global function for clear button
    window.clearFile = function() {
        fileInput.value = '';
        fileInfo.classList.add('d-none');
        submitBtn.disabled = true;
        submitText.textContent = 'Process Video';
        uploadSpinner.classList.add('d-none');
    };
}

// Navigation handling
function initializeNavigation() {
    // Handle video upload navigation
    const videoUploadLinks = document.querySelectorAll('[data-video-upload]');
    videoUploadLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            // For now, show an alert since we don't have a separate route yet
            alert('Video upload functionality will be integrated when you add the Flask route for video_upload.');
            // When you add the route, replace the alert with:
            // window.location.href = '/video-upload'; // or whatever your route is
        });
    });
}
