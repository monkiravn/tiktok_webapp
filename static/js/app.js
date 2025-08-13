// App configuration constants
const SIDEBAR_BREAKPOINT = 992; // Large screen breakpoint (lg) in pixels
const UPLOAD_PROGRESS_TIMEOUT_MS = 30000; // 30 seconds timeout

// App functionality
document.addEventListener('DOMContentLoaded', function() {
    initializeSidebar();
    initializeUploadPage();
    initializeNavigation();
});

// Sidebar functionality
function initializeSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mobileSidebarToggle = document.getElementById('mobileSidebarToggle');
    const sidebarOverlay = document.getElementById('sidebarOverlay');

    // Check if sidebar elements exist
    if (!sidebar) {
        return; // Exit if not on authenticated pages
    }

    // Initialize hover-based expansion for accessibility (keyboard navigation)
    if (window.innerWidth >= SIDEBAR_BREAKPOINT) {
        addKeyboardAccessibility(sidebar);
    }

    // Mobile sidebar toggle
    if (mobileSidebarToggle) {
        mobileSidebarToggle.addEventListener('click', function() {
            toggleMobileSidebar();
        });
    }

    // Overlay click to close (mobile only)
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', function() {
            closeMobileSidebar();
        });
    }

    // Close sidebar on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            if (sidebar.classList.contains('mobile-open')) {
                closeMobileSidebar();
            }
        }
    });

    // Handle window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth >= SIDEBAR_BREAKPOINT) {
            // Desktop: remove mobile classes and re-add keyboard accessibility
            sidebar.classList.remove('mobile-open');
            if (sidebarOverlay) {
                sidebarOverlay.classList.remove('active');
            }
            addKeyboardAccessibility(sidebar);
        } else {
            // Mobile: remove hover effect classes
            sidebar.classList.remove('keyboard-focus');
        }
    });

    function toggleMobileSidebar() {
        sidebar.classList.toggle('mobile-open');
        if (sidebarOverlay) {
            sidebarOverlay.classList.toggle('active');
        }
    }

    function closeMobileSidebar() {
        sidebar.classList.remove('mobile-open');
        if (sidebarOverlay) {
            sidebarOverlay.classList.remove('active');
        }
    }

    // Add keyboard accessibility for sidebar expansion
    function addKeyboardAccessibility(sidebar) {
        const sidebarLinks = sidebar.querySelectorAll('.nav-link');
        
        // Add focus/blur handlers for keyboard navigation
        sidebarLinks.forEach(link => {
            link.addEventListener('focus', function() {
                sidebar.classList.add('keyboard-focus');
            });
            
            link.addEventListener('blur', function() {
                // Small delay to check if focus moved to another sidebar link
                setTimeout(() => {
                    if (!sidebar.contains(document.activeElement)) {
                        sidebar.classList.remove('keyboard-focus');
                    }
                }, 10);
            });
        });

        // Handle mouseenter/mouseleave for consistency
        sidebar.addEventListener('mouseenter', function() {
            if (!sidebar.classList.contains('keyboard-focus')) {
                sidebar.classList.add('hover-focus');
            }
        });

        sidebar.addEventListener('mouseleave', function() {
            sidebar.classList.remove('hover-focus');
        });
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
    // Ensure dropdown z-index is properly set
    const userDropdown = document.getElementById('userDropdown');
    if (userDropdown) {
        userDropdown.addEventListener('click', function(e) {
            e.preventDefault();
            const dropdownMenu = this.nextElementSibling;
            if (dropdownMenu) {
                dropdownMenu.style.zIndex = '9999';
                dropdownMenu.style.position = 'absolute';
            }
        });

        // Also set it when Bootstrap shows the dropdown
        userDropdown.addEventListener('shown.bs.dropdown', function() {
            const dropdownMenu = this.nextElementSibling;
            if (dropdownMenu) {
                dropdownMenu.style.zIndex = '9999';
                dropdownMenu.style.position = 'absolute';
            }
        });
    }
}
