// Voice Capsule Web App JavaScript
// Handles file upload, progress tracking, and result display

const API_BASE = window.location.origin;

class VoiceCapsuleApp {
    constructor() {
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.uploadBtn = document.getElementById('uploadBtn');
        this.progressContainer = document.getElementById('progressContainer');
        this.progressFill = document.getElementById('progressFill');
        this.statusMessage = document.getElementById('statusMessage');
        this.resultContainer = document.getElementById('resultContainer');
        this.resultText = document.getElementById('resultText');
        this.wordCount = document.getElementById('wordCount');
        this.notePath = document.getElementById('notePath');
        this.errorMessage = document.getElementById('errorMessage');
        
        this.selectedFile = null;
        this.currentJobId = null;
        
        this.initEventListeners();
    }
    
    initEventListeners() {
        // Upload area click
        this.uploadArea.addEventListener('click', () => this.fileInput.click());
        
        // File selection
        this.fileInput.addEventListener('change', (e) => this.handleFileSelect(e));
        
        // Drag and drop
        this.uploadArea.addEventListener('dragover', (e) => this.handleDragOver(e));
        this.uploadArea.addEventListener('dragleave', () => this.handleDragLeave());
        this.uploadArea.addEventListener('drop', (e) => this.handleDrop(e));
        
        // Upload button
        this.uploadBtn.addEventListener('click', () => this.uploadFile());
    }
    
    handleFileSelect(e) {
        this.selectedFile = e.target.files[0];
        if (this.selectedFile) {
            this.updateUploadAreaText(this.selectedFile.name);
            this.uploadBtn.disabled = false;
        }
    }
    
    handleDragOver(e) {
        e.preventDefault();
        this.uploadArea.classList.add('dragover');
    }
    
    handleDragLeave() {
        this.uploadArea.classList.remove('dragover');
    }
    
    handleDrop(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('dragover');
        
        this.selectedFile = e.dataTransfer.files[0];
        if (this.selectedFile) {
            this.updateUploadAreaText(this.selectedFile.name);
            this.uploadBtn.disabled = false;
        }
    }
    
    updateUploadAreaText(filename) {
        this.uploadArea.querySelector('.upload-text').textContent = filename;
    }
    
    async uploadFile() {
        if (!this.selectedFile) return;
        
        this.uploadBtn.disabled = true;
        this.showProgress();
        this.hideResult();
        this.hideError();
        
        try {
            const formData = new FormData();
            formData.append('file', this.selectedFile);
            
            const response = await fetch(`${API_BASE}/api/upload`, {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Upload failed');
            }
            
            const { job_id } = await response.json();
            this.currentJobId = job_id;
            
            await this.pollStatus(job_id);
            
        } catch (error) {
            this.showError(error.message);
            this.uploadBtn.disabled = false;
        }
    }
    
    async pollStatus(jobId) {
        const pollInterval = setInterval(async () => {
            try {
                const response = await fetch(`${API_BASE}/api/status/${jobId}`);
                const data = await response.json();
                
                this.updateProgress(data.progress, data.message);
                
                if (data.status === 'completed') {
                    clearInterval(pollInterval);
                    this.showResult(data.result);
                } else if (data.status === 'failed') {
                    clearInterval(pollInterval);
                    this.showError(data.message);
                }
            } catch (error) {
                clearInterval(pollInterval);
                this.showError('Failed to check status');
            }
        }, 1000);
    }
    
    updateProgress(progress, message) {
        this.progressFill.style.width = progress + '%';
        this.progressFill.textContent = progress + '%';
        this.statusMessage.textContent = message;
    }
    
    showProgress() {
        this.progressContainer.style.display = 'block';
        this.updateProgress(0, 'Starting...');
    }
    
    hideProgress() {
        this.progressContainer.style.display = 'none';
    }
    
    showResult(result) {
        this.hideProgress();
        this.resultContainer.style.display = 'block';
        
        this.resultText.textContent = result.transcription;
        this.wordCount.textContent = result.word_count;
        this.notePath.textContent = '✓';
        
        this.uploadBtn.disabled = false;
        this.uploadBtn.textContent = 'Process Another File';
    }
    
    hideResult() {
        this.resultContainer.style.display = 'none';
    }
    
    showError(message) {
        this.errorMessage.textContent = '❌ Error: ' + message;
        this.errorMessage.style.display = 'block';
        this.hideProgress();
        this.uploadBtn.disabled = false;
    }
    
    hideError() {
        this.errorMessage.style.display = 'none';
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new VoiceCapsuleApp();
});
