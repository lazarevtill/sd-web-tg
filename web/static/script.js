let currentPage = 1;
const page_size = 10;
const imageGrid = document.getElementById('image-grid');
const loadMoreButton = document.getElementById('load-more');

loadMoreButton.addEventListener('click', () => {
    currentPage++;
    fetchImages(currentPage);
});

function fetchImages(page) {
    fetch(`/images?page=${page}`)
        .then(response => response.json())
        .then(images => {
            if (images.length === 0) {
                loadMoreButton.style.display = 'none';
                return;
            }

            images.forEach(imageData => {
                const imageElement = new Image();
                imageElement.src = `data:image/jpeg;base64,${imageData}`;
                imageGrid.appendChild(imageElement);
            });
        })
        .catch(error => console.error('Error fetching images:', error));
}

fetchImages(currentPage);
