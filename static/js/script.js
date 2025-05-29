// Custom JavaScript for File Share application

document.addEventListener('DOMContentLoaded', function() {
    // Initialize the file preview modal functionality
    initFilePreviewModal();
    
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // File upload preview
    const fileInput = document.getElementById('file');
    if (fileInput) {
        fileInput.addEventListener('change', function() {
            const fileName = this.files[0]?.name || 'No file selected';
            const fileLabel = document.querySelector('.custom-file-label');
            if (fileLabel) {
                fileLabel.textContent = fileName;
            }
        });
    }

    // Auto dismiss alerts after 5 seconds
    window.setTimeout(function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Confirm delete actions
    const deleteButtons = document.querySelectorAll('.delete-confirm');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this item? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });

    // Toggle star status with ajax (placeholder functionality)
    const starButtons = document.querySelectorAll('.star-btn');
    starButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const fileId = this.dataset.fileId;
            const icon = this.querySelector('i');
            
            // Toggle star appearance (in a real app, this would be done after the AJAX call succeeds)
            icon.classList.toggle('text-warning');
            icon.classList.toggle('text-muted');
            
            // Here you would typically make an AJAX call to the server to update the star status
            console.log('Toggled star status for file:', fileId);
        });
    });

    // File drop zone functionality
    const dropZone = document.getElementById('dropZone');
    if (dropZone) {
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
            dropZone.classList.add('highlight');
        }

        function unhighlight() {
            dropZone.classList.remove('highlight');
        }

        dropZone.addEventListener('drop', handleDrop, false);

        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            
            if (files.length > 0) {
                // In a real app, you would handle the file upload here
                console.log('Files dropped:', files);
                
                // If there's a file input, you could set its files
                const fileInput = document.getElementById('file');
                if (fileInput) {
                    fileInput.files = files;
                    // Trigger change event to update any UI elements
                    const event = new Event('change');
                    fileInput.dispatchEvent(event);
                }
            }
        }
    }

    // Search functionality enhancements
    const searchForm = document.querySelector('form[action*="search"]');
    if (searchForm) {
        const searchInput = searchForm.querySelector('input[name="query"]');
        if (searchInput) {
            // Clear search when x is clicked
            searchInput.addEventListener('search', function() {
                if (this.value === '') {
                    window.location.href = '/dashboard';
                }
            });
            
            // Add autocomplete placeholder (in a real app, this would fetch from the server)
            searchInput.addEventListener('keyup', function() {
                console.log('Search query:', this.value);
                // Here you would typically make an AJAX call to get search suggestions
            });
        }
    }
    
    // Set up file preview buttons
    document.querySelectorAll('.file-item').forEach(function(fileItem) {
        const fileId = fileItem.dataset.fileId;
        if (fileId) {
            // Make the entire file item clickable for preview
            fileItem.addEventListener('click', function(e) {
                // Don't trigger for clicks on buttons or links within the file item
                if (e.target.closest('a, button, .dropdown')) return;
                e.preventDefault();
                previewFile(fileId);
            });
        }
    });
    
    // Handle dedicated preview buttons click events
    document.querySelectorAll('.preview-file-btn').forEach(function(button) {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation(); // Stop event bubbling
            const fileId = this.getAttribute('data-file-id');
            if (fileId) {
                previewFile(fileId);
            }
        });
    });
});

// File Preview Modal Functions
function initFilePreviewModal() {
    // Create references to modal elements
    window.previewModal = {
        modal: document.getElementById('previewModal'),
        title: document.getElementById('previewModalLabel'),
        body: document.getElementById('previewModalBody'),
        downloadBtn: document.getElementById('previewDownloadBtn'),
        openNewTabBtn: document.getElementById('previewOpenNewTabBtn'),
        bsModal: new bootstrap.Modal(document.getElementById('previewModal'))
    };
}

function previewFile(fileId) {
    if (!window.previewModal) return;
    
    // Show loading spinner
    window.previewModal.body.innerHTML = `
        <div class="text-center py-5">
            <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>
    `;
    
    // Show the modal
    window.previewModal.bsModal.show();
    
    // Setup download and open in new tab buttons
    window.previewModal.downloadBtn.href = `/download/${fileId}`;
    window.previewModal.openNewTabBtn.href = `/preview/${fileId}?direct=1`;
    
    // Fetch file preview content
    fetch(`/preview/${fileId}?modal=1`)
        .then(response => {
            if (!response.ok) {
                throw new Error('Error loading preview');
            }
            return response.json();
        })
        .then(data => {
            // Update modal title
            window.previewModal.title.textContent = data.filename || 'File Preview';
            
            // Handle different file types
            if (data.file_type === 'image') {
                window.previewModal.body.innerHTML = `
                    <div class="preview-container">
                        <img src="/preview/${fileId}?inline=1" alt="${data.filename}">
                    </div>
                `;
            } else if (data.file_type === 'pdf') {
                window.previewModal.body.innerHTML = `
                    <div class="ratio ratio-16x9">
                        <iframe src="/preview/${fileId}?inline=1" allowfullscreen></iframe>
                    </div>
                `;
            } else if (data.file_type === 'video') {
                window.previewModal.body.innerHTML = `
                    <div class="preview-container">
                        <video controls preload="metadata">
                            <source src="/preview/${fileId}?inline=1" type="video/${data.extension}">
                            Your browser does not support the video tag.
                        </video>
                    </div>
                `;
            } else if (data.file_type === 'text') {
                window.previewModal.body.innerHTML = `
                    <div class="preview-container">
                        <pre class="preview-text">${data.content}</pre>
                    </div>
                `;
            } else {
                window.previewModal.body.innerHTML = `
                    <div class="text-center py-3">
                        <i class="fas fa-file fa-4x text-muted mb-2"></i>
                        <h4 class="text-muted">Preview not available</h4>
                        <p class="text-muted">This file type cannot be previewed</p>
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Preview error:', error);
            window.previewModal.body.innerHTML = `
                <div class="alert alert-danger">
                    Error loading preview: ${error.message}
                </div>
            `;
        });
}
