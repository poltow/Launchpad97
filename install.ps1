# Copia LaunchpadLooper a los MIDI Remote Scripts de Live 9 y Live 10.
$source = Join-Path $PSScriptRoot 'LaunchpadLooper'
$targets = @(
    'C:\ProgramData\Ableton\Live 9 Suite\Resources\MIDI Remote Scripts\LaunchpadLooper',
    'C:\ProgramData\Ableton\Live 10 Suite\Resources\MIDI Remote Scripts\LaunchpadLooper',
    'C:\ProgramData\Ableton\Live 11 Suite\Resources\MIDI Remote Scripts\LaunchpadLooper',
    'C:\ProgramData\Ableton\Live 12 Suite\Resources\MIDI Remote Scripts\LaunchpadLooper',
    (Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'Ableton\User Library\Remote Scripts\LaunchpadLooper')
)
foreach ($target in $targets) {
    $parent = Split-Path $target -Parent
    if (-not (Test-Path $parent)) { Write-Host "No existe $parent, se omite"; continue }
    if (Test-Path $target) { Remove-Item -Recurse -Force $target }
    New-Item -ItemType Directory -Force $target | Out-Null
    Get-ChildItem $source -Filter '*.py' | Copy-Item -Destination $target
    Write-Host "Instalado en $target"
}
