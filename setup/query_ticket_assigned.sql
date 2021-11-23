SELECT t.*, ic.name AS nome_categoria, rt.name AS origem, u.firstname AS nome_tecnico, c.avg_time AS tempo_medio_fechamento, d.avg_time AS tempo_medio_solucao  
FROM glpi_tickets t

LEFT JOIN glpi_itilcategories ic
ON t.itilcategories_id = ic.id

LEFT JOIN glpi_tickets_users tu
ON t.id = tu.tickets_id AND
tu.type = 2

LEFT JOIN glpi_requesttypes rt
ON t.requesttypes_id = rt.id

LEFT JOIN glpi_users u
ON u.id = tu.users_id

LEFT JOIN (
    SELECT ic.id, ic.completename, avg(t.close_delay_stat) AS avg_time FROM glpi_tickets t 
    LEFT JOIN glpi_itilcategories ic 
    ON t.itilcategories_id = ic.id 
    WHERE (DATE(t.date) BETWEEN %(first_day)s AND %(final_date)s)
    GROUP BY t.itilcategories_id
    ) c
ON t.itilcategories_id = c.id    

LEFT JOIN (
    SELECT ic.id, ic.completename, avg(t.solve_delay_stat) AS avg_time FROM glpi_tickets t 
    LEFT JOIN glpi_itilcategories ic 
    ON t.itilcategories_id = ic.id 
    WHERE (DATE(t.date) BETWEEN %(first_day)s AND %(final_date)s)
    GROUP BY t.itilcategories_id
    ) d
ON t.itilcategories_id = d.id

WHERE (DATE(t.date) BETWEEN %(initial_date)s AND %(final_date)s) AND
t.status = 6 