param([string]$In, [string]$Out)
$ErrorActionPreference = 'Stop'
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
try {
    $d = $w.Documents.Open($In, $false, $true)
    $d.Repaginate()
    $pages = $d.ComputeStatistics(2)
    $d.ExportAsFixedFormat($Out, 17)
    Write-Output "pages=$pages"
    $d.Close($false)
} finally {
    $w.Quit()
}
