$FolderOne   = "MyFirstFolder"
$FolderTwo   = "MySecondFolder"
$FolderThree = "MyThirdFolder"
$FileName    = "my_script"

# Create the three main folders

New-Item -ItemType Directory -Path ".\$FolderOne"
Write-Output "Folder with the name $FolderOne has been created"

New-Item -ItemType Directory -Path ".\$FolderTwo" 
Write-Output "Folder with the name $FolderTwo has been created"

New-Item -ItemType Directory -Path ".\$FolderThree" 
Write-Output "Folder with the name $FolderThree has been created"

$FolderThreeOne   = "FirstFolderinFolderThree"
$FolderThreeTwo   = "MySecondFolderinFolderThree"
$FolderThreeThree = "MyThirdFolderinFolderThree"

# Navigate into FolderThree and create three new folders
New-Item -ItemType Directory -Path ".\$FolderThree\$FolderThreeOne"
Write-Output (
    "Folder with the name $FolderThreeOne has been " +
    "created inside $FolderThree"
)

New-Item -ItemType Directory -Path ".\$FolderThree\$FolderThreeTwo"
Write-Output (
    "Folder with the name $FolderThreeTwo has been " +
    "created inside $FolderThree"
)

New-Item -ItemType Directory -Path ".\$FolderThree\$FolderThreeThree"
Write-Output (
    "Folder with the name $FolderThreeThree has been " +
    "created inside $FolderThree"
)

# Remove FolderOne and FolderTwo
Remove-Item -Path ".\$FolderOne" -Recurse
Write-Output "$FolderOne has been removed"

Remove-Item -Path ".\$FolderTwo" -Recurse
Write-Output "$FolderTwo has been removed"

