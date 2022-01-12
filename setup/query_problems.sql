SELECT p.*, u.firstname AS nome_tecnico, ic.name AS nome_categoria, peso.pesofield AS peso FROM glpi_problems p

LEFT JOIN glpi_problems_users pu
ON p.id = pu.problems_id AND pu.type = 2

LEFT JOIN glpi_users u
ON pu.users_id = u.id

LEFT JOIN glpi_itilcategories ic
ON p.itilcategories_id = ic.id

LEFT JOIN glpi_plugin_fields_itilcategorypesos peso
ON p.itilcategories_id = peso.items_id

WHERE (date(p.date) BETWEEN %(initial_date)s AND %(final_date)s)
AND (p.status = 5 OR p.status = 6)