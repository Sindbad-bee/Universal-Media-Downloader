/**
 * Universal Media Downloader - Frontend Application
 *
 * Handles URL validation, metadata display, download management,
 * and theme toggling via the REST API.
 */

'use strict';

// ── Constants ──────────────────────────────────────────────────────

const API_BASE = '/api/v1';
const POLL_INTERVAL_MS = 2000;
const TOAST_DURATION_MS = 4000;

// ── State ──────────────────────────────────────────────────────────

const state = {
    currentUrl: '',
    metadata: null,
    isDownloading: false,
    pollInterval: null,
};

// ── DOM References ─────────────────────────────────────────────────

const $ = (id) => document.getElementById(id);

const dom = {
    urlInput: $('urlInput'),
    validateBtn: $('validateBtn'),
    urlFeedback: $('urlFeedback'),
    optionsPanel: $('optionsPanel'),
    mediaType: $('mediaType'),
    videoQuality: $('videoQuality'),
    audioFormat: $('audioFormat'),
    videoQualityGroup: $('videoQualityGroup'),
    audioFormatGroup: $('audioFormatGroup'),
    downloadBtn: $('downloadBtn'),
    metadataPreview: $('metadataPreview'),
    thumbnailImg: $('thumbnailImg'),
    mediaTitle: $('mediaTitle'),
    mediaUploader: $('mediaUploader'),
    mediaDuration: $('mediaDuration'),
    mediaExtractor: $('mediaExtractor'),
    downloadsList: $('downloadsList'),
    totalCount: $('totalCount'),
    refreshBtn: $('refreshBtn'),
    themeToggle: $('themeToggle'),
    toast: $('toast'),
};

// ── API Client ─────────────────────────────────────────────────────

const api = {
    async request(method, path, body = null) {
        const options = {
            method,
            headers: { 'Content-Type': 'application/json' },
        };
        if (body) {
            options.body = JSON.stringify(body);
        }

        const response = await fetch(`${API_BASE}${path}`, options);
        const data = await response.json();

        if (!response.ok) {
            const errorMsg =
                data?.error?.message || `Request failed with status ${response.status}`;
            throw new Error(errorMsg);
        }

        return data;
    },

    validateUrl(url) {
        return this.request('POST', '/validate-url', { url });
    },

    fetchMetadata(url) {
        return this.request('GET', `/metadata?url=${encodeURIComponent(url)}`);
    },

    createDownload(body) {
        return this.request('POST', '/downloads', body);
    },

    executeDownload(id) {
        return this.request('POST', `/downloads/${id}/execute`);
    },

    getDownloadStatus(id) {
        return this.request('GET', `/downloads/${id}`);
    },

    listDownloads(limit = 50, offset = 0) {
        return this.request('GET', `/downloads?limit=${limit}&offset=${offset}`);
    },

    cancelDownload(id) {
        return this.request('POST', `/downloads/${id}/cancel`);
    },
};

// ── UI Helpers ─────────────────────────────────────────────────────

function showToast(message, type = 'info') {
    dom.toast.textContent = message;
    dom.toast.className = `toast ${type}`;
    // Force reflow to restart animation
    void dom.toast.offsetWidth;
    dom.toast.classList.add('show');

    setTimeout(() => {
        dom.toast.classList.remove('show');
    }, TOAST_DURATION_MS);
}

function setFeedback(message, type = 'info') {
    dom.urlFeedback.textContent = message;
    dom.urlFeedback.className = `feedback ${type}`;
}

function clearFeedback() {
    dom.urlFeedback.textContent = '';
    dom.urlFeedback.className = 'feedback';
}

function formatDuration(seconds) {
    if (!seconds) return '';
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = seconds % 60;
    if (h > 0) return `${h}h ${m}m ${s}s`;
    if (m > 0) return `${m}m ${s}s`;
    return `${s}s`;
}

function formatDate(dateStr) {
    if (!dateStr) return '';
    // yt-dlp provides YYYYMMDD
    const match = dateStr.match(/(\d{4})(\d{2})(\d{2})/);
    if (match) {
        return `${match[1]}-${match[2]}-${match[3]}`;
    }
    return dateStr;
}

function statusLabel(status) {
    const labels = {
        pending: 'Pending',
        queued: 'Queued',
        in_progress: 'Downloading',
        completed: 'Completed',
        failed: 'Failed',
        cancelled: 'Cancelled',
    };
    return labels[status] || status;
}

function getStatusEmoji(status) {
    const emojis = {
        pending: '⏳',
        queued: '📋',
        in_progress: '⬇️',
        completed: '✅',
        failed: '❌',
        cancelled: '🚫',
    };
    return emojis[status] || '❓';
}

