const imageInput = document.getElementById('imageInput');
const gallery = document.getElementById('gallery');
const imageCount = document.getElementById('imageCount');
const prevButton = document.getElementById('prevButton');
const nextButton = document.getElementById('nextButton');

let currentIndex = 0;
const imagesPerPage = 3;
let imageArray = [];

document.getElementById('addImagesButton').addEventListener('click', () => {
    const files = imageInput.files;
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const imgUrl = URL.createObjectURL(file);
        imageArray.push(imgUrl);
        const img = document.createElement('img');
        img.src = imgUrl;
        img.alt = `Image ${imageArray.length}`;
        gallery.appendChild(img);
    }
    imageCount.textContent = imageArray.length;
    imageInput.value = ''; // Clear the input
    showImages();
});

function showImages() {
    const startIndex = currentIndex * imagesPerPage;
    const endIndex = startIndex + imagesPerPage;

    // Clear the gallery and show only the images for the current page
    gallery.innerHTML = '';
    const imagesToShow = imageArray.slice(startIndex, endIndex);
    imagesToShow.forEach((imgSrc) => {
        const img = document.createElement('img');
        img.src = imgSrc;
        gallery.appendChild(img);
    });

    // Disable buttons based on the current index
    prevButton.disabled = currentIndex === 0;
    nextButton.disabled = endIndex >= imageArray.length;
}

prevButton.addEventListener('click', () => {
    if (currentIndex > 0) {
        currentIndex--;
        showImages();
    }
});

nextButton.addEventListener('click', () => {
    if ((currentIndex + 1) * imagesPerPage < imageArray.length) {
        currentIndex++;
        showImages();
    }
})