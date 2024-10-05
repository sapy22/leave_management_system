
**Purpose**:
Create a new leave balance.

**View:**
Page with form.

**Rules and Checks:**
1-Permissions:
	- Balance_Manager

2-Type:
	Sick leave not listed.

3-Unique:
	- Only one balance should exist for the given combination of fields employee, `leave_type`, `from_date`, and `to_date`.

**Result:**
1-New leave balance created.