

import frappe
from frappe.model.document import Document

@frappe.whitelist()
def add_employee_role(employee, role, branch, department, designation, custom_acting_from, custom_acting_to):
    emp = frappe.get_doc("Employee", employee)

    # ✅ Add role if not already assigned
    user_id = emp.user_id
    if user_id and not frappe.db.exists("Has Role", {"parent": user_id, "role": role}):
        user_doc = frappe.get_doc("User", user_id)
        user_doc.append("roles", {"role": role})
        user_doc.save(ignore_permissions=True)

    # ✅ Check if internal_work_history row already exists
    exists = False
    for row in emp.internal_work_history:
        if (
            row.branch == branch and
            row.department == department and
            row.designation == designation and
            str(row.from_date) == str(custom_acting_from) and
            str(row.to_date) == str(custom_acting_to)
        ):
            exists = True
            break

    # ✅ Append only if not already added
    if not exists:
        emp.append("internal_work_history", {
            "branch": branch,
            "department": department,
            "designation": designation,
            "from_date": custom_acting_from,
            "to_date": custom_acting_to
        })

    # ✅ Set acting info
    emp.custom_acting = 1
    emp.custom_acting_from = custom_acting_from
    emp.custom_acting_to = custom_acting_to

    emp.save(ignore_permissions=True)





@frappe.whitelist()
def remove_employee_role(employee, role):
    emp = frappe.get_doc("Employee", employee)
    user_id = emp.user_id

    # Remove role from User
    if user_id:
        user_doc = frappe.get_doc("User", user_id)
        user_doc.roles = [r for r in user_doc.roles if r.role != role]
        user_doc.save(ignore_permissions=True)

    # Only unset acting flag (don't touch acting_from or acting_to)
    emp.custom_acting = 0
    emp.custom_role = ""
    emp.custom_acting_from = ""
    emp.custom_acting_to = ""

    # Save changes to Employee
    emp.save(ignore_permissions=True)




