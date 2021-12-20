SELECT
    t.id,
    date(tt.date) AS data_tarefa,
    date(att.actual_end) AS ultima_modificacao,
    u2.firstname as tecnico_do_chamado,
    u.firstname as tecnico_das_tarefas,
    ic.name as categoria_chamado,
    sum(att.actual_actiontime) as tempo_via_plugin,
    sum(tt.actiontime) as tempo_via_glpi
FROM glpi_tickets t

LEFT JOIN glpi_tickettasks tt
ON t.id = tt.tickets_id

LEFT JOIN glpi_itilcategories ic
ON t.itilcategories_id = ic.id

LEFT JOIN glpi_tickets_users tu
ON t.id = tu.tickets_id AND tu.type = 2

LEFT JOIN glpi_users u2
ON u2.id = tu.users_id

LEFT JOIN glpi_users u
ON u.id = tt.users_id_tech

LEFT JOIN glpi_plugin_actualtime_tasks att
ON tt.id = att.tasks_id

WHERE (DATE(att.actual_begin) BETWEEN %(initial_date)s AND %(final_date)s) AND
(DATE(att.actual_end) BETWEEN %(initial_date)s AND %(final_date)s)
AND tt.users_id_tech != 0

GROUP BY t.id, tt.users_id_tech, date(att.actual_end)