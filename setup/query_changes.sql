SELECT c.*, u.firstname AS nome_tecnico, ic.name AS nome_categoria, p.pesofield AS peso FROM glpi_changes c

LEFT JOIN glpi_changes_users cu
ON c.id = cu.changes_id AND cu.type = 2

LEFT JOIN glpi_users u
ON cu.users_id = u.id 

LEFT JOIN glpi_itilcategories ic
ON c.itilcategories_id = ic.id

LEFT JOIN glpi_plugin_fields_itilcategorypesos p
ON c.itilcategories_id = p.items_id

WHERE (date(c.date) BETWEEN %(initial_date)s AND %(final_date)s)
AND (c.status = 5 OR c.status = 6)