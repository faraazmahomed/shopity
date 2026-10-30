# FIX: Dynamically target the directory where this script runs from
$BasePath = $PSScriptRoot
$folder   = "if_folder"

# FIX: Properly resolve the target path to look for 'new_folder'
$NewFolderPath = Join-Path -Path $BasePath -ChildPath "new_folder"
$IfFolderPath  = Join-Path -Path $BasePath -ChildPath $folder

# Check if new_folder exists to create if_folder 
if (Test-Path -Path $NewFolderPath) {
    Write-Output "The folder named 'new_folder' already exists."
    
    # Create the if_folder since new_folder was found
    if (-not (Test-Path -Path $IfFolderPath)) {
        New-Item -Path $IfFolderPath -ItemType Directory
        Write-Output (
            "Folder with the name $folder has " +
            "been created successfully."
        )
    } else {
        Write-Output "The folder named $folder already exists."
    }
} 
else {
    Write-Output (
        "The folder named 'new_folder' does not " +
        "exist, so $folder will not be created."
    )
}

# Define cross-platform paths for the second check
$HyperionPath    = Join-Path -Path $BasePath -ChildPath "hyperionDev"
$NewProjectsPath = Join-Path -Path $BasePath -ChildPath "new-projects"

# Write an if-else statement to check whether if_folder exists
if (Test-Path -Path $IfFolderPath) {
    Write-Output (
        " 'if_folder' exists! Attempting to " +
        "create 'hyperionDev'..."
    )
    
    # Check if hyperionDev exists before creating it
    if (-not (Test-Path -Path $HyperionPath)) {
        New-Item -Path $HyperionPath -ItemType Directory
        Write-Output "Folder 'hyperionDev' has been created."
    } else {
        Write-Output "Folder 'hyperionDev' already exists."
    }
} 
else {
    Write-Output (
        " 'if_folder' does not exist! Attempting " +
        "to create 'new-projects'..."
    )
    
    # Check if new-projects already exists before creating it
    if (-not (Test-Path -Path $NewProjectsPath)) {
        New-Item -Path $NewProjectsPath -ItemType Directory
        Write-Output "Folder 'new-projects' has been created."
    } else {
        Write-Output "Folder 'new-projects' already exists."
    }
}