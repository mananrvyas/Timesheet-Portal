function calculatePayPeriods(referenceEndDate) {
    const currentDate = new Date();
    const daysDifference = Math.floor((currentDate - referenceEndDate) / (1000 * 60 * 60 * 24));
    const completedPeriods = Math.floor(daysDifference / 14);

    const currentPeriodStart = new Date(referenceEndDate);
    currentPeriodStart.setDate(referenceEndDate.getDate() - (completedPeriods * 14));

    const previousPeriodStart = new Date(currentPeriodStart);
    previousPeriodStart.setDate(currentPeriodStart.getDate() - 14);

    return { currentPeriodStart, previousPeriodStart };
}

function showTimesheetForm() {
    const referenceEndDate = new Date(2024, 0, 28); // January 27, 2024
    const { currentPeriodStart, previousPeriodStart } = calculatePayPeriods(referenceEndDate);

    const payPeriodSelect = document.getElementById('pay-period-select');
    payPeriodSelect.innerHTML = '';
    payPeriodSelect.add(new Option(formatPayPeriod(currentPeriodStart), currentPeriodStart.toISOString()));
    payPeriodSelect.add(new Option(formatPayPeriod(previousPeriodStart), previousPeriodStart.toISOString()));

    document.getElementById('timesheet-form-container').style.display = 'block';
    updateTimesheetDates(currentPeriodStart);
}

function formatPayPeriod(start) {
    const end = new Date(start);
    end.setDate(start.getDate() + 13);
    return `Pay Period: ${start.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'numeric', day: 'numeric' })} - ${end.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'numeric', day: 'numeric' })}`;
}
function updateTimesheetDates(startDate) {
    const timesheetContainer = document.getElementById('timesheet-dates-container');
    timesheetContainer.innerHTML = '';

    for (let i = 0; i < 14; i++) {
        const date = new Date(startDate);
        date.setDate(startDate.getDate() + i);
        for (let slot = 1; slot <= 2; slot++) {
            timesheetContainer.innerHTML += `
                <div class="timesheet-day">
                    <label>${date.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'numeric', day: 'numeric' })} Timeslot ${slot}</label>
                    <input type="time" name="${date.toLocaleDateString()}-slot${slot}-start">
                    <input type="time" name="${date.toLocaleDateString()}-slot${slot}-end">
                </div>
            `;
        }
    }
}


document.getElementById('pay-period-select').addEventListener('change', function() {
    const selectedStartDate = new Date(this.value);
    updateTimesheetDates(selectedStartDate);
});
