select
         	bot_table.code
      	,	bot_table.tg as id_tg
      	,   CASE
				WHEN branch.branch_1c_id not in (6712, 6713, 6711, 4729, 4730, 4731, 4732, 193) then 'retail'
				WHEN branch.branch_1c_id in (6712, 6713, 6711) then 'oait'
				--###### Другие направления
				WHEN branch.branch_1c_id in (4729) then 'integration'
		       	WHEN branch.branch_1c_id in (4730) then 'hr'
		        WHEN branch.branch_1c_id in (4731) then 'logistics'
		       	WHEN branch.branch_1c_id in (4732) then 'marketing'
		       	--######
		        WHEN branch.branch_1c_id in (193) then 'boss'

		       	ELSE null
			END as session_type
      	,	branch.division as division_name
      	,	branch.rrs as rrs_name
	    ,	branch.branch_1c_id as branch_id
      	,	branch."name" as branch_name
      	, 	staff.mail as user_mail
      	, 	staff_name.avtor_name  as full_name
      	, 	staff_name.dolzhnost as post_name
      	, 	staff.staff_position_id as post_id
      	,	staff.is_deleted
      	,	null as employee_status
FROM
            inlet.staff_for_bot as bot_table
LEFT JOIN
			inlet.staff_dim_staff as staff
ON
            bot_table.code = staff.code
LEFT JOIN
  			division.branch_73 as branch
ON
	        bot_table.branch_1c  = branch.branch_1c_id
LEFT JOIN
	        division.staff_for_rp as staff_name
ON
	        bot_table.code  = staff_name.code_1c
where
			staff.is_deleted = false
    --       bot_table.tg is not null