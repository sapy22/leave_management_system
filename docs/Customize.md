
### 1. Leave Type

- Located in: `src.leaves.models.LEAVE_TYPE`
- You can customize the types of leave available in the system.

### 2. Department

- Located in: `src.profiles.models.Profile.DEPARTMENT`
- This defines the departments within your organization.

### 3. Approval Workflow

The system is based on a two-stage approval process, with an Officer assigned to each department. However, you can modify this logic as needed.

- **Officer**  
    Located in: `src.leaves.forms.LeaveRequestCreateForm`  
    You can modify the query here to match your business logic. For example, if you have specific officers, you can adjust the query to reflect that.
    
- **Manager**  
    Located in: `src.leaves.models.LeaveRequest`  
    If a single-stage approval process is sufficient for your organization, you can change the default value of `approval_stage` to `2`, skipping the Officer step.