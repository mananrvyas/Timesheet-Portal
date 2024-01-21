function deleteTimeslot(day, slotIndex) {
    // Send a POST request to the server to delete the specified timeslot
    const formData = new FormData();
    formData.append('day', day);
    formData.append('slot_index', slotIndex);

    fetch('/delete_timeslot', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Refresh the page to reflect the updated schedule
            window.location.reload();
        } else {
            alert('Failed to delete timeslot: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function addTimeslot(day) {
    const timeslotContainer = document.getElementById(day.toLowerCase() + '-timeslots');
    const timeslotCount = timeslotContainer.children.length;

    if (timeslotCount >= 2) {
        alert('You cannot add more than two timeslots per day.');
        return;
    }

    const slotIndex = timeslotCount + 1;
    const newTimeslotDiv = document.createElement('div');
    newTimeslotDiv.classList.add('timeslot');
    newTimeslotDiv.innerHTML = `
        <label for="${day.toLowerCase()}-${slotIndex}-start">Start:</label>
        <input type="time" id="${day.toLowerCase()}-${slotIndex}-start" name="${day.toLowerCase()}-${slotIndex}-start">
        <label for="${day.toLowerCase()}-${slotIndex}-end">End:</label>
        <input type="time" id="${day.toLowerCase()}-${slotIndex}-end" name="${day.toLowerCase()}-${slotIndex}-end">
    `;
    timeslotContainer.appendChild(newTimeslotDiv);
}
