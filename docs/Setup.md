
### Steps to Set Up the Application:

1. **Create and activate a virtual environment**
	`py -m venv venv`
	`.\venv\Scripts\activate`
	or 
	`python3 -m venv venv`
	`source venv/bin/activate`
	
2. **Install the dependencies**
	`pip install -r requirements.txt`

3. **Run Migrations**  
    `py .\src\manage.py migrate`
	`python3 .\src\manage.py migrate`

4. **Create an Admin User**  
    `py .\src\manage.py createsuperuser`
	`python3 .\src\manage.py createsuperuser`
	
5. **Create Groups with Permissions**
    1. **Using a Command**  
        Run the following command to set up predefined groups:
        `py .\src\manage.py create_groups`
	**OR**
    2. **Using the Admin Page**
        - Navigate to the admin page and manually create groups with the following permissions:
            1. **Group Name**: Officer  
                **Permission**: `(leaves | Leave Approval | officer - approve stage 1 request)`
            2. **Group Name**: Manager  
                **Permission**: `(leaves | Leave Approval | manager - approve stage 2 request)`
            3. **Group Name**: HR  
                **Permission**: `(leaves | Leave Request | hr - view leaves)`

6. **Run the Development Server**  
	`py .\src\manage.py runserver`
	`python3 .\src\manage.py runserver`
	
7. **Create Users**
	Navigate to the `Admin Page` and then do the following:
    1. Create a user.
    2. Assign the user to one of the following groups: `Officer`, `Manager`, `HR`, or leave it unassigned.
    3. Set the user’s department in the profiles section.

8. **Create Leave Balances**
	Navigate to the `New Balance` to set up leave balances for each user.


**Note:**
If you want to test with the admin user, please ensure to add the admin user to the `Officer` group.