<#  demo_mpqr.ps1
    Demostración/Prueba unitaria rápida del objeto COM MPQR.Server
#>

param(
    [string]$Token    = "TEST-6315433665621565-042910-cf49248dbba65897a7e6dd30f2f93742-63189587",
    [string]$PosId    = "PBTEST",
    [string]$PosName  = "Caja PB",
    [string]$Title    = "Artículo X",
    [decimal]$Amount  = 150,
    [string]$SaveDir  = "$env:TEMP"     # carpeta donde guardar PNG
)

function Show-Json { param($o) $o | ConvertTo-Json -Depth 5 }

Write-Host "== 1) Instanciando COM =="
try   { $srv = New-Object -ComObject MPQR.Server }
catch { throw "❌ No se pudo crear MPQR.Server. ¿Registrado?" }

Write-Host "== 2) SetAccessToken =="
$srv.SetAccessToken($Token) | Out-Null
Write-Host "   OK"

# --------------------------------------------------------------------
Write-Host "== 3) CreatePOS (id=$PosId) =="
$posJson = $srv.CreatePOS($PosId, $PosName) | ConvertFrom-Json
Show-Json $posJson

Write-Host "== 4) GetPOS =="
$pos = $srv.GetPOS($PosId) | ConvertFrom-Json
Show-Json $pos

# --------------------------------------------------------------------
Write-Host "== 5) CreateQR =="
$qr = $srv.CreateQR($PosId, $Title, $Amount) | ConvertFrom-Json
Show-Json $qr
$instore = $qr.in_store_order_id

Write-Host "== 6) PNG guardado =="
$png = $srv.SaveLastPngToFile($SaveDir)
Write-Host "   → $png  ($(Get-Item $png).Length bytes)"
Start-Process $png    # abre visor por defecto

Write-Host "== 7) LastQrPng length = ", ($srv.LastQrPng()).Length
Write-Host "== 8) LastOrderId     = ", $srv.LastOrderId()

# --------------------------------------------------------------------
$orderId   = $qr.order_id
$instoreId = $qr.in_store_order_id

Start-Sleep 15         # pequeña pausa para que la orden aparezca
Write-Host "== 9) GetQRStatus =="
$status = $srv.GetQRStatus($PosId, $orderId) | ConvertFrom-Json
Show-Json $status


Write-Host "== 10) CancelQR =="
$cancel = $srv.CancelQR($instore) | ConvertFrom-Json
Show-Json $cancel

Write-Host "`n✅  DEMO FINALIZADA"
