SELECT t.id, u2.name as técnico_chamado, u.name as técnico_tarefas, sum(att.actual_actiontime) as tempo_plugin, sum(tt.actiontime) as tempo_glpi
FROM glpi_tickets t

LEFT JOIN glpi_tickettasks tt
ON t.id = tt.tickets_id

LEFT JOIN glpi_tickets_users tu
ON t.id = tu.tickets_id AND tu.type = 2

LEFT JOIN glpi_users u2
ON u2.id = tu.users_id

LEFT JOIN glpi_users u
ON u.id = tt.users_id_tech

LEFT JOIN glpi_plugin_actualtime_tasks att
ON tt.id = att.tasks_id

WHERE (DATE(t.date) BETWEEN %s AND %s) AND
t.status = 6 AND
(att.actual_actiontime IS NOT NULL OR tt.actiontime != 0) AND
tt.users_id_tech != 0

GROUP BY t.id, tt.users_id_tech