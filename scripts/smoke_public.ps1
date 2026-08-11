param(
    [string]$WebUrl = "https://furniture-zk.zeabur.app",
    [string]$ApiUrl = "https://furniture-api-zk.zeabur.app"
)

$ErrorActionPreference = "Stop"

function Assert-Status {
    param(
        [string]$Name,
        [string]$Uri,
        [int[]]$Expected
    )

    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri $Uri -MaximumRedirection 5 -TimeoutSec 30
        $status = [int]$response.StatusCode
    }
    catch {
        if ($_.Exception.Response) {
            $status = [int]$_.Exception.Response.StatusCode
        }
        else {
            throw
        }
    }

    if ($status -notin $Expected) {
        throw "$Name returned HTTP $status; expected $($Expected -join ', ')"
    }
    Write-Host "[OK] $Name -> HTTP $status"
}

Assert-Status -Name "Web" -Uri "$($WebUrl.TrimEnd('/'))/" -Expected @(200)
Assert-Status -Name "API health" -Uri "$($ApiUrl.TrimEnd('/'))/api/health/" -Expected @(200)
Assert-Status -Name "Agent auth boundary" -Uri "$($ApiUrl.TrimEnd('/'))/api/agent/capabilities/" -Expected @(401, 403)

Write-Host "Public smoke checks passed."
