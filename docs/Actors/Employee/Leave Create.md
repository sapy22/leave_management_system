
**Purpose**:
Create a new leave request.

**View:**
Page with form.

**Rules and Checks:**
1-Type:
    The leave type match the balance type.

2-Leave Balance:
    User must have enough leave balance.

3-Sick Leave:
	leave balance is not required.

4-Dates:
	End date >= start date.

5-Officer:
	The officer must be on same department.

6-Unique:
	- Only one leave request should exist for the given combination of fields `employee`, `leave_type`, `from_date`, `to_date` and `officer`.

**Result:**
1-New leave request created.