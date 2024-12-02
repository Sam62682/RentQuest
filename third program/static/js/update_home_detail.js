const imageInput = document.getElementById('imageInput');
const gallery = document.getElementById('gallery');
const imageCount = document.getElementById('imageCount');

imageInput.addEventListener('change', function () {
    gallery.innerHTML = '';  // Clear previous images
    Array.from(imageInput.files).forEach(file => {
        const reader = new FileReader();
        reader.onload = function (e) {
            const img = document.createElement('img');
            img.src = e.target.result;
            gallery.appendChild(img);
        }
        reader.readAsDataURL(file);
    });
    imageCount.textContent = imageInput.files.length; // Update count
});
function setActive(activeId) {
    // Get all nav links
    const navLinks = document.querySelectorAll('.nav-link');

    // Remove active class from all links
    navLinks.forEach(link => {
        link.classList.remove('active');
    });

    // Add active class to the clicked link
    const activeLink = document.getElementById(activeId);
    activeLink.classList.add('active');
}