$(document).ready(function() {
    var page = 1;
    var isModalOpen = false;

    function loadImages() {
        $.ajax({
            url: '/load_images',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ 'page': page }),
            beforeSend: function() {
                $('#loading-message').show();
            },
            success: function(response) {
                var imageUrls = response.image_urls;
                var next_page = response.next_page;

                var imageContainer = $('.image-container');
                $.each(imageUrls, function(index, imageUrl) {
                    var imageItem = $('<div>').addClass('image-item');
                    var image = $('<img>').attr('src', imageUrl);
                    image.on('click', function() {
                        openModal(imageUrl);
                    });
                    image.appendTo(imageItem);
                    imageItem.appendTo(imageContainer);
                });

                page = next_page;

                if (page) {
                    $('#loading-message').hide();
                } else {
                    $('#loading-message').text('No more images to load').show();
                    $('#load-more-button').hide();
                }
            }
        });
    }

    function openModal(imageUrl) {
        var modal = $('#modal');
        var modalImage = $('#modal-image');
        modalImage.attr('src', imageUrl);
        modal.show();
        isModalOpen = true;
    }

    function closeModal() {
        var modal = $('#modal');
        modal.hide();
        isModalOpen = false;
    }

    function loadMoreImages() {
        loadImages();
    }

    $(window).scroll(function() {
        if ($(window).scrollTop() + $(window).height() >= $(document).height()) {
            loadImages();
        }
    });

    $('#modal').click(function() {
        closeModal();
    });

    $('#modal-image').click(function(e) {
        e.stopPropagation();
        if (isModalOpen) {
            closeModal();
        }
    });

    $(document).keyup(function(e) {
        if (e.key === 'Escape' && isModalOpen) {
            closeModal();
        }
    });

    $('#load-more-button').click(function() {
        loadMoreImages();
    });

    // Initial load of images
    loadImages();
});
