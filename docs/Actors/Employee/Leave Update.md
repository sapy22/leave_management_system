
**Purpose:**
Update the leave request dates.

**View:**
Page with form.

**Rules and Checks:**
1-Status:
    only approved request can be updated.

2-Changing Dates:
	-Before the leave is active:
		Can change start date and end date.
    -After the leave is active:
        Can only change end date.

3-User:
    Only the user who made the request can update it.

4-Leave Balance:
    User must have enough leave balance.

5-Unique:
	- Only one leave request should exist for the given combination of fields `employee`, `leave_type`, `from_date`, `to_date` and `officer`.

**Result:**
1-New leave request created based on the original request with the new dates and linked with the original request.