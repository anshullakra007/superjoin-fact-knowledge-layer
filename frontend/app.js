document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const uploadStatus = document.getElementById('upload-status');
    
    // Fetch initial data
    fetchData();
    setInterval(fetchData, 5000); // Poll for updates

    // Drag and Drop Handlers
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            uploadFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length) {
            uploadFile(e.target.files[0]);
        }
    });

    function uploadFile(file) {
        if (file.type !== 'application/pdf') {
            uploadStatus.textContent = 'Error: Only PDF files are allowed.';
            uploadStatus.style.color = 'var(--danger)';
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        uploadStatus.textContent = `Uploading ${file.name}...`;
        uploadStatus.style.color = 'var(--text-secondary)';

        fetch('/api/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            uploadStatus.textContent = `Uploaded! Processing ${file.name} in background...`;
            uploadStatus.style.color = 'var(--success)';
            fetchData(); // Fetch right away to update doc list
        })
        .catch(err => {
            uploadStatus.textContent = 'Upload failed.';
            uploadStatus.style.color = 'var(--danger)';
            console.error(err);
        });
    }

    function fetchData() {
        fetch('/api/documents').then(r => r.json()).then(renderDocuments);
        fetch('/api/facts').then(r => r.json()).then(renderFacts);
        fetch('/api/relationships').then(r => r.json()).then(renderRelationships);
    }

    function renderDocuments(docs) {
        const list = document.getElementById('doc-list');
        list.innerHTML = '';
        if (docs.length === 0) {
            list.innerHTML = '<li>No documents uploaded yet.</li>';
            return;
        }
        docs.forEach(doc => {
            const li = document.createElement('li');
            li.textContent = doc.filename;
            list.appendChild(li);
        });
    }

    function renderFacts(facts) {
        const tbody = document.querySelector('#facts-table tbody');
        tbody.innerHTML = '';
        if (facts.length === 0) {
            tbody.innerHTML = '<tr><td colspan="3" style="text-align:center">No facts extracted yet.</td></tr>';
            return;
        }
        facts.forEach(fact => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${fact.statement}</td>
                <td><small>"${fact.evidence}"</small></td>
                <td>${fact.document} (pg ${fact.page_number})</td>
            `;
            tbody.appendChild(tr);
        });
    }

    function renderRelationships(rels) {
        const container = document.getElementById('relationships-list');
        if (rels.length === 0) {
            // Keep empty state if nothing
            return;
        }
        container.innerHTML = '';
        rels.forEach(rel => {
            const card = document.createElement('div');
            card.className = `relationship-card ${rel.type}`;
            card.innerHTML = `
                <div class="rel-badge">${rel.type}</div>
                <div class="rel-facts">
                    <div><strong>Fact 1 (${rel.fact1.document}):</strong> ${rel.fact1.statement}</div>
                    <div><strong>Fact 2 (${rel.fact2.document}):</strong> ${rel.fact2.statement}</div>
                </div>
                <div class="rel-explanation">${rel.explanation}</div>
            `;
            container.appendChild(card);
        });
    }
});
