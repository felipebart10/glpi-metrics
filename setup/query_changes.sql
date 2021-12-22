SELECT c.*, u.firstname FROM glpi_changes c

LEFT JOIN glpi_changes_users cu
ON c.id = cu.changes_id AND cu.type = 2

LEFT JOIN glpi_users u
ON cu.users_id = u.id 

WHERE (date(c.date) BETWEEN %(initial_date)s AND %(final_date)s)
AND (c.status = 5 OR c.status = 6)