function showOptions(show = true) {
    dom.optionsPanel.style.display = show ? 'block' : 'none';
}

function showMetadata(show = true) {
    dom.metadataPreview.style.display = show ? 'flex' : 'none';
}

// ── Media Type Toggle ──────────────────────────────────────────────

dom.mediaType.addEventListener('change', () => {
    const type = dom.mediaType.value;
    if (type === 'audio') {
        dom.videoQualityGroup.style.display = 'none';
        dom.audioFormatGroup.style.display = 'block';
    } else {
        dom.videoQualityGroup.style.display = 'block';
        dom.audioFormatGroup.style.display = 'none';
    }
});

// ── URL Validation & Metadata ─────────────────────────────────────

let validationTimeout = null;

dom.urlInput.addEventListener('input', () => {
    clearTimeout(validationTimeout);
    clearFeedback();
    showOptions(false);
    showMetadata(false);
    dom.downloadBtn.disabled = true;
    state.metadata = null;

    const url = dom.urlInput.value.trim();
    if (url.length < 5) return;

    validationTimeout = setTimeout(async () => {
        if (!url.startsWith('http://') && !url.startsWith('https://')) {
            setFeedback('Please enter a valid URL starting with http:// or https://', 'error');
            return;
        }

        setFeedback('Validating URL...', 'info');
        dom.validateBtn.disabled = true;

        try {
            const result = await api.validateUrl(url);
            if (result.supported) {
                setFeedback(`✅ Supported — ${result.extractor || 'Unknown source'}`, 'success');
                state.currentUrl = url;
                dom.downloadBtn.disabled = false;
                showOptions(true);

                // Fetch metadata
                try {
                    const meta = await api.fetchMetadata(url);
                    state.metadata = meta;
                    displayMetadata(meta);
                } catch {
                    // Metadata is optional
                }
            } else {
                setFeedback('❌ This URL is not supported by the downloader', 'error');
                dom.downloadBtn.disabled = true;
                showOptions(false);
            }
        } catch (err) {
            setFeedback(`❌ ${err.message}`, 'error');
            dom.downloadBtn.disabled = true;
            showOptions(false);
        } finally {
            dom.validateBtn.disabled = false;
        }
    }, 600);
});

dom.validateBtn.addEventListener('click', () => {
    // Trigger the input event manually
    dom.urlInput.dispatchEvent(new Event('input'));
});

function displayMetadata(meta) {
    if (!meta) return;

    dom.mediaTitle.textContent = meta.title || 'Unknown Title';

    if (meta.thumbnail) {
        dom.thumbnailImg.src = meta.thumbnail;
        dom.thumbnailImg.alt = `${meta.title || 'Video'} thumbnail`;
    }

    const parts = [];
    if (meta.uploader) {
        parts.push(`📺 ${meta.uploader}`);
    }
    if (meta.duration) {
        parts.push(`⏱️ ${formatDuration(meta.duration)}`);
    }
    if (meta.extractor) {
        parts.push(`🔗 ${meta.extractor}`);
    }

    dom.mediaUploader.textContent = parts[0] || '';
    dom.mediaDuration.textContent = parts[1] || '';
    dom.mediaExtractor.textContent = parts[2] || '';

    showMetadata(true);
}

// ── Download Handling ──────────────────────────────────────────────

dom.downloadBtn.addEventListener('click', async () => {
    if (state.isDownloading) return;

    const url = dom.urlInput.value.trim();
    if (!url) {
        showToast('Please enter a valid URL', 'error');
        return;
    }

    state.isDownloading = true;
    dom.downloadBtn.disabled = true;
    dom.downloadBtn.textContent = '⏳ Creating download...';

    try {
        // 1. Create the download request
        const created = await api.createDownload({
            url: url,
            media_type: dom.mediaType.value,
            video_quality: dom.videoQuality.value,
            audio_format: dom.audioFormat.value,
        });

        showToast('Download request created! Starting download...', 'success');

        // 2. Execute the download asynchronously
        api.executeDownload(created.id).catch((err) => {
            console.error('Download execution error:', err);
        });

        // 3. Refresh the download list
        await loadDownloads();

        // 4. Start polling for this download
        startPolling(created.id);

    } catch (err) {
        showToast(`Failed to create download: ${err.message}`, 'error');
    } finally {
        state.isDownloading = false;
        dom.downloadBtn.textContent = '⬇️ Download';
        dom.downloadBtn.disabled = false;
    }
});

// ── Polling ────────────────────────────────────────────────────────

