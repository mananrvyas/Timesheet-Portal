# Timesheet Portal

[Timesheet Portal](https://timesheet.mananvyas.in/) is a full-stack weekly time logging software built using Python. It allows users to log their work hours and submit timesheets for approval.

## Features

- User registration and login
- Weekly timesheet submission
- Default schedule setup for users
- Admin approval/rejection of timesheets
- User profile management
- Email notifications for timesheet submission and approval/rejection
- Data persistence using a MySQL database

## Technologies Used

- Python
- Streamlit (for the web interface)
- MySQL (for data storage)
- Mailgun (for email notifications)

## Class Design

The system is designed using the following main classes:

- `StandardUser`: Represents a standard user who can submit timesheets and manage their profile.
- `AdminUser`: Extends the `StandardUser` class and adds functionality for approving/rejecting timesheets.
- `TimeSlot`: Represents a single time slot entry in a timesheet.
- `PayPeriod`: Represents a pay period and contains the timesheet for that period.

Here's a UML diagram illustrating the class design:

![alt text](https://timesheet.mananvyas.in/UML.png)

## Setup and Installation

1. Clone the repository:
   ``` git clone https://github.com/mananrvyas/Timesheet-Portal.git ```
2. Install the required dependencies:
   ```pip install -r requirements.txt```
3. Set up a MySQL database (preferably using phpMyAdmin) and update the database connection details in the code.

4. Create a `.env` file in the project root directory with the following variables:
   ```MAILGUN_API_KEY=your_mailgun_api_key
      DB_HOST=your_database_host
      DB_USER=your_database_username
      DB_PASSWORD=your_database_password
      DB_NAME=your_database_name
5. Run the application:
   ```streamlit run app.py```
6. Access the application in your web browser at `http://localhost:8501`.

## Usage

- Users can register, log in, and manage their profile.
- Users can set up their default schedule and submit weekly timesheets.
- Admin users can approve or reject submitted timesheets.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
