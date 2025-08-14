param(
  [Parameter(Position=0, Mandatory=$true)]
  [string]$Slash,
  [Parameter(ValueFromRemainingArguments=$true)]
  [string[]]$Rest
)

function Show-Usage {
  Write-Host "Usage: cx /<nom-fichier-sans-ext> [args...] | cx --list"
  exit 1
}

function List-All {
  $roots = @(".codex/commands", "$HOME/.codex/commands")
  $names = @()
  foreach ($r in $roots) {
    if (Test-Path $r) {
      $names += Get-ChildItem -Path $r -Recurse -File -Include *.md,*.txt,*.prompt |
        ForEach-Object { [System.IO.Path]::GetFileNameWithoutExtension($_.Name) }
    }
  }
  $names | Sort-Object -Unique
}

if ($Slash -eq "--list") { List-All; exit 0 }
if (-not $Slash.StartsWith("/")) { Show-Usage }

$cmd  = $Slash.Substring(1)
$args = ($Rest -join " ")

$roots = @(".codex/commands", "$HOME/.codex/commands")
$matches = @()

foreach ($r in $roots) {
  if (Test-Path $r) {
    $matches += Get-ChildItem -Path $r -Recurse -File -Include "$cmd.md","$cmd.txt","$cmd.prompt" |
      Select-Object -ExpandProperty FullName
  }
}

if ($matches.Count -eq 0) {
  Write-Error "❌ Commande '$cmd' introuvable dans .codex/commands/** ou ~/.codex/commands/**"
  exit 1
}

if ($matches.Count -gt 1) {
  Write-Error "❌ Plusieurs correspondances pour '$cmd' :"
  $matches | ForEach-Object { Write-Host " - $_" }
  exit 1
}

$file = $matches[0]
$prompt = Get-Content -Raw -Path $file
$prompt = $prompt -replace '\$ARGUMENTS', [Regex]::Escape($args)
$prompt = $prompt -replace '\$CWD', [Regex]::Escape((Get-Location).Path)

& codex --ask-for-approval on-request $prompt
