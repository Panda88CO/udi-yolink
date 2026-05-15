$nlsPath="profile/nls/en_us.txt"
$ndPath="profile/nodedef/nodedefs.xml"
$nls=Get-Content $nlsPath
$nd=[xml](Get-Content $ndPath -Raw)
$nodeIds = New-Object "System.Collections.Generic.HashSet[string]"
$stPairs = New-Object "System.Collections.Generic.HashSet[string]"
$cmdPairs = New-Object "System.Collections.Generic.HashSet[string]"
$paramIds = New-Object "System.Collections.Generic.HashSet[string]"
foreach($node in $nd.nodeDefs.nodeDef){
  if($node.id){ [void]$nodeIds.Add([string]$node.id) }
  $nlsId=[string]$node.nls
  if($node.sts){ foreach($st in $node.sts.st){ if($st.id){ [void]$stPairs.Add("$nlsId|$($st.id)") } } }
  if($node.cmds){
    foreach($grpName in @("accepts","sends")){
      $grp=$node.cmds.$grpName
      if($grp){
        foreach($cmd in $grp.cmd){
          if($cmd.id){ [void]$cmdPairs.Add("$nlsId|$($cmd.id)") }
          if($cmd.p){ foreach($p in $cmd.p){ if($p.id -and [string]$p.id -ne ""){ [void]$paramIds.Add([string]$p.id) } } }
        }
      }
    }
  }
}
$orphans=@()
for($i=0;$i -lt $nls.Count;$i++){
  $line=$nls[$i].Trim()
  if($line -eq "" -or $line.StartsWith("#")){ continue }
  if($line -match "^ND-([^-]+)-(NAME|ICON)="){
    if(-not $nodeIds.Contains($Matches[1])){ $orphans += [pscustomobject]@{Line=$i+1;Type="ND";Entry=$line} }
    continue
  }
  if($line -match "^ST-([^-]+)-([^-]+)-NAME="){
    $pair="$($Matches[1])|$($Matches[2])"
    if(-not $stPairs.Contains($pair)){ $orphans += [pscustomobject]@{Line=$i+1;Type="ST";Entry=$line} }
    continue
  }
  if($line -match "^CMD-([^-]+)-([^-]+)-NAME="){
    $pair="$($Matches[1])|$($Matches[2])"
    if(-not $cmdPairs.Contains($pair)){ $orphans += [pscustomobject]@{Line=$i+1;Type="CMD";Entry=$line} }
    continue
  }
  if($line -match "^CMDP-([^-]+)-NAME="){
    if(-not $paramIds.Contains($Matches[1])){ $orphans += [pscustomobject]@{Line=$i+1;Type="CMDP";Entry=$line} }
    continue
  }
}
"Total orphans: $($orphans.Count)"
$orphans | Sort-Object Type,Line | Format-Table -AutoSize
$orphans.Entry
