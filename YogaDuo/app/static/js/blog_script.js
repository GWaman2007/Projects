document.addEventListener('DOMContentLoaded', function () {
    console.log('DOM fully loaded and parsed');

    // Blog form handling
    const blogForm = document.getElementById('blogForm');
    if (blogForm) {
        console.log('blogForm found');
        blogForm.addEventListener('submit', function (event) {
            const elements = document.getElementsByName('elements[]');
            elements.forEach((el) => {
                if (el.tagName === 'INPUT' && el.type === 'text') {
                    el.value = 'Subtitle: ' + el.value;
                } else if (el.tagName === 'TEXTAREA') {
                    el.value = 'Paragraph: ' + el.value;
                }
            });
        });
    }

    // Responsive menu toggle
    const menuToggle = document.querySelector('.menu-toggle');
    const menu = document.querySelector('.menu');
    if (menuToggle && menu) {
        console.log('menuToggle and menu found');
        menuToggle.addEventListener('click', function () {
            menu.classList.toggle('active');
        });

        document.addEventListener('click', function (event) {
            if (!menu.contains(event.target) && !menuToggle.contains(event.target)) {
                menu.classList.remove('active');
            }
        });
    } else {
        console.log('menuToggle or menu not found');
    }

    // Fade-out for flash messages
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach((flashMessage) => {
        setTimeout(() => {
            flashMessage.classList.add('flash-hidden');
        }, 5000);
    });

    // Load more blogs
    const loadMoreButton = document.getElementById('load-more');
    if (loadMoreButton) {
        loadMoreButton.addEventListener('click', function () {
            const offset = document.querySelectorAll('#latest-blogs .blog-item').length;
            fetch('/load_more_blogs', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ offset })
            })
                .then((response) => response.json())
                .then((data) => {
                    if (data.length === 0) {
                        alert('No more blogs to load!');
                        return;
                    }
                    const latestBlogsContainer = document.getElementById('latest-blogs');
                    data.forEach((blog) => {
                        const blogItem = document.createElement('div');
                        blogItem.classList.add('blog-item');
                        blogItem.innerHTML = `
                            <h3>${blog.title}</h3>
                            ${blog.image ? `<img src="/static/images/${blog.image}" alt="${blog.title}">` : ''}
                            <p>${blog.excerpt}</p>
                            <a href="/blog/${blog.id}" class="btn">Read More</a>
                        `;
                        latestBlogsContainer.appendChild(blogItem);
                    });
                })
                .catch((error) => console.error('Error loading more blogs:', error));
        });
    }

    // Smooth page transitions
    window.addEventListener('load', () => {
        document.body.classList.add('fade-in');
    });

    // Floating header
    const header = document.querySelector('.header');
    window.addEventListener('scroll', () => {
        if (header) {
            if (window.scrollY > 50) {
                header.classList.add('shrink');
            } else {
                header.classList.remove('shrink');
            }
        }
    });

    // Slide-in animation for new comments/posts
    const newCommentsElements = document.querySelectorAll('.new-comment, .new-post');
    newCommentsElements.forEach((comment) => {
        comment.classList.add('slide-in');
    });
});

// Element addition for blog creation
function addElement(type) {
    const container = document.getElementById('blogElements');
    let element;

    switch (type) {
        case 'subtitle':
            element = document.createElement('input');
            element.type = 'text';
            element.name = 'elements[]';
            element.placeholder = 'Subtitle';
            break;

        case 'paragraph':
            element = document.createElement('textarea');
            element.name = 'elements[]';
            element.placeholder = 'Paragraph';
            break;

        case 'image':
            const fileInput = document.createElement('input');
            fileInput.type = 'file';
            fileInput.name = 'images[]';
            fileInput.accept = 'image/*';

            const hiddenInput = document.createElement('input');
            hiddenInput.type = 'hidden';
            hiddenInput.name = 'elements[]';

            fileInput.addEventListener('change', () => {
                if (fileInput.files.length > 0) {
                    hiddenInput.value = 'Image: ' + fileInput.files[0].name;
                }
            });

            container.appendChild(fileInput);
            container.appendChild(hiddenInput);
            return;
    }

    container.appendChild(element);
}

document.addEventListener('DOMContentLoaded', () => {
    const toggleDesktop = document.getElementById('dark-mode-toggle');
    const toggleMobile = document.getElementById('dark-mode-toggle-mobile');
    const body = document.body;
    const headerPhone = document.querySelector('.header-phone');

    // Disable transition temporarily on page load
    body.style.transition = 'none';

    // Load the user's dark mode preference
    const darkMode = localStorage.getItem('darkMode');
    if (darkMode === 'enabled') {
        body.classList.add('dark-mode');
        if (toggleDesktop) toggleDesktop.checked = true;
        if (toggleMobile) toggleMobile.checked = true;
    }

    // Function to enable/disable dark mode
    const toggleDarkMode = (isEnabled) => {
        if (isEnabled) {
            body.classList.add('dark-mode');
            localStorage.setItem('darkMode', 'enabled');
        } else {
            body.classList.remove('dark-mode');
            localStorage.setItem('darkMode', 'disabled');
        }
    };

    // Event listeners for desktop and mobile toggles
    if (toggleDesktop) {
        toggleDesktop.addEventListener('change', () => {
            toggleDarkMode(toggleDesktop.checked);
        });
    }

    if (toggleMobile) {
        toggleMobile.addEventListener('change', () => {
            toggleDarkMode(toggleMobile.checked);
        });
    }

    // Add shadow to the mobile header when scrolling
    if (headerPhone) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 10) {
                headerPhone.classList.add('scrolled');
            } else {
                headerPhone.classList.remove('scrolled');
            }
        });
    }
});

