function uploadProfileImage() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];

    if (file) {
        const reader = new FileReader();
        reader.onload = function (e) {
            // Update profile image preview
            document.getElementById('profileImage').src = e.target.result;
        };
        reader.readAsDataURL(file);

        const formData = new FormData();
        formData.append('profile_image', file);
        formData.append('user_id', '{{ user_id }}');  // Ensure user_id is passed correctly

        fetch('/update_profile_image', {
            method: 'POST',
            body: formData
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('Image updated successfully:', data);
            })
            .catch(error => {
                console.error('Error updating image:', error);
            });

        closeModal();
    } else {
        alert("Please select an image file.");
    }
}