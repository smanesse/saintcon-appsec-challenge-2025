let selectedFile = null;
let uploadMethod = 'file';
let elements = {
    useUrl: document.querySelector("aside button:first-of-type"),
    useFile: document.querySelector("aside button:last-of-type"),
    fileUpload: document.getElementById("fileUpload"),
    urlUpload: document.getElementById("urlUpload"),
    fileLabel: document.getElementById("fileLabel"),
    submitBtn: document.getElementById('submitBtn'),
    loading: document.getElementById('loading'),
    errorMessage: document.getElementById('errorMessage'),
    fortuneResult: document.getElementById('fortuneResult'),
    photoUrl: document.getElementById("photoUrl"),
    fortuneCategory: document.getElementById("fortuneCategory"),
    fortuneText: document.getElementById("fortuneText")
};

function resetFortune() {
    elements.errorMessage.classList.remove('show');
    elements.fortuneCategory.innerText = "";
    elements.fortuneText.innerHTML = "<span></span>";
}

function selectMethod(method) {
    resetFortune();
    uploadMethod = method;
    const wantsFile = method === "file";
    elements.useUrl.classList.toggle("active", wantsFile);
    elements.fileUpload.classList.toggle("active", wantsFile);
    elements.useFile.classList.toggle("active", !wantsFile);
    elements.urlUpload.classList.toggle("active", !wantsFile);
    if (!wantsFile) {
        elements.photoUrl.focus();
    }
}

function handleFileSelect(event) {
    resetFortune();
    const file = event.target.files[0];
    if (file) {
        selectedFile = file;
        elements.fileLabel.textContent = file.name;
    }
}

async function getFortune() {
    resetFortune();

    if (uploadMethod === 'file' && !selectedFile) {
        elements.errorMessage.textContent = 'Please select a photo first';
        elements.errorMessage.classList.add('show');
        return;
    }

    if (uploadMethod === 'url') {
        const url = elements.photoUrl.value.trim();
        if (!url) {
            elements.errorMessage.textContent = 'Please enter an image URL';
            elements.errorMessage.classList.add('show');
            return;
        }
    }

    elements.submitBtn.disabled = true;
    elements.loading.classList.add('show');

    try {
        let response;

        if (uploadMethod === 'file') {
            const formData = new FormData();
            formData.append('photo', selectedFile);

            response = await fetch('/api/fortune', {
                method: 'POST',
                body: formData
            });
        } else {
            const url = elements.photoUrl.value.trim();
            response = await fetch('/api/fortune', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ image_url: url })
            });
        }

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Failed to read fortune');
        }

        elements.fortuneCategory.textContent = data.category || 'Your Fortune';
        elements.fortuneText.textContent = data.fortune;

        elements.fortuneResult.classList.remove('golden');
        if (data.special) {
            elements.fortuneResult.classList.add('golden');
        }

        elements.fortuneResult.classList.add('show');

    } catch (error) {
        elements.errorMessage.textContent = error.message;
        elements.errorMessage.classList.add('show');
    } finally {
        elements.loading.classList.remove('show');
        elements.submitBtn.disabled = false;
    }
}