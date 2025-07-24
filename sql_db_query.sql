USE [YourDatabaseName];
SELECT DP1.name AS RoleName,
       DP2.name AS MemberName
FROM sys.database_role_members AS DRM
JOIN sys.database_principals AS DP1 ON DRM.role_principal_id = DP1.principal_id
JOIN sys.database_principals AS DP2 ON DRM.member_principal_id = DP2.principal_id
WHERE DP1.name = 'db_owner';



USE YourDatabaseName;  -- Replace with your actual database name

SELECT 
    dp.name AS MemberName,
    dp.type_desc AS MemberType
FROM sys.database_principals dp
WHERE dp.principal_id IN (
    SELECT member_principal_id
    FROM sys.database_role_members
    WHERE role_principal_id = USER_ID('db_owner')
);
