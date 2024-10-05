
## Overview

The **Leave Management System** is a simple, user-friendly application designed to streamline the process of managing employee leave requests.

## Features

- **User Accounts**: Each employee has a unique account where they can log in, view their leave balance, and submit leave requests.

- **Leave Requests**: Employees can submit requests for different types of leave, such as Annual Leave, sick leave, directly through the system.

- **Approval Workflow**: Submitted leave requests are automatically forwarded to the respective personnel for approval or rejection.

- **Leave Balance Tracking**: The system keeps track of each employee's leave balance, updating it automatically as leave is approved and taken.

- **Email Notification**s: Automated email notifications keep users informed about the status of their leave requests.

## Actors:

- **Admin**: Manages users and leave balances within the system.
	- **Actions**: View, Create, Update

- **Employee**: Submits leave requests, specifying the type and duration of the leave.
    - **Actions**: View, Create, Cancel, Update

- **Officer**: The first reviewer of leave requests for employees within the same department. The Officer can approve or reject requests. Upon approval, the request is forwarded to the next reviewer.
    - **Actions**: View, Approve, Reject

- **Manager**: Conducts the final review of leave requests. The manager can either approve or reject the request. Upon approval, the system updates the employee's leave balance.
    - **Actions**: View, Approve, Reject

- **HR**: Monitors and tracks all leave requests 
    - **Actions**: View

## Technology Stack

- **Frontend**: HTML, CSS (Bootstrap 5), JavaScript
- **Backend**: Python (Django)