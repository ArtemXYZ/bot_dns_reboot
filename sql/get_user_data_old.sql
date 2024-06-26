--# separation _by_session 
--# 6712(Отдел Аналитики див. СВ) 6713(Отдел Форматы и Распределение див. СВ), 4723(Отдел Аналитики и Товарооборота див. СВ) 6711(Отдел Товарооборота див. СВ)	6712.0
select 
         	bot_table.code 
      	,	bot_table.tg as id_tg
      	,   CASE
				WHEN branch.branch_1c_id not in (6712, 6713, 6711, 4729, 4730, 4731, 4732, 193) then 'retail'  	--# Все остальные подразделения (филиалы)				
				WHEN branch.branch_1c_id in (6712, 6713, 6711) then 'oait'				--# Отдел Аналитики и Товарооборота див. СВ
				--###### Другие направления
				WHEN branch.branch_1c_id in (4729) then 'integration' 					--# Развитие Розничных процессов див.СВ (интеграции) +		       	
		       	WHEN branch.branch_1c_id in (4730) then 'hr'  							--# HR служба дивизиона СВ +
		        WHEN branch.branch_1c_id in (4731) then 'logistics'  						--# Логистическая служба дивизиона СВ +
		       	WHEN branch.branch_1c_id in (4732) then 'marketing'						--# Рекламная служба дивизиона СВ +
		       	--######
		        WHEN branch.branch_1c_id in (193) then 'boss'  							--# Адм. дивизиона Средне-Волжский  +
		        --##########
		       -- WHEN bot_table.code in 'IU13763'  then 'admin'  						--# ! озможно сделать на SQL - реализация в пайтон после создания таблицы. По конкретому id (code) первичный админ - Познышев АА. (разработчик) 
		       	ELSE null
			END as session_type	
      	,	branch.division as division_name
      	,	branch.rrs as rrs_name 
	    ,	branch.branch_1c_id as branch_id 
      	,	branch."name" as branch_name
      	, 	staff.mail as user_mail
      	, 	staff_name.avtor_name  as full_name       	
      	, 	staff_name.dolzhnost as post_name 
      	, 	staff.staff_position_id as post_id  -- in (939, 881 1041 43 62, 95, 43)
      	,	staff.is_deleted  				 -- + флаг уволен ли сотрудник или нет.   
      	,	null as employee_status 
      	--------
      	,   CASE
				WHEN holiday.id in (17, 20, 22, 23, 24, 43, 44, 40, 49) then True
      			ELSE False      		
      		END as holiday_status      	
      	,	false as admin_status
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
LEFT JOIN		        
	        inlet.staff_dim_eventtype as holiday
ON 
			staff.staff_event_type_id = holiday.id 
	        ------	        
where  
			staff.is_deleted = false
and         bot_table.tg is not null  
            
-- 939(Младший специалист по аналитике),
 --881(Аналитик данных 1 категории), 1041(Аналитик данных 2 категории),
 --43(Ст. специалист коммерческого отдела), 62(Специалист коммерческого отдела)