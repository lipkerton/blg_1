let postModal = null;
document.addEventListener('DOMContentLoaded', function() {
    // Инициализируем модальное окно Bootstrap
    postModal = new bootstrap.Modal(
	    document.getElementById('createPostModal')
	);
    // Назначаем обработчик на кнопку "Написать пост"
    document.querySelector('.create-post-btn').addEventListener(
	    'click', openPostModal
    );
    // Обработчик для кнопки публикаци
	document.getElementById('publishBtn').addEventListener(
		'click', publishPost
	);
    // Счетчики символов
    setupCharacterCounters();
    // Очистка формы при закрытии модального окна
    document.getElementById('createPostModal').addEventListener(
	    'hidden.bs.modal', clearForm
    );
});
function openPostModal() {
    postModal.show();
    document.getElementById('postTitle').focus();
}
function setupCharacterCounters() {
    const titleInput = document.getElementById('postTitle');
    const contentInput = document.getElementById('postContent');
    const titleCounter = document.getElementById('titleCounter');
    const contentCounter = document.getElementById('contentCounter');

    titleInput.addEventListener(
        'input', function() {
            updateCounter(this, titleCounter, 100);
        }
    );
    contentInput.addEventListener(
        'input', function() {
            updateCounter(this, contentCounter, 5000);
        }
    );
}
function updateCounter(inputElement, counterElement, maxLength) {
    const length = inputElement.value.length;
    counterElement.textContent = length;

    counterElement.classList.remove('near-limit', 'over-limit');
    if (length > maxLength * 0.9) {
        counterElement.classList.add('near-limit')
    };
    if (length > maxLength) {
        counterElement.classList.add('over-limit');
        inputElement.classList.add('is-invalid');
    } else {
        inputElement.classList.remove('is-invalid');
    }
}
async function publishPost() {
    const title = document.getElementById('postTitle').value.trim();
    const content = document.getElementById('postContent').value.trim();

    if (!validateForm(title, content)) {
        return;
    }

    showLoading(true);

    const jwtToken = getJWTToken();

    const postData = {
        title: title,
        content: content
    }
    try {
        const response = await fetch('/api/p', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${jwtToken}`
            },
            body: JSON.stringify(postData)
        });
        
        const result = await response.json();

        if (response.ok) {
            showMessage('cool story', 'success');
            setTimeout(() => {
                postModal.hide();
                addPostToFeed(result.post);
                updatePostCount(1);
            }, 1500);
        } else {
            throw new Error(result.error || 'something went wrong during shitposting')
        }
    } catch (error) {
        console.error('error:', error);
        showMessage(`error ${error.message}`, 'danger');
    } finally {
        showLoading(false);
    }
    
    // валидация
    if (!title) {
        showFormMessage('cant be empty', 'danger');
        document.getElementById('postTitle').focus();
        return false;
    }
    if (title.length <= 3) {
        showFormMessage('pls 3 symbols at least', 'danger');
        document.getElementById('postTitle').focus();
        return false;
    }
    if (title.length > 100) {
        showFormMessage('title is too big', 'danger');
        document.getElementById('postTitle').focus();
        return false;
    }
    if (!content) {
        showFormMessage('cant be empty', 'danger');
        document.getElementById('postContent').focus();
        return false;
    }
    if (content.length <= 10) {
        showFormMessage('pls 10 symbols at least', 'danger');
        document.getElementById('postContent').focus();
        return false;
    }
    if (content.length > 5000) {
        showFormMessage('content is too big', 'danger');
        document.getElementById('postContent').focus();
        return false;
    }
    return true;
}
function showFormMessage(message, type) {
    const formMessage = document.getElementById('formMessage');
    formMessage.textContent = message;
    formMessage.className = `alert alert-${type}`;
    formMessage.classList.remove('d-none');

    setTimeout(() => {
        formMessage.classList.add('d-none');
    }, 5000);
}
function showLoading(isLoading) {
    const loadingElement = document.getElementById('formLoading');
    const publishBtn = document.getElementById('publishBtn');

    if (isLoading) {
        loadingElement.classList.remove('d-none');
        publishBtn.disabled = true;
        
    }
}