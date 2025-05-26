// Custom JavaScript for File Share application

document.addEventListener('DOMContentLoaded', function() {
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
});
