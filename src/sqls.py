'''
Created on Aug 1, 2012

@author: Mingze
'''

SQL_INSERT_COMMIT_INFO = '''
    INSERT INTO commits(author, 
                        transaction,
                        revision,
                        repos_token, 
                        comments,   
                        status_id,                       
                        cdate)
    VALUES(?, ?, ?, ?, ?, ?, ?);
    '''

SQL_INSERT_CHANGESET_INFO = '''
    INSERT INTO change_set(commit_id, 
                        type,
                        file_name,
                        file_url, 
                        diff_name, 
                        diff_path, 
                        cdate)
    VALUES(?, ?, ?, ?, ?, ?, ?);
    '''

SQL_INSERT_BUILD_INFO = '''
    INSERT INTO builds (job_id, 
                        commit_id,
                        cdate)
    VALUES(?, ?, ?);
    '''    

SQL_INSERT_ACTION_INFO= '''
    INSERT INTO actions (commit_id,
                         person,
                         action_id,
                         category_id,
                         comment,
                         cdate)
    VALUES(?, ?, ?, ?, ?, ?);
    '''

SQL_SET_BUILD_INVALID = '''
    UPDATE builds 
    SET isvalid = 0 
    WHERE job_id = ? and commit_id = ? ;
    '''
    
SQL_SET_COMMIT_STATUS = '''
    UPDATE commits 
    SET status_id = ? 
    WHERE id = ? ;
    '''     

SQL_SET_COMMIT_STATUS_BY_TXN = '''
    UPDATE commits 
    SET status_id = ? 
    WHERE transaction = ? and repos_token = ? ;
    '''    

SQL_UPDATE_BUILD_STATUS = '''
    UPDATE builds 
    SET build_num = ?, status_id = ?, phase_id = ?, url = ?   
    WHERE job_id = ? and commit_id = ? ;
    '''       
    
SQL_SELECT_JOB_ID = '''
    SELECT id
    FROM lu_job 
    WHERE name = ? ;
    '''   
    
SQL_SELECT_PHASE_ID = '''
    SELECT id
    FROM lu_phase
    WHERE name = ? ;
    '''  
    
SQL_SELECT_STATUS_ID = '''
    SELECT id
    FROM lu_status
    WHERE name = ? ;
    '''

SQL_SELECT_ACTION_ID = '''
    SELECT id
    FROM lu_action
    WHERE name = ? ;
    '''
    
SQL_SELECT_CATEGORY_ID = '''
    SELECT id
    FROM lu_category
    WHERE name = ? ;
    '''
    
SQL_SELECT_PERSON_ID = '''
    SELECT id
    FROM lu_person
    WHERE name = ? ;
    '''
        
SQL_SELECT_COMMIT_ID_BY_TRANSACTION = '''
    SELECT id
    FROM commits 
    WHERE transaction = ? ;
    '''   
    
SQL_SELECT_COMMIT_ID_BY_REVISION = '''
    SELECT id
    FROM commits 
    WHERE revision = ? ;
    '''
    
SQL_SELECT_CATEGORY = '''
    SELECT name
    FROM lu_category ;
    '''

SQL_SELECT_JOB_BY_COMMIT = '''
    SELECT lj.name, b.build_num
    FROM lu_job as lj inner join builds as b on lj.id = b.job_id
    WHERE commit_id = ? ;
    '''    



SQL_SELECT_DIFF_BY_COMMIT = '''
    SELECT file_name, diff_path
    FROM change_set
    WHERE commit_id = ? ;
    '''
    
SQL_SELECT_COMMIT_STATUS = '''
    SELECT status_id
    FROM commits
    WHERE transaction = ? and revision = ? ;
    '''
    
SQL_SELECT_UNPROCESSED_REQUEST_BY_AUTHOR = '''
    SELECT count(id)
    FROM commits 
    WHERE author = ? and status_id = 4 ;
    '''

SQL_SELECT_PROJECT_INFO = '''
    SELECT distinct lp.product, lv.version, lv.platform 
    FROM cibuild_info AS ci 
        JOIN action_result AS ar ON ci.CIBuildID = ar.CIBuildID 
        JOIN lu_job AS lj ON ci.jobID = lj.jobID 
        JOIN test_relation AS tr ON tr.testRelationID = ar.testRelationID 
        JOIN lu_product AS lp ON lp.productID = tr.productID
        JOIN lu_version AS lv ON lv.versionID = tr.versionID
    WHERE lj.jobName = ? and ci.CIBuildNumber = ? ;
    '''    

SQL_SELECT_DOWNSTREAM_JOBS = '''
    SELECT  lj1.jobName, ci.CIBuildNumber
    FROM cibuild_info AS ci 
        JOIN lu_job AS lj ON ci.upstreamJobID = lj.jobID 
                JOIN lu_job AS lj1 ON ci.jobID = lj1.jobID
    WHERE lj.jobName = ? and ci.upBuildNumber = ? ;   
    ''' 

SQL_SELECT_TEST_NUM = '''
    SELECT ci.testID
    FROM cibuild_info AS ci     
        JOIN lu_job AS lj ON ci.jobID = lj.jobID 
    WHERE lj.jobName = ? and ci.CIBuildNumber = ? ;
    '''
SQL_SELECT_TEST_RESULT = '''
    SELECT lj.jobName, ls.scenarioName, la.actionName AS action, 
           if(ar.resultStatusID = 1, "Success", "Failure") AS result, ar.executionTime
    FROM action_result AS ar 
                 JOIN cibuild_info AS ci ON ci.CIBuildID = ar.CIBuildID
                 JOIN test_relation AS tr ON ar.testRelationID = tr.testRelationID
                 JOIN lu_job AS lj ON lj.jobID = ci.jobID
                 JOIN lu_scenario AS ls ON ls.scenarioID = tr.scenarioID
                 JOIN lu_action AS la ON la.actionID = tr.actionID
    WHERE lj.jobName = ? AND ci.CIBuildNumber = ?
    '''
SQL_SELECT_TEST_FAILURES = '''
    SELECT count(ci.CIBuildID)
    FROM cibuild_info AS ci 
        JOIN action_result AS ar on ci.CIBuildID = ar.CIBuildID
        JOIN lu_job AS lj ON ci.jobID = lj.jobID 
    WHERE lj.jobName = ? and ci.CIBuildNumber = ? and ci.testID = ? and ar.resultStatusID = 2; 
    '''
SQL_SELECT_TEST_RESULT_ID = '''
    SELECT ar.resultStatusID 
    FROM cibuild_info AS ci 
        JOIN action_result AS ar on ci.CIBuildID = ar.CIBuildID
        JOIN lu_job AS lj ON ci.jobID = lj.jobID 
    WHERE lj.jobName = ? and ci.CIBuildNumber = ? and ci.testID = ?; 
    '''
    
SQL_CHECK_IS_ANY_FAILURES = '''
    SELECT job_id, build_num, commit_id, url 
    FROM builds
    WHERE commit_id = ? 
          and status_id in (2,8) 
          and phase_id = 3 
          and (SELECT count(job_id) 
               FROM builds 
               WHERE commit_id = ?) = 
              (SELECT count(job_id) 
               FROM builds
               WHERE commit_id = ?
                     and phase_id = 3) ;
    '''
    
SQL_COUNT_FILES_BY_COMMIT = '''
    SELECT COUNT(id)
    FROM change_set
    WHERE commit_id = ?
    '''
    