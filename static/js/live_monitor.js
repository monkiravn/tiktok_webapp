/**
 * TikTok Live Monitor - Frontend JavaScript
 */

class LiveMonitor {
    constructor() {
        this.refreshInterval = null;
        this.autoRefreshEnabled = true;
        this.initializeEventListeners();
        this.startAutoRefresh();
    }

    initializeEventListeners() {
        // Add user button
        document.getElementById('addUserBtn').addEventListener('click', () => {
            this.addMonitor();
        });

        // Enter key in username input
        document.getElementById('usernameInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.addMonitor();
            }
        });

        // Settings button
        document.getElementById('settingsBtn').addEventListener('click', () => {
            this.openSettings();
        });

        // Save settings button
        document.getElementById('saveSettingsBtn').addEventListener('click', () => {
            this.saveSettings();
        });

        // Update CLI button
        document.getElementById('updateCliBtn').addEventListener('click', () => {
            this.updateCli();
        });

        // Refresh button
        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.refreshMonitors();
        });

        // Remove monitor buttons (delegated)
        document.getElementById('monitorsTableBody').addEventListener('click', (e) => {
            if (e.target.classList.contains('remove-monitor') || e.target.closest('.remove-monitor')) {
                const button = e.target.closest('.remove-monitor');
                const username = button.getAttribute('data-username');
                this.removeMonitor(username);
            }
        });

        // Telegram checkbox toggle
        document.getElementById('useTelegram').addEventListener('change', (e) => {
            const configDiv = document.getElementById('telegramConfig');
            if (e.target.checked) {
                configDiv.style.display = 'block';
            } else {
                configDiv.style.display = 'none';
            }
        });

        // Modal close buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('btn-close') || e.target.getAttribute('data-bs-dismiss') === 'modal') {
                const modal = document.getElementById('settingsModal');
                modal.style.display = 'none';
                modal.classList.remove('show');
            }
        });
    }

    async addMonitor() {
        const usernameInput = document.getElementById('usernameInput');
        const username = usernameInput.value.trim();

        if (!username) {
            this.showAlert('Please enter a TikTok username', 'warning');
            return;
        }

        // Extract username from URL if provided
        const cleanUsername = this.extractUsername(username);
        
        try {
            const response = await fetch('/api/v1/live/monitors', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username: cleanUsername })
            });

            const data = await response.json();

            if (data.success) {
                this.showAlert(data.message, 'success');
                usernameInput.value = '';
                this.refreshMonitors();
            } else {
                this.showAlert(data.error, 'danger');
            }
        } catch (error) {
            this.showAlert('Error adding monitor: ' + error.message, 'danger');
        }
    }

    async removeMonitor(username) {
        if (!confirm(`Are you sure you want to remove monitor for @${username}?`)) {
            return;
        }

        try {
            const response = await fetch(`/api/v1/live/monitors/${username}`, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (data.success) {
                this.showAlert(data.message, 'success');
                this.refreshMonitors();
            } else {
                this.showAlert(data.error, 'danger');
            }
        } catch (error) {
            this.showAlert('Error removing monitor: ' + error.message, 'danger');
        }
    }

    async refreshMonitors() {
        try {
            const response = await fetch('/api/v1/live/monitors');
            const data = await response.json();

            if (data.success) {
                this.updateMonitorsTable(data.monitors);
                this.updateMonitorCount(data.monitors.length);
            } else {
                this.showAlert('Error loading monitors: ' + data.error, 'danger');
            }
        } catch (error) {
            this.showAlert('Error refreshing monitors: ' + error.message, 'danger');
        }
    }

    updateMonitorsTable(monitors) {
        const tbody = document.getElementById('monitorsTableBody');
        
        if (monitors.length === 0) {
            tbody.innerHTML = `
                <tr id="noMonitorsRow">
                    <td colspan="5" class="text-center py-4 text-muted">
                        <i class="fas fa-inbox fa-2x mb-3 opacity-50"></i>
                        <h6>No monitors active</h6>
                        <p class="small mb-0">Add a TikTok username to start monitoring</p>
                    </td>
                </tr>
            `;
            return;
        }

        const rows = monitors.map(monitor => {
            const statusBadge = this.getStatusBadge(monitor.status);
            const startTime = monitor.start_time ? monitor.start_time.substring(0, 19).replace('T', ' ') : '-';
            const lastCheck = monitor.last_check ? monitor.last_check.substring(0, 19).replace('T', ' ') : '-';

            return `
                <tr data-username="${monitor.username}">
                    <td>
                        <div class="d-flex align-items-center">
                            <i class="fab fa-tiktok me-2 text-dark"></i>
                            <span class="fw-semibold">${monitor.username}</span>
                        </div>
                    </td>
                    <td>${statusBadge}</td>
                    <td><small>${startTime}</small></td>
                    <td><small>${lastCheck}</small></td>
                    <td>
                        <button type="button" class="btn btn-danger btn-sm remove-monitor" 
                                data-username="${monitor.username}">
                            <i class="fas fa-trash me-1"></i>
                            Remove
                        </button>
                    </td>
                </tr>
            `;
        }).join('');

        tbody.innerHTML = rows;
    }

    getStatusBadge(status) {
        switch (status) {
            case 'recording':
                return '<span class="badge bg-success"><i class="fas fa-record-vinyl me-1"></i>Recording</span>';
            case 'monitoring':
                return '<span class="badge bg-info"><i class="fas fa-eye me-1"></i>Monitoring</span>';
            default:
                return '<span class="badge bg-secondary"><i class="fas fa-stop me-1"></i>Stopped</span>';
        }
    }

    updateMonitorCount(count) {
        document.getElementById('monitorCount').textContent = count;
    }

    async openSettings() {
        try {
            const response = await fetch('/api/v1/live/settings');
            const data = await response.json();

            if (data.success) {
                this.populateSettingsForm(data.settings);
                // Try to use Bootstrap modal if available, otherwise show as overlay
                const modal = document.getElementById('settingsModal');
                if (typeof bootstrap !== 'undefined') {
                    new bootstrap.Modal(modal).show();
                } else {
                    // Fallback for when Bootstrap is not available
                    modal.style.display = 'block';
                    modal.classList.add('show');
                    modal.style.backgroundColor = 'rgba(0,0,0,0.5)';
                }
            } else {
                this.showAlert('Error loading settings: ' + data.error, 'danger');
            }
        } catch (error) {
            this.showAlert('Error opening settings: ' + error.message, 'danger');
        }
    }

    populateSettingsForm(settings) {
        document.getElementById('checkInterval').value = settings.check_interval || 5;
        document.getElementById('duration').value = settings.duration || '';
        document.getElementById('outputDir').value = settings.output_dir || '';
        document.getElementById('useTelegram').checked = settings.use_telegram || false;
        
        // Telegram config
        if (settings.telegram_config) {
            document.getElementById('telegramApiId').value = settings.telegram_config.api_id || '';
            document.getElementById('telegramApiHash').value = settings.telegram_config.api_hash || '';
            document.getElementById('telegramChannel').value = settings.telegram_config.channel || '';
        }

        // Show/hide telegram config
        const telegramConfig = document.getElementById('telegramConfig');
        telegramConfig.style.display = settings.use_telegram ? 'block' : 'none';
    }

    async saveSettings() {
        const settings = {
            check_interval: parseInt(document.getElementById('checkInterval').value) || 5,
            duration: parseInt(document.getElementById('duration').value) || null,
            output_dir: document.getElementById('outputDir').value.trim(),
            use_telegram: document.getElementById('useTelegram').checked,
            telegram_config: {
                api_id: document.getElementById('telegramApiId').value.trim(),
                api_hash: document.getElementById('telegramApiHash').value.trim(),
                channel: document.getElementById('telegramChannel').value.trim()
            }
        };

        try {
            const response = await fetch('/api/v1/live/settings', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(settings)
            });

            const data = await response.json();

            if (data.success) {
                this.showAlert(data.message, 'success');
                // Close modal with fallback
                const modal = document.getElementById('settingsModal');
                if (typeof bootstrap !== 'undefined') {
                    bootstrap.Modal.getInstance(modal)?.hide();
                } else {
                    modal.style.display = 'none';
                    modal.classList.remove('show');
                }
            } else {
                this.showAlert(data.error, 'danger');
            }
        } catch (error) {
            this.showAlert('Error saving settings: ' + error.message, 'danger');
        }
    }

    async updateCli() {
        const updateBtn = document.getElementById('updateCliBtn');
        const originalText = updateBtn.innerHTML;
        
        updateBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Updating...';
        updateBtn.disabled = true;

        try {
            const response = await fetch('/api/v1/live/cli-update', {
                method: 'POST'
            });

            const data = await response.json();

            if (data.success) {
                this.showAlert(data.message, 'success');
            } else {
                this.showAlert(data.error, 'danger');
            }
        } catch (error) {
            this.showAlert('Error updating CLI: ' + error.message, 'danger');
        } finally {
            updateBtn.innerHTML = originalText;
            updateBtn.disabled = false;
        }
    }

    extractUsername(input) {
        // Remove @ if present
        input = input.replace(/^@/, '');
        
        // Extract username from TikTok URL
        const urlPattern = /(?:https?:\/\/)?(?:www\.)?tiktok\.com\/@([^\/\?]+)/;
        const match = input.match(urlPattern);
        
        if (match) {
            return match[1];
        }
        
        return input;
    }

    startAutoRefresh() {
        // Refresh every 30 seconds
        this.refreshInterval = setInterval(() => {
            if (this.autoRefreshEnabled) {
                this.refreshMonitors();
            }
        }, 30000);
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    showAlert(message, type = 'info') {
        // Remove existing alerts
        const existingAlerts = document.querySelectorAll('.live-monitor-alert');
        existingAlerts.forEach(alert => alert.remove());

        // Create new alert
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show live-monitor-alert`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        // Insert at the top of the main content
        const contentWrapper = document.querySelector('.content-wrapper');
        contentWrapper.insertBefore(alertDiv, contentWrapper.firstChild);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new LiveMonitor();
});