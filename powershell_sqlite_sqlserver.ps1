# -------------------------
# PowerShell Script: SQLite to SQL Server Migration (Using Login & Password)
# Prerequisites:
# 1. Install PowerShell SQL Server Module:
#    Run: Install-Module -Name SqlServer -Scope CurrentUser -Force
# 2. Install SQLite Database Engine:
#    Download: https://system.data.sqlite.org/index.html/doc/trunk/www/downloads.wiki
# 3. Ensure SQL Server is running and accessible remotely with proper permissions.
# 4. Run PowerShell as Administrator.
# -------------------------

# Define SQL Server connection parameters (with username/password authentication)
$server = "YourRemoteSQLServer"  # Replace with actual server name
$database = "YourDatabase"  # Replace with actual database name
$username = "YourUsername"  # Replace with actual SQL login
$password = "YourPassword"  # Replace with actual password
$connectionString = "Server=$server;Database=$database;UID=$username;PWD=$password;"

# Load SQL module
Import-Module SqlServer

# Define SQLite database paths
$sqliteDatabases = @("db1.sqlite", "db2.sqlite", "db3.sqlite")  # Replace with actual paths

# Iterate through each SQLite database
foreach ($dbFile in $sqliteDatabases) {
    if (-Not (Test-Path $dbFile)) {
        Write-Host "⚠️ Skipping: Database '$dbFile' not found!"
        continue
    }

    # Extract base name of SQLite DB
    $dbName = [System.IO.Path]::GetFileNameWithoutExtension($dbFile)

    # Open SQLite connection
    $sqliteConn = New-Object System.Data.SQLite.SQLiteConnection("Data Source=$dbFile;Version=3;")
    $sqliteConn.Open()

    # Get table names
    $sqliteCmd = $sqliteConn.CreateCommand()
    $sqliteCmd.CommandText = "SELECT name FROM sqlite_master WHERE type='table';"
    $tables = $sqliteCmd.ExecuteReader() | ForEach-Object { $_["name"] }

    # Process each table sequentially
    foreach ($tableName in $tables) {
        $newTableName = "${dbName}_${tableName}"  # Append DB name to table

        try {
            # Fetch data into PowerShell DataTable
            $sqliteCmd.CommandText = "SELECT * FROM $tableName"
            $adapter = New-Object System.Data.SQLite.SQLiteDataAdapter($sqliteCmd)
            $dataTable = New-Object System.Data.DataTable
            $adapter.Fill($dataTable)

            if ($dataTable.Rows.Count -eq 0) {
                Write-Host "⚠️ Skipping: Table '$tableName' in '$dbFile' has no data!"
                continue
            }

            # Generate table creation SQL for SQL Server
            $columnDefinitions = ($dataTable.Columns | ForEach-Object { "[$($_.ColumnName)] NVARCHAR(MAX)" }) -join ", "
            $createQuery = "IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = '$newTableName') CREATE TABLE $newTableName ($columnDefinitions)"
            Invoke-Sqlcmd -ConnectionString $connectionString -Query $createQuery

            # Bulk Insert Data into SQL Server
            foreach ($row in $dataTable.Rows) {
                $values = ($dataTable.Columns | ForEach-Object { "'$($row[$_.ColumnName].ToString())'" }) -join ", "
                $insertQuery = "INSERT INTO $newTableName ($($dataTable.Columns.ColumnName -join ', ')) VALUES ($values)"
                Invoke-Sqlcmd -ConnectionString $connectionString -Query $insertQuery
            }

            # Indexing for performance
            $indexQuery = "CREATE INDEX IX_$newTableName ON $newTableName ($($dataTable.Columns[0].ColumnName))"
            Invoke-Sqlcmd -ConnectionString $connectionString -Query $indexQuery

            Write-Host "✅ $newTableName migrated successfully!"
        }
        catch {
            Write-Host "❌ ERROR processing '$tableName' in '$dbFile': $_"
        }
    }

    $sqliteConn.Close()
}

Write-Host "🚀 All tables migrated sequentially!"
