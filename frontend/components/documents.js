async function uploadDocument() {
    const f = file.files[0];

    if (!f) {
        uploadMsg.textContent = 'Select a document first.';
        return;
    }

    const fd = new FormData();
    fd.append('file', f);
    fd.append('category', category.value || 'General');

    const { response, data } = await api(
        '/api/documents/upload',
        {
            method: 'POST',
            body: fd
        }
    );

    uploadMsg.textContent =
        data.message || data.detail || 'Upload failed';

    if (response.ok) {
        file.value = '';
        loadDocuments();
    }
}


async function searchDocumentsUI() {
    const q = query.value.trim();

    if (!q) {
        results.innerHTML = '';
        return;
    }

    const { response, data } = await api(
        '/api/search?q=' + encodeURIComponent(q)
    );

    if (!response.ok) {
        results.innerHTML =
            '<p class="muted">Search failed.</p>';
        return;
    }

    results.innerHTML = data.length
        ? data.map(d => `
            <div class="result">
                <b>${d.title}</b><br>

                <span class="muted">
                    ${d.filename} · ${d.category} · relevance ${d.score}%
                </span>

                <br><br>

                <button onclick="downloadDocument(${d.id})">
                    Download
                </button>

                <button onclick="deleteDocument(${d.id})">
                    Delete
                </button>
            </div>
        `).join('')
        : '<p class="muted">No relevant documents found.</p>';
}


async function loadDocuments() {
    const { response, data } = await api('/api/documents');

    if (!response.ok) {
        return;
    }

    docs.innerHTML = data.length
        ? data.map(d => `
            <div class="result">
                <b>${d.title}</b><br>

                <span class="muted">
                    ${d.filename} · ${d.category}
                </span>

                <br><br>

                <button onclick="downloadDocument(${d.id})">
                    Download
                </button>

                <button onclick="deleteDocument(${d.id})">
                    Delete
                </button>
            </div>
        `).join('')
        : '<p class="muted">No documents uploaded yet.</p>';
}


async function downloadDocument(id) {
    const r = await fetch(
        API + '/api/documents/' + id + '/download',
        {
            headers: {
                Authorization:
                    'Bearer ' + localStorage.getItem('token')
            }
        }
    );

    if (!r.ok) {
        alert('Download failed');
        return;
    }

    const b = await r.blob();
    const u = URL.createObjectURL(b);

    const a = document.createElement('a');

    a.href = u;
    a.download = 'document';
    document.body.appendChild(a);
    a.click();
    a.remove();

    URL.revokeObjectURL(u);
}


async function deleteDocument(id) {

    const confirmDelete = confirm(
        'Are you sure you want to delete this document?'
    );

    if (!confirmDelete) {
        return;
    }

    const { response, data } = await api(
        '/api/documents/' + id,
        {
            method: 'DELETE'
        }
    );

    if (!response.ok) {
        alert(data.detail || 'Delete failed');
        return;
    }

    alert(data.message || 'Document deleted successfully');

    loadDocuments();
    results.innerHTML = '';
}