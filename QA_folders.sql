The following SQL query returns the workspace name, folder name(s), document description(s), document number(s), default security, userid(s), and user access rights for a specified workspace.

Replace '%Name or Partial Name of workspace%' with the complete name or part of the name of the workspace for which you want to run the document report, and enclose the workspace name in single quotation marks and percent symbols, e.g. ‘%iManage Example Workspace%’.

SELECT prjs2.PRJ_NAME AS Workspace, prjs.PRJ_NAME AS Folder, dm.DOCNAME AS "Document Description", dm.DOCNUM AS "Document Number", CASE DM.DEFAULT_SECURITY WHEN 'V' THEN 'View' WHEN 'X' THEN 'Private' WHEN 'P' THEN 'Public' END AS "Default Security", du.USERID, CASE da.ACCESS_RIGHT WHEN 1 THEN 'Read' WHEN 2 THEN 'Read/Write' WHEN 3 THEN 'Full Access' END AS "Access Rights"
FROM MHGROUP.DOCMASTER dm
JOIN MHGROUP.PROJECT_ITEMS prji ON dm.DOCNUM=prji.ITEM_ID
JOIN MHGROUP.PROJECTS prjs ON prji.PRJ_ID = prjs.PRJ_ID
JOIN MHGROUP.PROJECTS prjs2 ON prjs.TREE_ID = prjs2.PRJ_ID
JOIN MHGROUP.DOC_ACCESS da ON da.DOCNUM = dm.DOCNUM AND da.DOCVER = dm.VERSION
JOIN MHGROUP.DOCUSERS du ON da.USER_GP_ID = du.USERNUM
WHERE prjs2.PRJ_NAME LIKE '%Name or Partial Name of workspace%'
