$kernelDir = DirectoryName[System`$InputFileName]
$parentDir = ParentDirectory[$kernelDir]
Print[$kernelDir]
Print[$parentDir]
SetDirectory[$parentDir]
(* Get[ $parentDir <> "/environment" ] *)
(* Get[ $parentDir <> "/equation.M", Trace->True ] *)
Get[ $parentDir <> "/functions.M" , Trace -> True]
Get[ $parentDir <> "/inequality.M", Trace-> True ]
Get[ $parentDIr <> "/prover.M" , Trace -> True]
Get[ "rewrite.M" ]
Get[ "system_interface.M" ]
Get[ "types.M" ]
Get[ "user_interface.M" ]
