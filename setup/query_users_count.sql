SELECT
    date(u1.date_creation) AS 'data',
    count(DISTINCT u1.id) AS 'novas_contas',
    count(DISTINCT u2.id) AS 'total_contas'
FROM glpi_users u1
INNER JOIN glpi_users u2 ON u1.id >= u2.id
WHERE
    u1.is_deleted = 0
    AND u2.is_deleted = 0
    AND u1.is_active = 1
    AND u2.is_active = 1
    AND u1.date_creation IS NOT NULL
    AND u2.date_creation IS NOT NULL
GROUP BY date(u1.date_creation);