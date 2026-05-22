document.addEventListener('DOMContentLoaded', () => {
    const deadlineElement = document.querySelector('[data-deadline]');
    if (deadlineElement) {
        const deadline = new Date(deadlineElement.getAttribute('data-deadline'));
        if (new Date() > deadline) {
            const btn = document.querySelector('.registration-form .btn-primary');
            if (btn) {
                btn.disabled = true;
                btn.classList.add('btn-disabled');
            }
        }
    }

    document.querySelectorAll('a[href*="#form"]').forEach(link => {
        link.addEventListener('click', (e) => {
            const url = new URL(link.href);
            if (url.pathname !== window.location.pathname || url.search !== window.location.search) {
                return;
            }
            e.preventDefault();
            const formElement = document.querySelector('#form');
            if (formElement) {
                formElement.scrollIntoView({ behavior: 'smooth' });
                setTimeout(() => {
                    const firstInput = formElement.querySelector('input');
                    if (firstInput) firstInput.focus();
                }, 500);
            }
        });
    });
});
