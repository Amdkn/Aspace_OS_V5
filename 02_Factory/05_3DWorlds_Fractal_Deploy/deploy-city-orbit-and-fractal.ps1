# 02_Factory/deploy-city-orbit-and-fractal.ps1
param(
  [ValidateSet("0L", "2L", "4L", "8L", "16L", "20L")]
  [string]$TargetLayer = "8L",
  [switch]$SpinOutCityOffice = $false
)
& "$PSScriptRoot/mount-fractal.ps1" -TargetLayer $TargetLayer -SpinOutCityOffice:$SpinOutCityOffice
