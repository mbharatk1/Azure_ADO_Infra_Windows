USE [YourDatabaseName];
SELECT DP1.name AS RoleName,
       DP2.name AS MemberName
FROM sys.database_role_members AS DRM
JOIN sys.database_principals AS DP1 ON DRM.role_principal_id = DP1.principal_id
JOIN sys.database_principals AS DP2 ON DRM.member_principal_id = DP2.principal_id
WHERE DP1.name = 'db_owner';
