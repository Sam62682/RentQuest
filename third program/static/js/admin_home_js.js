// Listen for the submit event on the room form
document.getElementById('roomForm').addEventListener('submit', function (event) {
    // Prevent the default form submission behavior
    event.preventDefault();

    // Get values from the form inputs
    const roomName = document.getElementById('roomName').value;
    const location = document.getElementById('location').value;
    const price = document.getElementById('price').value;
    const description = document.getElementById('description').value;
    const imageFile = document.getElementById('image').files[0];

    // Create a URL for the image file
    const imageURL = URL.createObjectURL(imageFile);

    // Get the display area for rooms
    const roomDisplay = document.getElementById('roomDisplay');

    // Create a new div element to show the room details
    const roomDiv = document.createElement('div');
    roomDiv.classList.add('room');

    // Set the inner HTML of the room div
    roomDiv.innerHTML = `
        <img src="${imageURL}" alt="${roomName}">
        <h3>${roomName}</h3>
        <p><strong>Location:</strong> ${location}</p>
        <p><strong>Price:</strong> $${price}/month</p>
        <p><strong>Description:</strong> ${description}</p>
    `;

    // Append the new room div to the display area
    roomDisplay.appendChild(roomDiv);

    // Reset the form fields
    this.reset();
});

// Function to open the upload modal
function openModal() {
    document.getElementById('uploadModal').style.display = 'flex';
}

// Function to close the upload modal
function closeModal() {
    document.getElementById('uploadModal').style.display = 'none';
}

// Listen for the click event on the save button
document.getElementById('saveButton').addEventListener('click', function () {
    // Get the file input element
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];

    // Check if a file was selected
    if (file) {
        // Create a FormData object to send the file
        const formData = new FormData();
        formData.append('file', file);

        // Send the file to the server using fetch
        fetch('/upload_profile_picture', {
            method: 'POST',
            body: formData,
        })
            .then(response => response.json())
            .then(data => {
                // Check if the upload was successful
                if (data.imageUrl) {
                    // Update the profile image with the new URL
                    document.getElementById('profileImage').src = data.imageUrl;
                    closeModal(); // Close the modal
                } else {
                    // Show an error message if the upload failed
                    alert('Failed to upload image: ' + data.error);
                }
            })
            .catch(error => {
                // Log any errors to the console
                console.error('Error:', error);
            });
    }
});
