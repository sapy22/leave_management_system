
**Purpose**:
Approve/Reject the leave request.

**View:**
Button with form.

**Workflow:**
[[Approval Workflow.canvas|Approval Workflow]]

_____

## 1- Officer:

**Rules and Checks:**
1-Department
    - Only requests from employees in the same department can be approved/rejected.

2-Status:
    - Only pending request can be approved/rejected.

3-Stage:
	- Only stage 1 request can be approved/rejected.

4-Permissions:
	- Officer

**Result:**
1. Approve
    - **Leave Approval Record**: create a new leave approval with status `approved` and stage `1`.
    - **Approval Stage**: advance the leave Approval stage to `2`.
2. Reject
    - **Leave Approval Record:** create a new leave approval with status `rejected` and stage `1`.
    - **Leave Status**: update the leave request status to `rejected`.

____

## 2- Manager:

**Rules and Checks:**
1-Status:
    - Only pending request can be approved/rejected.

2-Stage:
	- Only stage 2 request can be approved/rejected.

3-Permissions:
	- Manager

**Result:**
1-New Request:
1. Approve:
    - **Leave Approval Record:** create a new leave approval with status `approved` and stage `2`.
    - **Leave Status**: update the leave request status to `approved`.
    - **Leave Balance**: deduct the leave duration from the leave balance.
2. Reject:
    - **Leave Approval Record**: create a new leave approval with status `rejected` and stage `2`.
    - **Leave Status**: update the leave request status to `rejected`.

2-Updated Request:
1. Approve:
    - **Leave Approval Record:** create a new leave approval with status `approved` and stage `2`.
    - **Leave Status**: 
	    1- Update the leave request status to `approved`.
		2- Update the original leave request status to `modified`.
    - **Leave Balance**: 
	    1- Restore the original leave duration to the leave balance.
	    2- Deduct the new leave duration from the leave balance.
2. Reject:
    - **Leave Approval Record**: create a new leave approval with status `rejected` and stage `2`.
    - **Leave Status**: update the leave request status to `rejected`.