function startPolling(requestId) {
    if (state.pollInterval) {
        clearInterval(state.pollInterval);
    }

    state.pollInterval = setInterval(async () => {
        try {
            const status = await api.getDownloadStatus(requestId);
            updateDownloadItem(status);

            if (['completed', 'failed', 'cancelled'].includes(status.status)) {
                clearInterval(state.pollInterval);
                state.pollInterval = null;

                if (status.status === 'completed') {
                    showToast('✅ Download completed!', 'success');
                } else if (status.status === 'failed') {
                    showToast(`❌ Download failed: ${status.error_message || 'Unknown error'}`, 'error');
                }
            }
        } catch {
            // Ignore polling errors
        }
    }, POLL_INTERVAL_MS);
}

// ── Downloads List ─────────────────────────────────────────────────

async function loadDownloads() {
    try {
        const result = await api.listDownloads(50, 0);
        renderDownloads(result.items || []);
        dom.totalCount.textContent = `${result.pagination?.total || 0} total`;
    } catch (err) {
        console.error('Failed to load downloads:', err);
    }
}

function renderDownloads(items) {
    if (!items || items.length === 0) {
        dom.downloadsList.innerHTML = `
            <div class="empty-state">
                <span class="empty-icon">📂</span>
                <p>No downloads yet. Paste a URL above to get started!</p>
            </div>
        `;
        return;
    }

    dom.downloadsList.innerHTML = items.map((item) => createDownloadItem(item)).join('');
}

function createDownloadItem(item) {
    const emoji = getStatusEmoji(item.status);
    const label = statusLabel(item.status);
    const isCompleted = item.status === 'completed';
    const isInProgress = item.status === 'in_progress';

    return `
        <div class="download-item" data-id="${item.id}">
            <div class="download-icon">${emoji}</div>
            <div class="download-info">
                <div class="download-url" title="${escapeHtml(item.url)}">
                    ${escapeHtml(item.url)}
                </div>
                <div class="download-meta">
                    ${item.media_type || ''} &middot; ID: ${item.id}
                </div>
                ${isCompleted && item.download_path ? `
                    <div class="download-meta" style="color: var(--accent-success);">
                        📁 ${escapeHtml(item.download_path)}
                    </div>
                ` : ''}
                ${item.error_message ? `
                    <div class="download-meta" style="color: var(--accent-error);">
                        ⚠️ ${escapeHtml(item.error_message)}
                    </div>
                ` : ''}
            </div>
            <div class="download-status status-${item.status}">
                ${isInProgress ? '<span class="spinner"></span>' : ''}
                ${label}
            </div>
            <div class="download-actions">
                ${['pending', 'queued', 'in_progress'].includes(item.status) ? `
                    <button class="btn-icon" onclick="cancelDownload('${item.id}')" title="Cancel">
                        🛑
                    </button>
                ` : ''}
                <button class="btn-icon" onclick="deleteDownload('${item.id}')" title="Remove">
                    🗑️
                </button>
            </div>
        </div>
    `;
}

function updateDownloadItem(item) {
    const existing = document.querySelector(`.download-item[data-id="${item.id}"]`);
    if (existing) {
        existing.outerHTML = createDownloadItem(item);
    } else {
        // Prepend new item
        const wrapper = document.createElement('div');
        wrapper.innerHTML = createDownloadItem(item);
        dom.downloadsList.prepend(wrapper.firstElementChild);
    }
}

// ── Download Actions ───────────────────────────────────────────────

async function cancelDownload(id) {
    try {
        const result = await api.cancelDownload(id);
        showToast(result.message, 'info');
        await loadDownloads();
    } catch (err) {
        showToast(`Failed to cancel: ${err.message}`, 'error');
    }
}

async function deleteDownload(id) {
    // For now just cancel and hide
    try {
        await api.cancelDownload(id);
        const el = document.querySelector(`.download-item[data-id="${id}"]`);
        if (el) {
            el.style.opacity = '0';
            setTimeout(() => el.remove(), 300);
        }
    } catch (err) {
        showToast(`Failed to remove: ${err.message}`, 'error');
    }
}

// ── Theme Toggle ───────────────────────────────────────────────────

function getPreferredTheme() {
    const stored = localStorage.getItem('theme');
    if (stored) return stored;
    return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
}

function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
}

dom.themeToggle.addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-theme');
    setTheme(current === 'dark' ? 'light' : 'dark');
});

// ── Utility ────────────────────────────────────────────────────────

function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

// ── Initialization ─────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
    // Set theme
    setTheme(getPreferredTheme());

    // Load existing downloads
    loadDownloads();

    // Auto-refresh every 5 seconds
    setInterval(loadDownloads, 5000);

    // Refresh button
    dom.refreshBtn.addEventListener('click', loadDownloads);

    // Focus URL input
    dom.urlInput.focus();

    console.log('Universal Media Downloader UI initialized');
});