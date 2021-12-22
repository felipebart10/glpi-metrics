SELECT p.*, u.firstname FROM glpi_problems p

LEFT JOIN glpi_problems_users pu
ON p.id = pu.problems_id AND pu.type = 2

LEFT JOIN glpi_users u
ON pu.users_id = u.id 

WHERE (date(p.date) BETWEEN %(initial_date)s AND %(final_date)s)
AND (p.status = 5 OR p.status = 6)