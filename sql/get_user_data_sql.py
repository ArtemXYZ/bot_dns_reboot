"""Модуль содержи
Порядок колонок в запросе (очередность в selekt) имеет значение!!
иначе сломается построение данных!
 """
user_data_sql_text ="""
select         
         	bot_table.tg as id_tg         	
        ,	user_data_bot.code
        , 	user_data_bot.session_type	
        , 	user_data_bot.full_name 
        , 	user_data_bot.post_id
        , 	user_data_bot.post_name
        , 	user_data_bot.branch_id
        , 	user_data_bot.branch_name
        , 	user_data_bot.rrs_name
        , 	user_data_bot.division_name
        , 	user_data_bot.user_mail
        , 	user_data_bot.is_deleted        
      	,	False as employee_status
      	,	False as admin_status
FROM
            inlet.staff_for_bot as bot_table
LEFT JOIN            
            inlet.user_data_bot as user_data_bot
ON
            bot_table.code = user_data_bot.code 
where
			user_data_bot.is_deleted = false 
			and bot_table.tg is not null		
"""


user_data_sql_text_old ="""
select 
         	bot_table.tg as id_tg  
      	,	bot_table.code
      	,   CASE
				WHEN branch.branch_1c_id not in (6712, 6713, 6711, 4729, 4730, 4731, 4732, 193) then 'retail'  			
				WHEN branch.branch_1c_id in (6712, 6713, 6711) then 'oait'				
				WHEN branch.branch_1c_id in (4729) then 'integration' 							       	
		       	WHEN branch.branch_1c_id in (4730) then 'hr'  							
		        WHEN branch.branch_1c_id in (4731) then 'logistics'  					
		       	WHEN branch.branch_1c_id in (4732) then 'marketing'
		        WHEN branch.branch_1c_id in (193) then 'boss' 		       					
		       	ELSE null
			END as session_type	
		, 	staff_name.avtor_name  as full_name 	
		, 	staff.staff_position_id as post_id 
		, 	staff_name.dolzhnost as post_name
		,	branch.branch_1c_id as branch_id 	
		,	branch."name" as branch_name
		,	branch.rrs as rrs_name 
      	,	branch.division as division_name
      	, 	staff.mail as user_mail
	    ,	staff.is_deleted  				  
      	,	false as employee_status 
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
where  
			staff.is_deleted = false
and         bot_table.tg is not null		
"""