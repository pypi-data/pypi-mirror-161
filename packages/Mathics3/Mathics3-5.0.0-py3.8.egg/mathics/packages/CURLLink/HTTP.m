
(* Wolfram CURLLink Package *)

BeginPackage["CURLLink`HTTP`",{"CURLLink`","OAuthSigning`"}]
System`CookieFunction
System`Cookies
URLFetch::usage = "URLFetch[url, elements] return elements from url, for any accessible URL.";
URLSave::usage = "URLSave[url, file, elements] return elements from url for any accessible URL, and store the content in file. ";
URLFetchAsynchronous::usage = "URLFetchAsynchronous[url, eventFunction] asynchronously connect to a URL";
URLSaveAsynchronous::usage = "URLSaveAsynchronous[url, file, eventFunction] asynchronously connect to a URL, and store the content in a file.";
$HTTPCookies::usage = "Returns the list of globally shared cookies."



SetAttributes[URLFetch, {ReadProtected}];
SetAttributes[URLSave, {ReadProtected}];
SetAttributes[URLFetchAsynchronous, {ReadProtected}];
SetAttributes[URLSaveAsynchronous, {ReadProtected}];
Needs["PacletManager`"]


Begin["`Private`"] (* Begin Private Context *) 

If[$VersionNumber <  9,
	Message[CURLLink::enable,  "CURLLink"]
]


Needs["CURLLink`Cookies`"]
(****************************************************************************)
$CACERT = FileNameJoin[{DirectoryName[System`Private`$InputFileName], "SSL", "cacert.pem"}];
$MessageHead = HTTP;

(****************************************************************************)
(* Default options for URLFetch *)
$StandardOptions = {	
	Method -> "GET", 
	"Parameters" -> {},
	"Body" -> "", 
	"MultipartElements" -> {},
	"VerifyPeer" -> True, 
	"Username" -> "", 
	"Password" -> "", 
	"UserAgent" -> Automatic, 
	System`CookieFunction->Automatic,
	"Cookies"->Automatic, 
	"StoreCookies" -> True,
	"Headers" -> {},
	"CredentialsProvider"->Automatic,
	"ConnectTimeout"->0,
	"ReadTimeout"->0,
	"DisplayProxyDialog" -> True,
	"OAuthAuthentication" -> None,
	"FollowRedirects" -> True,
	Authentication->Automatic
}
$returnTypes={"Content","ContentData","Cookies","Headers","StatusCode","Stream","HeadersReceived"}
$storageForms={"Return","Proxies","FTP","URL","BaseURL","OPTIONS"}
$HTTPStorageForms={"Stream"}
$DeprecatedOptions = {
	"BodyData" -> "Body",
	"MultipartData" -> "MultipartElements"
}
Options[URLFetch] = $StandardOptions
Options[setStandardOptions] = $StandardOptions

(* Deprecated options fix *)

(* Uncomment those lines and the message inside deprecatedOptionFix to send a deprecation warning. *)
(* URLFetch::depropt             = "The option \"``\" is deprecated, please use \"``\""; *)
(* URLSave::depropt              = URLFetch::depropt; *)
(* URLFetchAsynchronous::depropt = URLFetch::depropt; *)
(* URLSaveAsynchronous::depropt  = URLFetch::depropt; *)

deprecatedOptionFix[sym_, options___] := Sequence @@ Replace[
	{options}, 
	head_[key:Alternatives @@ Keys[$DeprecatedOptions], value_] :> (
		(* uncomment the next line to send a deprecation warning *)
		(* Message[sym::depropt, key, Lookup[$DeprecatedOptions, key]]; *)
		head[Lookup[$DeprecatedOptions, key], value]
	),
	{1}
]
(*Utility functions*)

isURL[url_,head_:URLFetch]:=StringQ[getURL[url,head]];
getURL[url_String,head_:URLFetch]:=url
getURL[URL[url_],head_:URLFetch]:=getURL[url,head]
getURL[IPAddress[url_],head_:URLFetch]:=getURL[url,head]
getURL[exp_,head_:URLFetch]:=(Message[head::invurl, exp];$Failed)

isFile[exp_,head_:URLSave]:=StringQ[getFile[exp,head]];
getFile[file_String,head_:URLSave]:=file
getFile[File[file_],head_:URLSave]:=getFile[file,head]
getFile[exp_,head_:URLSave]:=(Message[head::invfile, exp];$Failed)

unsetCURLHandle[handles_List]:=Map[unsetCURLHandle[#]&,handles]
unsetCURLHandle[handle_CURLLink`CURLHandle]:=Map[Quiet[Unset[handle[#]], Unset::norep]&,$storageForms]
unsetHTTPData[handle_CURLLink`CURLHandle]:=Map[Quiet[Unset[HTTPData[handle, #]], Unset::norep]&,$HTTPStorageForms]

deprecatedOptionQ[options___] := Cases[Keys @ {options}, Alternatives @@ Keys[$DeprecatedOptions]] =!= {}

URLFetch[urlExp_,opts:OptionsPattern[]]/;InitializeQ[]:=(URLFetch[urlExp,"Content",opts])	

URLFetch[urlExp_, res:(_String|_List|All), options___?OptionQ] /; deprecatedOptionQ[options] := 
	URLFetch[urlExp, res, deprecatedOptionFix[URLFetch, options]] 

allowCredintalDialog[opts:OptionsPattern[]] := (
	"DisplayProxyDialog" /. Flatten[{opts}] /. "DisplayProxyDialog"->True
);
URLFetch[urlExp_List, res:(_String|_List|All), opts:OptionsPattern[]] /; InitializeQ[] :=
	Module[{usefulConnectAndstatusCodes,connectCodes,handlesAndElements,noProxiesSpecified,isBlockingQ,urlsWith401,easyHandlesWith401,codes,multihandle,streamIsRequested,contentOrContentDataIsRequested,requestedElements=Flatten@{res},urls,easyhandles, output, error, stdOpts, elements, wellFormedURL,isblocking=True},
		$LastKnownCookies=CURLLink`Cookies`GetKnownCookies[];
		
		urls=Map[getURL[#]&,Flatten[{urlExp}]];
		
		setMessageHead[URLFetch];
		
		streamIsRequested=MemberQ[requestedElements,"Stream"];
		
		isBlockingQ=!streamIsRequested;
		
		contentOrContentDataIsRequested=MemberQ[requestedElements,"Content"|"ContentData"];
		
		(*If we asked for a Stream then CURLPerform[] will be non-blocking*)
		If[streamIsRequested,isblocking=False];

		If[streamIsRequested && contentOrContentDataIsRequested,Throw[$Failed,CURLLink`Utilities`Exception]];
		
		If[res===All,requestedElements=Complement[$URLFetchElements,{"Stream"}]];

		stdOpts = Flatten[{opts, FilterRules[Options[URLFetch], Except[{opts}]]}];
	
		easyhandles = commonInit[urls, URLFetch, stdOpts];
		
		setOutput[easyhandles, "String"];
		
		multihandle = CURLLink`CURLMultiHandleInit[];
		
		multihandle = CURLLink`CURLLMultiHandleAdd[multihandle,easyhandles];
		
		noProxiesSpecified=AllTrue[Map[#["Proxies"] === {}&,easyhandles],TrueQ];
		
		elements = $URLFetchElements;

		If[noProxiesSpecified,
			CURLLink`CURLMultiPerform[multihandle,"IsBlocking"->isBlockingQ];
		
			codes=CURLLink`CURLStatusCodes[easyhandles];
			
			(*if Stream is requesed, block until all the status codes, associated with easy handles, are received*)
			While[MemberQ[Values[codes],0] && !isBlockingQ,CURLLink`CURLMultiPerform[multihandle,"IsBlocking"->isBlockingQ];codes=CURLLink`CURLStatusCodes[easyhandles]];
			
			easyHandlesWith401=Cases[codes,(easyhandle_->401)->easyhandle];
			
			If[easyHandlesWith401=!={}&&!isBlockingQ,CURLLink`CURLLMultiHandleRemove[multihandle,easyHandlesWith401]];
			
			urlsWith401=Map[{#,#["URL"]}&,easyHandlesWith401];
			
			If[easyHandlesWith401=!={} && allowCredintalDialog[opts],
				If[AllTrue[Map[credWrapper[#[[1]], #[[2]], OptionValue["CredentialsProvider"]]&,urlsWith401],TrueQ],
							multihandle = CURLLink`CURLLMultiHandleAdd[multihandle,easyHandlesWith401];
							CURLLink`CURLMultiPerform[multihandle];]
			];
			
			Map[Set[#["Return"],0]&,easyhandles];
				
			(*else*),
			
			
			Map[CURLLink`CURLOption[#, "CURLOPT_PROXY", #["Proxies"][[1]]]&,easyhandles];
			
			CURLLink`CURLMultiPerform[multihandle,"IsBlocking"->isBlockingQ];
			
			codes=CURLLink`CURLStatusCodes[easyhandles];
			
			(*if Stream is requesed, block until all the status codes, associated with easy handles, are received*)
			While[!isBlockingQ,
				usefulConnectAndstatusCodes=Cases[codes~Join~connectCodes,(handle_->cd_/;cd>0)->handle->cd];
				If[Complement[Keys[usefulConnectAndstatusCodes],easyhandles]==={},CURLLink`CURLLMultiHandleRemove[multihandle,easyhandles];Break[]];
				CURLLink`CURLMultiPerform[multihandle,"IsBlocking"->isBlockingQ];
				codes=CURLLink`CURLStatusCodes[easyhandles];
				connectCodes=CURLLink`CURLHTTPConnectCodes[easyhandles]
			];
			
			If[AllTrue[Map[proxyCredentials[#, #["URL"]]&,easyhandles],TrueQ],
							
							CURLLink`CURLLMultiHandleAdd[multihandle,easyhandles];
							CURLLink`CURLMultiPerform[multihandle,"IsBlocking"->isblocking];
							codes=CURLLink`CURLStatusCodes[easyhandles];
							connectCodes=CURLLink`CURLHTTPConnectCodes[easyhandles];
						];

			TimeConstrained[
				While[!isBlockingQ,
					CURLLink`CURLMultiPerform[multihandle,"IsBlocking"->isBlockingQ];
					codes=CURLLink`CURLStatusCodes[easyhandles];
					connectCodes=CURLLink`CURLHTTPConnectCodes[easyhandles];
					If[!AllTrue[Values[codes~Join~connectCodes],#==0&],Break[];]
				     ];,
				    3];			

			codes=CURLLink`CURLStatusCodes[easyhandles];
			
			(*if Stream is requesed, block until all the status codes, associated with easy handles, are received*)
			While[MemberQ[Values[codes],0] && !isBlockingQ,CURLLink`CURLMultiPerform[multihandle,"IsBlocking"->isBlockingQ];codes=CURLLink`CURLStatusCodes[easyhandles]];

			easyHandlesWith401=Cases[codes,(easyhandle_->401)->easyhandle];
			
			If[easyHandlesWith401=!={}&&!isBlockingQ,CURLLink`CURLLMultiHandleRemove[multihandle,easyHandlesWith401]];
			
			urlsWith401=Map[{#,#["URL"]}&,easyHandlesWith401];
			
			If[easyHandlesWith401=!={} && allowCredintalDialog[opts],
				If[AllTrue[Map[credWrapper[#[[1]], #[[2]], OptionValue["CredentialsProvider"]]&,urlsWith401],TrueQ],
							multihandle = CURLLink`CURLLMultiHandleAdd[multihandle,easyHandlesWith401];
							CURLLink`CURLMultiPerform[multihandle];]
			];
			
			Map[Set[#["Return"],0]&,easyhandles];
			
			];
			
			If[easyHandlesWith401=!={}, 
				wellFormedURL = If[StringMatchQ[urls, {"http://*", "https://*, ftp://*, ftps://*"}], 
					URIJoin[Flatten@{URISplit[url]}]
				(*else*), 
					URIJoin[Flatten@{URISplit["http://" <> url]}]
				];				
				
				sessionStore[wellFormedURL] := False
			];
			sessionStore[wellFormedURL] := False;
			If[CURLLink`CURLStatusCode[handle] === 401||CURLLink`CURLStatusCode[handle] === 407||CURLLink`CURLHTTPConnectCode[handle] === 407,
				$proxyCache = False;
			];
			$proxyCache=False;
			If[!MemberQ[Map[#["Return"]&,easyhandles], 0],
				CURLLink`CURLHandleUnload[easyhandles];
				Message[URLFetch::invhttp, CURLLink`CURLError[handle["Return"]]];
				Return[$Failed]
			];
		
			If[(OptionValue[System`CookieFunction]=!=None)&&OptionValue["StoreCookies"] && (OptionValue["Cookies"] =!= Automatic),
				storeCookies[HTTPData[easyhandles, "Cookies"]]
			]; 
		
			handlesAndElements = Map[{#,If[#["FTP"]===True, $FTPFetchElements, $URLFetchElements]}&,easyhandles];
			(* Perhaps the user just wants to know the available output types. *)
			If[res === "Elements",
					Return[handlesAndElements[[;;,2]]]
			];
		
			output = parseElements[handlesAndElements, requestedElements];
			(*
			if non blocking,i.e stream element is 
			requested then unload happens in c-code
			when Close[InputStream[..]] is called
			*)
			If[isblocking,CURLLink`CURLHandleUnload[easyhandles]];
			unsetCURLHandle[easyhandles];
		
		
		If[error === $Failed,
			$Failed,
			If[Head[urlExp]===List,cookiefunction[OptionValue[System`CookieFunction]];output,output[[1]]]
		]
	]

URLFetch[urlExp_/;isURL[urlExp,URLFetch], res:(_String|_List|All), opts:OptionsPattern[]] /; InitializeQ[] :=
	Module[{stream,oldhandle,streamIsRequested,contentOrContentDataIsRequested,requestedElements=Flatten@{res},url,handle, output, error, stdOpts, elements, wellFormedURL, oauth, token, args,isblocking=True},
		url=getURL[urlExp,URLFetch];
		setMessageHead[URLFetch];
		
		$LastKnownCookies=CURLLink`Cookies`GetKnownCookies[];
		
		streamIsRequested=MemberQ[requestedElements,"Stream"];
		
		contentOrContentDataIsRequested=MemberQ[requestedElements,"Content"|"ContentData"];
		
		(*If we asked for a Stream then CURLPerform[] will be non-blocking*)
		If[streamIsRequested,isblocking=False];

		If[streamIsRequested && contentOrContentDataIsRequested,Throw[$Failed,CURLLink`Utilities`Exception]];
		
		If[res===All,requestedElements=Complement[$URLFetchElements,{"Stream"}]];
				
		If[OptionValue["OAuthAuthentication"] =!= None,
			oauth = OptionValue["OAuthAuthentication"];
			token = If[Head[oauth] === OAuthSigning`OAuthToken, oauth, OAuthSigning`OAuthAuthentication[oauth]];
			stdOpts = FilterRules[Flatten[{opts}], Except["OAuthAuthentication"]];
			args = OAuthSigning`OAuthSignURL[url, Join[stdOpts, {"CredentialsProvider" -> None, "OAuthAuthentication" -> token}]]; 
			Return[URLFetch @@ args]
		];
		stdOpts = Flatten[{opts, FilterRules[Options[URLFetch], Except[{opts}]]}];
		error = Catch[
			handle = commonInit[url, URLFetch, stdOpts];
			If[handle === $Failed,
				Return[$Failed]
			];
			setOutput[handle, "String"];
			If[MatchQ[handle["Proxies"], {}|{""}],
				handle["Return"] = CURLLink`CURLPerform[handle,"Blocking"->isblocking];
				handle=retryIfSSLError[handle,url,URLFetch,None,None,stdOpts];
				If[streamIsRequested,stream=getResponseCodes[handle][[1]]];
				If[CURLLink`CURLStatusCode[handle] === 401 && allowCredintalDialog[opts],
					oldhandle=handle;
					handle=getNewHandle[url,URLFetch,None,stdOpts];
					If[credWrapper[handle, url, OptionValue["CredentialsProvider"]],
						handle["Return"] = CURLLink`CURLPerform[handle,"Blocking"->isblocking];
						If[streamIsRequested,Close[stream],CURLLink`CURLHandleUnload[oldhandle]];
						,
						handle=oldhandle;
					]
				]
			(*else*),
				Do[
					CURLLink`CURLOption[handle, "CURLOPT_PROXY", handle["Proxies"][[i]]];
					handle["Return"] = CURLLink`CURLPerform[handle,"Blocking"->isblocking];
					handle=retryIfSSLError[handle,url,URLFetch,None,handle["Proxies"][[i]],stdOpts];
					If[streamIsRequested,stream=getResponseCodes[handle][[1]]];
					If[MemberQ[{CURLLink`CURLHTTPConnectCode[handle],CURLLink`CURLStatusCode[handle]},401] && allowCredintalDialog[opts],
						oldhandle=handle;
						handle=getNewHandle[url,URLFetch,None,stdOpts];
						If[credWrapper[handle, url, OptionValue["CredentialsProvider"]],
							handle["Return"] = CURLLink`CURLPerform[handle,"Blocking"->isblocking];
							If[streamIsRequested,Close[stream],CURLLink`CURLHandleUnload[oldhandle]];
							,
							handle=oldhandle;
						]
					];
					If[MemberQ[{CURLLink`CURLHTTPConnectCode[handle],CURLLink`CURLStatusCode[handle]},407]&& allowCredintalDialog[opts],
						oldhandle=handle;
						handle=getNewHandle[url,URLFetch,None,stdOpts];
						If[proxyCredentials[handle, url],
							If[streamIsRequested,Close[stream],CURLLink`CURLHandleUnload[oldhandle]];
							handle["Return"] = CURLLink`CURLPerform[handle,"Blocking"->isblocking];
							handle=retryIfSSLError[handle,url,URLFetch,None,handle["Proxies"][[i]],stdOpts];
							If[streamIsRequested,stream=getResponseCodes[handle][[1]]];
							If[CURLLink`CURLStatusCode[handle] === 401 && allowCredintalDialog[opts],
								oldhandle=handle;
								handle=getNewHandle[url,URLFetch,None,stdOpts];
								If[credWrapper[handle, url, OptionValue["CredentialsProvider"]],
									handle["Return"] = CURLLink`CURLPerform[handle,"Blocking"->isblocking];
									If[streamIsRequested,Close[stream],CURLLink`CURLHandleUnload[oldhandle]];
									If[streamIsRequested,getResponseCodes[handle]];
									,
									handle=oldhandle;
								  ]
							  ];
							  ,
							  handle=oldhandle;
						]
					];
					(* these error codes indicate a problem with the proxy *)
					If[handle["Return"] =!= 5 && handle["Return"] =!= 7,
						Break[]
					];
	
				, {i, Length[handle["Proxies"]]}
				];		
			];
			If[CURLLink`CURLStatusCode[handle] === 401, 
				wellFormedURL = If[StringMatchQ[url, {"http://*", "https://*, ftp://*, ftps://*"}], 
					URIJoin[Flatten@{URISplit[url]}]
				(*else*), 
					URIJoin[Flatten@{URISplit["http://" <> url]}]
				];				
				
				sessionStore[wellFormedURL] := False
			];
			
			If[CURLLink`CURLStatusCode[handle] === 407||CURLLink`CURLHTTPConnectCode[handle] === 407,
				$proxyCache = False;
			];
			
			If[handle["Return"] =!= 0,
				CURLLink`CURLHandleUnload[handle];
				Message[URLFetch::invhttp, CURLLink`CURLError[handle["Return"]]];
				Return[$Failed]
			];
		
			If[(OptionValue[System`CookieFunction]=!=None)&&OptionValue["StoreCookies"] ,
				storeCookies[HTTPData[handle, "Cookies"]]
			]; 
		
			elements = If[handle["FTP"]===True, $FTPFetchElements, $URLFetchElements];
			(* Perhaps the user just wants to know the available output types. *)
			If[res === "Elements",
					Return[elements]
			];
			output = parseElements[handle, requestedElements, elements];
			(*
			if non blocking,i.e stream element is 
			requested then unload happens in c-code
			when Close[InputStream[..]] is called
			*)
			If[isblocking,CURLLink`CURLHandleUnload[handle]];
			unsetCURLHandle[handle];
			unsetHTTPData[handle];
		,CURLLink`Utilities`Exception];
		
		If[error === $Failed,
			$Failed,
			cookiefunction[OptionValue[System`CookieFunction]];
			output
		]
	]
	
	
URLFetch::invhttp = "`1`.";
URLFetch::noelem = "The element \"`1`\" is not allowed."
URLFetch::invurl="`1` is not a valid URL";
URLFetchAsynchronous::invurl="`1` is not a valid URL";
	
(****************************************************************************)
(* URLSave... *)
Options[URLSave] = Join[$StandardOptions, {BinaryFormat->True}]

URLSave[urlExp_, options___?OptionQ] := 
	URLSave[urlExp, Automatic, options]

URLSave[urlExp_/;isURL[urlExp,URLSave], Automatic|None|Null, rest___] := 
	URLSave[urlExp, FileNameJoin[{$TemporaryDirectory, CreateUUID[] <> ".tmp"}], rest]

URLSave[urlExp_, file_, res:(_String|_List|All):"Content", options___?OptionQ] /; deprecatedOptionQ[options] := 
	URLSave[urlExp, file, deprecatedOptionFix[URLSave, options]]  
	
URLSave[urlExp_/;isURL[urlExp,URLSave], fileExp_/;isFile[fileExp,URLSave], res:(_String|_List|All):"Content", opts:OptionsPattern[]] /; InitializeQ[] :=
	Module[{oldhandle,handle, output, error,file ,stdOpts, elements, wellFormedURL, oauth, token, args,url},
		setMessageHead[URLSave];
		
		url=getURL[urlExp];
		
		file=getFile[fileExp];
		
		$LastKnownCookies=CURLLink`Cookies`GetKnownCookies[];
		
		If[OptionValue["OAuthAuthentication"] =!= None,
			oauth = OptionValue["OAuthAuthentication"];
			token = If[Head[oauth] === OAuthSigning`OAuthToken, oauth, OAuthSigning`OAuthAuthentication[oauth]];
			stdOpts = FilterRules[Flatten[{opts}], Except["OAuthAuthentication"]];
			args = OAuthSigning`OAuthSignURL[url, Join[stdOpts, {"CredentialsProvider" -> None, "OAuthAuthentication" -> token}]]; 
			Return[URLSave @@ {First[args], file, Rest[args]}]
		];
		stdOpts = Flatten[{opts, FilterRules[Options[URLSave], Except[{opts}]]}];
		error = Catch[
			handle = commonInit[url, URLSave, stdOpts];
			If[handle === $Failed,
				Return[$Failed]
			];
		
			setOutput[handle, "File", ExpandFileName[file], OptionValue[BinaryFormat]];
			
			If[MatchQ[handle["Proxies"], {}|{""}],
				handle["Return"] = CURLLink`CURLPerform[handle];
				If[CURLLink`CURLStatusCode[handle] === 401,
					oldhandle=handle;
					handle=getNewHandle[url,URLSave,file,stdOpts];
					If[credWrapper[handle, url, OptionValue["CredentialsProvider"]],
						CURLLink`CURLHandleUnload[oldhandle];
						handle["Return"] = CURLLink`CURLPerform[handle];
						,
						handle=oldhandle;
					]
				]
			(*else*),
				Do[
					CURLLink`CURLOption[handle, "CURLOPT_PROXY", handle["Proxies"][[i]]];
					handle["Return"] = CURLLink`CURLPerform[handle];
					
					If[MemberQ[{CURLLink`CURLHTTPConnectCode[handle],CURLLink`CURLStatusCode[handle]},401],
						oldhandle=handle;
						handle=getNewHandle[url,URLSave,file,stdOpts];
						If[credWrapper[handle, url, OptionValue["CredentialsProvider"]],
							CURLLink`CURLHandleUnload[oldhandle];
							handle["Return"] = CURLLink`CURLPerform[handle];
							,
							handle=oldhandle;
						];
					];
					If[ MemberQ[{CURLLink`CURLHTTPConnectCode[handle],CURLLink`CURLStatusCode[handle]},407],
						oldhandle=handle;
						handle=getNewHandle[url,URLSave,file,stdOpts];
						If[proxyCredentials[handle, url],
							CURLLink`CURLHandleUnload[oldhandle];
							handle["Return"] = CURLLink`CURLPerform[handle];
							If[ MemberQ[{CURLLink`CURLHTTPConnectCode[handle],CURLLink`CURLStatusCode[handle]},401],
								oldhandle=handle;
								handle=getNewHandle[url,URLSave,file,stdOpts];
								If[credWrapper[handle, url, OptionValue["CredentialsProvider"]],
									handle["Return"] = CURLLink`CURLPerform[handle];
									CURLLink`CURLHandleUnload[oldhandle];
									,
									handle=oldhandle;
								  ];
							  ];
							  
							  ,
							  handle=oldhandle;
						]
					];
	
					(* these error codes indicate a problem with the proxy *)
					If[handle["Return"] =!= 5 && handle["Return"] =!= 7,
						Break[]
					]
					, {i, Length[handle["Proxies"]]}
				];		
			];
			If[CURLLink`CURLStatusCode[handle] === 401, 
				wellFormedURL = If[StringMatchQ[url, {"http://*", "https://*, ftp://*, ftps://*"}], 
					URIJoin[Flatten@{URISplit[url]}]
				(*else*), 
					URIJoin[Flatten@{URISplit["http://" <> url]}]
				];				
				
				sessionStore[wellFormedURL] := False
			];
			
			If[CURLLink`CURLStatusCode[handle] === 407,
				$proxyCache = False;
			];
			
			If[handle["Return"] =!= 0,
				CURLLink`CURLHandleUnload[handle];
				Message[URLSave::invhttp, CURLLink`CURLError[handle["Return"]]];
				Return[$Failed]
			];
		
			If[(OptionValue[System`CookieFunction]=!=None)&&OptionValue["StoreCookies"] && (OptionValue["Cookies"] =!= Automatic),
				storeCookies[HTTPData[handle, "Cookies"]]
			]; 
		
			elements = If[handle["FTP"]===True, $FTPSaveElements, $URLSaveElements];
			(* Perhaps the user just wants to know the available output types. *)
			If[res === "Elements",
				Return[elements]
			];
	
			output = 
				If[res === "Content",
					file
				(*else*), 
					parseElements[handle, res, elements]
				];
		
			CURLLink`CURLHandleUnload[handle];
			unsetCURLHandle[handle];
		,CURLLink`Utilities`Exception];
		
		If[error === $Failed,
			$Failed,
			cookiefunction[OptionValue[System`CookieFunction]];
			output
		]
	]

URLSave::invhttp = "`1`.";
URLSave::noelem = "The element \"`1`\" is not allowed.";
URLSave::invurl="`1` is not a valid URL";
URLSaveAsynchronous::invurl="`1` is not a valid URL";
URLSave::invfile="`1` is not a valid File";
URLSaveAsynchronous::invfile="`1` is not a valid File";
(****************************************************************************)
(* Useful functions for both URLFetch and URLSave *)

setMessageHead[head_] := $MessageHead = head;
curlMessage[head_, tag_, args___] := Message[MessageName[head, tag], args]

connectQ[] :=
	If[$AllowInternet,
		True
	(*else*),
		Message[URLFetch::offline];
		False
	];
	
(* Check all the options passed are valid. *)
validOptionsQ[opts_, func_] := 
	Module[{},
		If[opts === {},
			Return[True]
		];
		
		If[FilterRules[opts, Except[Options[func]]] =!= {},
			Message[General::optx, First[#], InString[$Line]] & /@ FilterRules[opts, Except[Options[func]]];
			Return[False];	
		];

		If[!StringQ[(Method /. opts)] || (Method /. opts) === "",
			If[!StringQ[("Method" /. opts)] || StringMatchQ[( "Method"/. opts), "Method"] || ("Method" /. opts) === "",
				Message[General::erropts, (Method /. opts /. Method -> "Method" ) /. opts, "Method"];
				Return[False];
			];
		];
		
		If[!MatchQ[("Headers" /. opts), List[Rule[_String, _String]...]],
			Message[General::erropts, "Headers" /. opts, "Headers"];
			Return[False];
		];
		
		If[!StringQ[("Username" /. opts)],
			Message[General::erropts, "Username" /. opts, "Username"];
			Return[False];
		];
		
		If[!StringQ[("Password" /. opts)],
			Message[General::erropts, "Password" /. opts, "Password"];
			Return[False];
		];
		
		If[("UserAgent" /. opts)=!= Automatic && !StringQ[("UserAgent" /. opts)],
			Message[General::erropts, "UserAgent" /. opts, "UserAgent"];
			Return[False];
		];
	
		If[!MatchQ[("VerifyPeer" /. opts), True|False],
			Message[General::erropts, "VerifyPeer" /. opts, "VerifyPeer"];
			Return[False];
		];
		
		If[!MatchQ[("StoreCookies" /. opts), True|False],
			Message[General::erropts, "StoreCookies" /. opts, "StoreCookies"];
			Return[False];
		];
		
		If[("Parameters" /. opts) === "Parameters",
			Return[True];
		];
		
		If[!MatchQ["Parameters" /. opts, List[Rule[_String, _String]...]],
			Message[General::erropts, "Parameters" /. opts, "Parameters"];
			Return[False];
		];

		If[!MatchQ[("Body" /. opts),None| _String|List[___Integer]],
			Message[General::erropts, "Body" /. opts, "Body"];
			Return[False];
		];
		
		If[("MultipartElements" /. opts) =!= {} && (
                                                    !MatchQ[("MultipartElements" /. opts), {{_String, _String,___String, {__Integer}}..}] &&
                                                    !MatchQ[("MultipartElements" /. opts), {Rule[{_String, _String|Automatic,___String}, {__Integer}|File[_String]|_String]..}] &&
                                                    !MatchQ[("MultipartElements" /. opts), {Rule[{_String, _String|Automatic,___String}, _String]..}]
                                                    
                                                    ),
			Message[General::erropts, "MultipartElements" /. opts, "MultipartElements"];
			Return[False];
		];
		
		If[!NonNegative[("ConnectTimeout" /. opts)],
			Message[General::erropts, "ConnectTimeout" /. opts, "ConnectTimeout"];
			Return[False];
		];
		
		If[!NonNegative[("ReadTimeout" /. opts)],
			Message[General::erropts, "ReadTimeout" /. opts, "ReadTimeout"];
			Return[False];
		];
	
		(* If we made it here, all the options should be valid. *)
		True
	]
	
(* Initialization routines common to both URLSave and URLFetch. *)
commonInit[urls_List, func_, opts_List]:=Map[commonInit[#,func,opts]&,urls]
commonInit[url_String, func_, opts_List] := 
	Module[{handle,norevoke=2},
		
		(* First determine if we're allowed to connect to the internet. *)	
		If[!connectQ[],
			Return[$Failed]
		];
		(* Now check all the options passed are valid. *)
		If[!validOptionsQ[Flatten[opts], func],
			Return[$Failed]	
		];
	
		handle = CURLLink`CURLHandleLoad[];
		handle["FTP"] = StringMatchQ[url, {"ftp://"~~___, "ftps://"~~___}];
		If[("UseProxy" /. PacletManager`$InternetProxyRules) =!= Automatic ,
			handle["Proxies"] = getProxies[url, "UseProxy" /. PacletManager`$InternetProxyRules];
			CURLLink`CURLSetProxies[handle, #] & /@ handle["Proxies"];
		];
		If[(("UseProxy" /. PacletManager`$InternetProxyRules) === Automatic) && (func === URLFetch || func === URLSave),
			handle["Proxies"] = getProxies[url, "UseProxy" /. PacletManager`$InternetProxyRules];
			CURLLink`CURLSetProxies[handle, #] & /@ handle["Proxies"];
		];
		If[(("UseProxy" /. PacletManager`$InternetProxyRules) === Automatic) && (func === URLFetchAsynchronous || func === URLSaveAsynchronous),
			CURLLink`CURLSetProxies[handle, "Automatic"];
		];
		CURLLink`CURLOption[handle, "CURLOPT_PROXYAUTH", 15];
		(* A bit mask passed to libcurl to indicated HTTP,HTTPS,FTP, and FTPS are the only allowed protocols *)
		CURLLink`CURLOption[handle, "CURLOPT_PROTOCOLS", 15]; 
		CURLLink`CURLOption[handle, "CURLOPT_NOSIGNAL", True];
		
		If[((System`CookieFunction/.opts)===None || !("StoreCookies" /. opts)) && ("Cookies" /. opts) === Automatic,
			setStandardOptions[handle, url, FilterRules[{Flatten[FilterRules[opts, Except["Cookies"]]], "Cookies"->$HTTPCookies}, $StandardOptions]]
		(*else*),
			setStandardOptions[handle, url, FilterRules[Flatten[opts], $StandardOptions]]
		];
		If[$OperatingSystem==="Windows",CURLLink`CURLOption[handle, "CURLOPT_SSL_OPTIONS",norevoke]];
		(*
		-When CURLHandleLoad is called, both 
		 easy_handle and multi_handle are created.
		-CURLHandle[<..>] contains easy_handle and multi_handle
		-URLFetch and URLSave use curl_multi_perform, 
		 which acts on multi_handle.
		-We must add easy_handle to multi_handle
		 and then use curl_multi_perform to start the transfer.
		-So, when doing URLFetch or URLSave, 
		 we add easy_handle to the multi_handle, i.e:
		 CURLLink`CURLMultiHandleAdd[handle,{handle}]
		-URLFetchAsynchronous and URLSaveAsynchronous use 
		 curl_easy_perform which acts on easy_handle. 
		 For this reason we do not need to add easy_handle to the multi_handle. 
		 We just use the easy_handle represented by CURLHandle[<..>]
		*) 
		If[MemberQ[{URLFetch,URLSave},func],CURLLink`CURLMultiHandleAdd[handle,{handle}],handle]
	]

(****************************************************************************)
(* Parse elements to return correct data *)
parseElements[handlesAndElements_List,out_]:=Map[parseElements[#[[1]],out,#[[2]]]&,handlesAndElements]
parseElements[handle_, out_, elements_] :=
	Module[{},
		Which[
			out === All, parseAll[handle, out, elements],
			StringQ[out], parseString[handle, out, elements],
			ListQ[out], parseList[handle, out, elements],
			True, Throw[$Failed,CURLLink`Utilities`Exception]
		]
	]

parseAll[handle_, All, elements_] := HTTPData[handle, #] & /@ elements;

parseString[handle_, "All", elements_] := parseAll[handle, All, elements] 
parseString[handle_, "Rules", elements_] := Rule @@@ Partition[Riffle[elements, (HTTPData[handle, #] & /@ elements)], 2]
parseString[handle_, str_String, elements_] := If[MemberQ[elements, str], HTTPData[handle, str],  curlMessage[$MessageHead, "noelem", ToString[str]]; Throw[$Failed,CURLLink`Utilities`Exception]]

parseList[handle_, list_List, elements_] :=
	Module[{subList},
		If[Length[list] === 1,
			Which[
				StringQ[First[list]], parseString[handle, First[list], elements],
				ListQ[First[list]], 
					subList = First[list];
					If[Length[subList] === 1,
						If[StringQ[First[subList]], 
							parseString[handle, First[subList], elements]
						(*else*),
							Return[$Failed]
						]
					(*else*),
						HTTPData[handle, #] & /@ subList	
					]
				,
				True, Return[$Failed]
			]
		(*else*),
			(*Special Case: {"Rules", {...}}*)
			If[MatchQ[list, {"Rules", List[_String ...]}],
				parseString[handle, "Rules", Last[list]]
			(*else*),
				parseString[handle, #, elements] & /@ list
			]
		]
	]

(****************************************************************************)

buildData[handle_CURLLink`CURLHandle, data_List, method_String] /; InitializeQ[] := 
	Quiet[
		Check[
			StringExpression[ 
				Sequence @@ 
				Riffle[CURLLink`CURLEscape[ToString[First[#]]] <> "=" <> CURLLink`CURLEscape[ToString[Last[#]]] & /@ data, "&"]
			], 
			Throw[$Failed,CURLLink`Utilities`Exception]
		]
	]

HTTPData[handles_List,element_String]:=Map[HTTPData[#,element]&,handles]	
(****************************************************************************)

(* stream *)
HTTPData[handle : CURLLink`CURLHandle[id_], "Stream"] /;errorQ[handle] :=HTTPData[ CURLLink`CURLHandle[id], "Stream"]=
 (OpenRead[handle["URL"],Method -> {"HTTPStreamElement", "CURLHandle" -> id}])
 
(****************************************************************************)

(* Return the headers of a CURLHandle as a list of rules. *)
HTTPData[handle_CURLLink`CURLHandle, "Headers"] /; errorQ[handle] := 
	impHeaders[CURLLink`CURLHeaderData[handle]];

HTTPData[handle_CURLLink`CURLHandle, "HeadersReceived"] /; errorQ[handle] :=
With[{lastheader=Last[StringSplit[CURLLink`CURLHeaderData[handle],"\r\n\r\n"]]}, 
	impHeaders[lastheader]
]
impHeaders[string_]:=Cases[StringSplit[StringSplit[string, "\r\n"], ": ", 2], {_, _}]
(****************************************************************************)
HTTPData[handle_CURLLink`CURLHandle, "Cookies"] /; errorQ[handle] := 
	Cases[
		{	"Domain"-> First[#], 
			If[#[[2]] === "FALSE",
				"MachineAccess"-> #[[2]]
			],
			"Path"->#[[3]], 
			"Secure"->#[[4]], 
			"ExpirationDate"->DateString[ToExpression[#[[5]]] + AbsoluteTime[{1970, 1, 1, 0, 0, 0}]], 
			"Name"->#[[6]], 
			"Value"->Last[#]
		}, 
		Except[Null]] & /@ StringSplit[StringSplit[CURLLink`CURLCookies[handle], "\n"], "\t"];

(****************************************************************************)
addHeaders[handle_CURLLink`CURLHandle, headers_List] :=
	CURLLink`CURLAddHeader[handle, StringReplace[ToString[First[#]] <> ": " <> ToString[Last[#]], "\n"->""]] & /@ headers


(****************************************************************************)
addCookies[handle_CURLLink`CURLHandle, ucookies_List] := 
	Module[{errs,cookies=ucookies},
		errs = Catch[
			If[cookies === {},
				CURLLink`CURLOption[handle, "CURLOPT_COOKIELIST", ""];
				Return[]		
			];
			(*if list of Assocs. is passed covert it to list of rules*)
			CURLLink`CURLOption[handle,"CURLOPT_COOKIELIST","SESS"];
			CURLLink`CURLOption[handle,"CURLOPT_COOKIEJAR",Quiet@Check[getFile@System`$CookieStore,""]];
			CURLLink`CURLOption[handle,"CURLOPT_COOKIELIST","FLUSH"];
			CURLLink`CURLOption[handle,"CURLOPT_COOKIEJAR",""];
			cookies=Map[Association,ucookies];
			cookies=Map[CURLLink`Cookies`Private`toOldCookie, cookies];
			CURLLink`CURLOption[handle, "CURLOPT_COOKIELIST", 
				StringJoin[
					ReleaseHold[{
							"Domain", "\t", 
							If[("MachineAccess" /. #) === "MachineAccess",
								"TRUE",
								"MachineAccess"
							], "\t",  			
							"Path", "\t", 
							"Secure", "\t", 
							Hold[ToString[AbsoluteTime["Expires"] - AbsoluteTime[{1970, 1, 1, 0, 0, 0}]]], "\t", 
							"Name", "\t", 
							"Value"
						} /. Rule @@@ #
					]
				]
			] & /@ cookies;
			(*Save to $CookieStore*)
			
			
			
			
		,CURLLink`Utilities`Exception];
	]




	
storeCookies[cookies_List] /; InitializeQ[] :=
	Module[{handle},
		handle = CURLLink`CURLHandleLoad[];
		setStandardOptions[handle, ""];
		addCookies[handle, cookies];
		
		CURLLink`CURLHandleUnload[handle];
	]

$LastKnownCookies="";

cookiefunction[f_] := 
	Module[{cookiesreceived,allcookies,handle,res},
		handle = CURLLink`CURLHandleLoad[];
		setStandardOptions[handle, ""];
		allcookies=CURLLink`CURLCookies[handle];
		CURLLink`CURLHandleUnload[handle];
		cookiesreceived=StringDelete[allcookies,$LastKnownCookies];
		res=CURLLink`Cookies`Private`cookiesToAssociation[cookiesreceived];
		Map[System`ClearCookies[#]&,res];     
		If[f===Automatic,System`SetCookies[res],Map[f,res]]

	]


$HTTPCookies /; InitializeQ[] :=
	Module[{cookies, handle, error},
		error = Catch[
			handle = CURLLink`CURLHandleLoad[];
			setStandardOptions[handle, ""];
			handle["Return"] = 0;
			cookies = HTTPData[handle, "Cookies"];
			CURLLink`CURLHandleUnload[handle];
		,CURLLink`Utilities`Exception];
		If[error === $Failed, $Failed, cookies]
	]
	

(****************************************************************************)

(* Return the headers of a CURLHandle as a list of rules. *)
HTTPData[handle_CURLLink`CURLHandle, "Headers"] /; errorQ[handle] := 
	Cases[StringSplit[StringSplit[CURLLink`CURLHeaderData[handle], "\r\n"], ": ", 2], {_, _}];
	

(* Return the cookies used for by this CURLHandle. *)
HTTPData[handle_CURLLink`CURLHandle, "Cookies"] /; errorQ[handle] := 
	Cases[
		{	"Domain"-> First[#], 
			If[#[[2]] === "FALSE",
				"MachineAccess"-> #[[2]]
			],
			"Path"->#[[3]], 
			"Secure"->#[[4]], 
			"ExpirationDate"->DateString[ToExpression[#[[5]]] + AbsoluteTime[{1970, 1, 1, 0, 0, 0}]], 
			"Name"->#[[6]], 
			"Value"->Last[#]
		}, 
		Except[Null]] & /@ StringSplit[StringSplit[CURLLink`CURLCookies[handle], "\n"], "\t"];
		
HTTPData[handle_CURLLink`CURLHandle, "CookiesReceived"] /; errorQ[handle]:=
Module[
	{allcookies,cookiesreceived,chandle},
	chandle = CURLLink`CURLHandleLoad[];
	setStandardOptions[chandle, ""];
	allcookies=CURLLink`CURLCookies[chandle];
	chandle["Return"] = 0;
	CURLLink`CURLHandleUnload[chandle];
	
	cookiesreceived=StringDelete[allcookies,$LastKnownCookies];
	CURLLink`Cookies`Private`cookiesToAssociation[cookiesreceived]
]


(* Return the content as a list of bytes of a given CURLHandle. *)
HTTPData[handle_CURLLink`CURLHandle, "ContentData"] /; errorQ[handle] := 
		CURLLink`CURLRawContentData[handle]
	
(* Return the content as a String of a given CURLHandle. *)
HTTPData[handle_CURLLink`CURLHandle, "Content"] /; errorQ[handle] :=
Module[
	{bytes,   mCharset="ISO8859-1"}, 
	
	bytes = HTTPData[handle, "ContentData"];
	Which[
		handle["FTP"] === True,
			Quiet[Check[FromCharacterCode[bytes, "UTF-8"], FromCharacterCode[bytes, "ISO8859-1"]]]
		,
		True,
			mCharset=getCharacterEncoding[HTTPData[handle, "Headers"]];
			FromCharacterCode[bytes,mCharset]
		]
	]
getCharacterEncoding[headers_]:=
Module[
	{contentTypeHeader,contentType,charset,mCharset="ISO8859-1"},
	contentTypeHeader=Select[headers, StringMatchQ[First[#], "Content-Type", IgnoreCase -> True] &];
	If[MatchQ[contentTypeHeader,{{_String,_String}..}],
				(*then*)
				contentType = contentTypeHeader[[-1,2]];
				charset = StringReplace[contentType,StartOfString ~~ ___ ~~(" "|";")~~ "charset=" ~~ c__ ~~ (WhitespaceCharacter | EndOfString) :> c,IgnoreCase->True ];
				mCharset = charsetToMCharset[charset];
				];
	mCharset		
]
charsetToMCharset[charset_] := (
    CloudObject; (* make sure the CloudObject paclet is loaded *)
    CloudObject`ToCharacterEncoding[charset, "ISO8859-1"]
)

		
(* Return the status code as an Integer of a given CURLHandle. *)
HTTPData[handle_CURLLink`CURLHandle, "StatusCode"] /; errorQ[handle] := 
	CURLLink`CURLStatusCode[handle]
	
(* Catch all for bad types *)
HTTPData[handle_CURLLink`CURLHandle, unknown_String/;!MemberQ[$returnTypes,unknown]] := (curlMessage[$MessageHead, "noelem", ToString[unknown]]; Throw[$Failed,CURLLink`Utilities`Exception])

(****************************************************************************)
URISplit[uri_String] := 
	Flatten[
		StringCases[
			uri, 
			RegularExpression[ "^(([^:/?#]+):)?(//([^/?#]*))?([^?#]*)(\\?([^#]*))?(#(.*))?"] -> 
			   	{"Scheme" -> "$2", "Authority" -> "$4"}
		]
	]

URIJoin[uri : List[_Rule, _Rule]] := 
	Module[{scheme, authority},
		If[!Fold[And, True, Map[MatchQ[#, Rule[_String, _String]] &, uri]], Return[$Failed]]; 
		{scheme, authority} = Map[Last, uri];
		StringJoin[
			Cases[{
				If[scheme =!= "", StringJoin[scheme, ":"]],
				Which[
					authority =!= "" && scheme =!= "", StringJoin["//", authority],
					authority === "" && scheme =!= "", authority
				]
			}, Except[Null]]
		]
	]

(****************************************************************************)

buildProxy[{scheme_String, url_String}] := If[StringMatchQ[url, scheme <> "://*"], url, scheme <> "://" <> url]
buildProxy[{url_String}] := url
buildProxy[url_String] := url	
	
getProxies[url_String, False] = {""}
getProxies[url_String, True] := Cases[Rest[PacletManager`$InternetProxyRules], Rule[scheme_, {proxy_, port_}] :> 
	If[StringMatchQ[proxy, scheme <> "://*", IgnoreCase -> True], "", ToLowerCase[scheme] <> "://"] <> proxy <> ":" <> ToString[port]]

getProxies[url_String, Automatic] :=
	getSystemProxies[url, $OperatingSystem]
	
getSystemProxies[url_String, "Windows"] :=
	Module[{rawProxies, proxies},
		rawProxies = If[StringMatchQ[url, {"http://*", "https://*, ftp://*, ftps://*"}],
			Quiet[Check[CURLLink`CURLGetProxies[url], {}], LibraryFunction::strnull]
		(*else*),
			Quiet[Check[CURLLink`CURLGetProxies["http://" <> url], {}], LibraryFunction::strnull]
		];
		
		proxies = StringSplit[StringSplit[rawProxies, ";"], "=", 2];
		buildProxy[#] & /@ proxies
	]	
	
getSystemProxies[url_String, "MacOSX"] := 
	Module[{},	
		If[StringMatchQ[url, {"http://*", "https://*", "ftp://*", "ftps://*"}],
			Flatten@{Quiet[Check[CURLLink`CURLGetProxies[URIJoin[Flatten@{URISplit[url]}]], {}]]}
		(*else*),
			Flatten@{Quiet[Check[CURLLink`CURLGetProxies[URIJoin[Flatten@{URISplit["http://" <> url]}]], {}]]}
		]
	]
	
getSystemProxies[url_String, _] := {}

setProxies[handle_CURLLink`CURLHandle] := CURLLink`CURLSetProxies[handle, StringJoin@Riffle[handle["Proxies"], "\n"]] 
(****************************************************************************)
setOutput[easyhandles_List,"String"]:=Map[setOutput[#,"String"]&,easyhandles]
setOutput[handle_CURLLink`CURLHandle, "String"] := 
	(
		If[!(handle["FTP"]===True),
			CURLLink`CURLOption[handle, "CURLOPT_HEADERFUNCTION", "WRITE_MEMORY"];
			CURLLink`CURLOption[handle, "CURLOPT_WRITEHEADER", "MemoryPointer"];
		];
		CURLLink`CURLOption[handle, "CURLOPT_WRITEFUNCTION", "WRITE_MEMORY"];
		CURLLink`CURLOption[handle, "CURLOPT_WRITEDATA", "MemoryPointer"];
	)
	
setOutput[handle_CURLLink`CURLHandle, "File", fileName_String, format:(True|False)] := 
	(
		If[!(handle["FTP"]===True),
			CURLLink`CURLOption[handle, "CURLOPT_HEADERFUNCTION", "WRITE_MEMORY"];
			CURLLink`CURLOption[handle, "CURLOPT_WRITEHEADER", "MemoryPointer"];
		];
		
		CURLLink`CURLFileInfo[handle, fileName, format];
		CURLLink`CURLOption[handle, "CURLOPT_WRITEFUNCTION", "WRITE_FILE"];
		CURLLink`CURLOption[handle, "CURLOPT_WRITEDATA", "FilePointer"];
	)
	
setOutput[handle_CURLLink`CURLHandle, "WriteFunction", func_String] :=
	(
		If[!(handle["FTP"]===True),
			CURLLink`CURLOption[handle, "CURLOPT_HEADERFUNCTION", "WRITE_MEMORY"];
			CURLLink`CURLOption[handle, "CURLOPT_WRITEHEADER", "MemoryPointer"];	
		];
		CURLLink`CURLWriteInfo[handle, func];
		CURLLink`CURLOption[handle, "CURLOPT_WRITEFUNCTION", "WRITE_USER"];
	)

(****************************************************************************)

setStandardOptions[handle_CURLLink`CURLHandle, iurl_String, opts:OptionsPattern[]] := 
	Module[{assoc,authentication,multipartElements,parameters,url=iurl,finalURL, method = ToUpperCase[OptionValue["Method"]], baseURL,optionValueCookies}, 
		finalURL = url;
		optionValueCookies=Which[	OptionValue["Cookies"]===Automatic && OptionValue["Cookies"]===Automatic,
									Automatic
									,
									OptionValue["Cookies"]=!=Automatic && OptionValue["Cookies"]===Automatic,
									OptionValue["Cookies"]
									,
									True,
									OptionValue["Cookies"]
									
								];
									
		If[OptionValue["UserAgent"] === Automatic,
			CURLLink`CURLOption[handle, "CURLOPT_USERAGENT", "Wolfram HTTPClient " <> ToString[$VersionNumber]],	
			CURLLink`CURLOption[handle, "CURLOPT_USERAGENT", OptionValue["UserAgent"]];
		];
		multipartElements=OptionValue["MultipartElements"];
		parameters=OptionValue["Parameters"];
		authentication=OptionValue[Authentication];
		If[Head[authentication]===PermissionsKey,
			assoc = URLParse[url];
			parameters=Join[parameters,assoc["Query"]];
			url=URLBuild[AssociateTo[assoc, "Query" -> {}]];
			parameters=Join[parameters, {"_key" -> First[authentication]}]
		];
		(*add to parameters to multipart-elements*)
		If[ MatchQ[parameters, {__}] && MatchQ[ multipartElements, {__}],
			multipartElements=appendParametersToMultipartElements[parameters,multipartElements];
			parameters={};
		];
		
		(*For Mac we use OSX native Keychain, after switching to darwinssl, this is only relevent when the using openssl*)	
		If[$SystemID=!="MacOSX-x86-64",
			CURLLink`CURLOption[handle, "CURLOPT_CAINFO", $CACERT];
		];
		CURLLink`CURLOption[handle, "CURLOPT_SSL_VERIFYPEER", OptionValue["VerifyPeer"]]; 
		CURLLink`CURLOption[handle, "CURLOPT_FOLLOWLOCATION", OptionValue["FollowRedirects"]];
		CURLLink`CURLOption[handle, "CURLOPT_POSTREDIR", CURLInfo`Private`$CURLPostRedir]; 
		CURLLink`CURLOption[handle, "CURLOPT_TIMEOUT_MS", Round[1000*N[OptionValue["ReadTimeout"]]]];
		CURLLink`CURLOption[handle, "CURLOPT_CONNECTTIMEOUT_MS", Round[1000*N[OptionValue["ConnectTimeout"]]]];
		
		Which[
			method === "GET",
			CURLLink`CURLOption[handle, "CURLOPT_CUSTOMREQUEST", "GET"]
			,
			method === "POST",
			CURLLink`CURLOption[handle, "CURLOPT_POST", True];
			,
			method === "HEAD",
			CURLLink`CURLOption[handle, "CURLOPT_NOBODY", True];
			,
			method ==="PUT",
			CURLLink`CURLOption[handle, "CURLOPT_CUSTOMREQUEST", method];
			,
			True,
			CURLLink`CURLOption[handle, "CURLOPT_CUSTOMREQUEST", method];	
		];

		If[OptionValue["Username"] =!= "",
			CURLLink`CURLOption[handle, "CURLOPT_USERNAME", OptionValue["Username"]]
		];
		If[OptionValue["Password"] =!= "",
			CURLLink`CURLOption[handle, "CURLOPT_PASSWORD", OptionValue["Password"]]
		];
		Switch[optionValueCookies,
			Automatic, CURLLink`CURLAutoCookies[handle], 
			_, addCookies[handle, optionValueCookies]
		];
		If[OptionValue["Headers"] =!= {},
			addHeaders[handle, OptionValue["Headers"]]
		];


		
		
		If[MatchQ[parameters, {__}],
			If[method === "GET",
				finalURL  = url <> "?" <> buildData[handle, parameters, method],
				CURLLink`CURLOption[handle, "CURLOPT_COPYPOSTFIELDS", buildData[handle, parameters, method]]
			]
		];
		(* If the Parmeters are set then, we don't want to set the body. *)
		If[StringQ[OptionValue["Body"]] && ( parameters ==={} ) && (multipartElements==={}), 
			CURLLink`CURLOption[handle, "CURLOPT_COPYPOSTFIELDS", OptionValue["Body"]];
		];
		
		CURLLink`CURLCredentialsProvider[handle, ToString[OptionValue["CredentialsProvider"]]];

		(*Handles the old List cases of Multipart Requests*)
         If[MatchQ[multipartElements, {{_String, _String, {__Integer}}..}],
            CURLLink`CURLForm[handle,
                    #[[1]],
                    #[[2]],
                     "",
                    #[[3]],
                     Length[#[[3]]],
                     ""
                     ] & /@ multipartElements
            ];
         (*Handles a List of Rules of MutipartData*)
         Which[MatchQ[multipartElements, {Rule[{_String, _String}, _String]..}],
               CURLForm[handle,
                    #[[1]][[1]],
                    #[[1]][[2]],
                    "",
                    #[[2]],
                        Length[#[[2]]],
                        ""
                        ] & /@ ((Rule[#[[1]],ToCharacterCode[#[[2]]]])& /@ multipartElements)
               ,
               MatchQ[multipartElements, {Rule[{_String, _String|Automatic,___String}, {__Integer}|File[_String]|_String]..}],
               CURLForm[handle,
                        #[[1]][[1]],
                        #[[1]][[2]],
                        If[Length[#[[1]]]===3,#[[1]][[3]],""],
                        If[StringQ[#[[2]]],ToCharacterCode[#[[2]]],#[[2]]],
                        If[StringQ[#[[2]]],Length[ToCharacterCode[#[[2]]]],Length[#[[2]]]],
                        ""
                        ] & /@multipartElements
               ,
               MatchQ[multipartElements, {Rule[{_String, _String|Automatic}, File[_String]]..}],
               CURLLink`CURLForm[handle,
                        #[[1]][[1]],
                        #[[1]][[2]],
                        If[Length[#[[1]]]===3,#[[1]][[3]],""],
                        #[[2]],
                        Length[#[[2]]],
                        ""
                        ] & /@multipartElements
               
               ];

		(* If the Parmeters are set then, we don't want to set the body. *)
		If[MatchQ[OptionValue["Body"], {__Integer}|{}]&& ( parameters ==={}) && (multipartElements === {}) ,
			CURLLink`CURLOption[handle, "CURLOPT_POSTFIELDSIZE", Length[OptionValue["Body"]]];
			CURLLink`CURLOption[handle, "CURLOPT_COPYPOSTFIELDS", OptionValue["Body"]]
		];
			
		handle["URL"] = finalURL;
		CURLLink`CURLSetURL[handle, finalURL];
		CURLLink`CURLOption[handle, "CURLOPT_URL", finalURL];	
		
		baseURL = If[StringMatchQ[url, {"http://*", "https://*, ftp://*, ftps://*"}], 
			URIJoin[Flatten@{URISplit[url]}]
		(*else*), 
			URIJoin[Flatten@{URISplit["http://" <> url]}]
		];				
		handle["BaseURL"] = baseURL;
		CURLLink`CURLSetBaseURL[handle, baseURL];
	]
(*helper function: join  parameters to multipart elements *)
(*Since the syntax for parameters option does not allow for
 "content/type" we hard-code "text/plain" this is in accordance with rfc 2388.
 http://www.ietf.org/rfc/rfc2388.txt
 *)
appendParametersToMultipartElements[parameters_,me_]:=
Module[
	{keys,values,formattedParameters},
	keys=Keys[parameters];
	(*the Values[parameters] must be converted to bytes automatically
	  because the user gives these parameters as strings. Encoding for
	  single argument ToCharacterCode is Unicode, and we cannot use that.
	  
	  Hard-code UTF-8 as the character encoding. 
	  Reason:
	  "The first 128 characters of Unicode, 
	  which correspond one-to-one with ASCII, are encoded using a single octet 
	  with the same binary value as ASCII, 
	  making valid ASCII text valid UTF-8-encoded Unicode as well."
	  https://en.wikipedia.org/wiki/UTF-8
	 *)
	values=If[Head[#]===String,ToCharacterCode[#,"UTF-8"],#]&/@Values[parameters];
	(*check multipart-element pattern and format parameters accordingly*)
	Which[
		MatchQ[me,{{_String, _String, {__Integer}}..}],
		formattedParameters=MapThread[{#1,"text/plain; charset=\"utf-8\"",#2}&,{keys,values}]
		,
		MatchQ[me,{Rule[{_String, _String|Automatic,___String}, {__Integer}|_File]..}],
		formattedParameters=MapThread[Rule[{#1,"text/plain; charset=\"utf-8\""},#2]&,{keys,values}];
		];
	(*join multipart elements with parameters*)
	Return[me~Join~formattedParameters];
	]



(****************************************************************************)
(* helper functions for HTTP streams *)
streamInit[url_String, opts_List] :=
	Module[{stdOpts, error, handle},
		Quiet[
			stdOpts = FilterRules[Flatten[{opts, FilterRules[Options[URLFetch], Except[opts]]}], Except[BinaryFormat]];
			error = Catch[
				handle = commonInit[url, URLFetch, stdOpts];
				If[handle === $Failed,
					Return[$Failed]
				];
				
				If[TrueQ[$proxyCache],
					CURLLink`CURLProxyCache[handle];
				];
		
				setOutput[handle, "String"];
			,CURLLink`Utilities`Exception]
		];
		handle["OPTIONS"] = stdOpts;
		
		If[error === $Failed,
			$Failed
		(*else*),
			First[handle]
		]
	]
	
Options[streamCookies] = $StandardOptions
streamCookies[id_Integer] :=
	streamCookies[id, Sequence@@CURLLink`CURLHandle[id]["OPTIONS"]]

streamCookies[id_Integer, opts:OptionsPattern[]] :=
	Module[{error},
		Quiet[
			error = Catch[
				If[OptionValue["StoreCookies"] && OptionValue["Cookies"] =!= Automatic,
					storeCookies[HTTPData[CURLLink`CURLHandle[id], "Cookies"]]
				] 
			,CURLLink`Utilities`Exception]
		];
		
		If[error === $Failed,
			$Failed,
			True
		]
	]
	
streamStore[id_Integer] := 
	Module[{wellFormedURL, handle},
		handle = CURLLink`CURLHandle[id];
		wellFormedURL = If[StringMatchQ[handle["URL"], {"http://*", "https://*, ftp://*, ftps://*"}], 
			URIJoin[Flatten@{URISplit[handle["URL"]]}]
		(*else*), 
			URIJoin[Flatten@{URISplit["http://" <> handle["URL"]]}]
		];
		sessionStore[wellFormedURL] := False
	]
(****************************************************************************)
sessionStore[_] := False;

credWrapper[handle_CURLLink`CURLHandle, url_String, func_] :=
	credWrapper[First[handle], url, func]
	
credWrapper[id_Integer, url_String, func_] :=
	Module[{credProvider, wellFormedURL, defaultQ, handle = CURLLink`CURLHandle[id], res},
		defaultQ = func === Automatic; 
		credProvider = If[defaultQ,passwordDialog, func];
		wellFormedURL = If[StringMatchQ[url, {"http://*", "https://*, ftp://*, ftps://*"}], 
			URIJoin[Flatten@{URISplit[url]}]
		(*else*), 
			URIJoin[Flatten@{URISplit["http://" <> url]}]
		];
		

		If[defaultQ && sessionStore[wellFormedURL],
			CURLLink`CURLReset[handle];
			CURLLink`CURLSessionCache[handle, wellFormedURL];
			Return[True]
		];
		res = credProvider[url];
		Which[
			res === $Canceled,False,
			MatchQ[res, List[_String, _String]], 
				CURLLink`CURLReset[handle];
				If[defaultQ,
					sessionStore[wellFormedURL] := True;
					
					CURLLink`CURLStore[handle, wellFormedURL, First[res], Last[res]];
				(*else*),
					CURLLink`CURLOption[handle, "CURLOPT_USERNAME", First[res]];
					CURLLink`CURLOption[handle, "CURLOPT_PASSWORD", Last[res]];	
				];
				
				True,
				True,False	
		]
	]
	
$proxyCache = False;
proxyCredentials[id_Integer, url_String] :=
	proxyCredentials[CURLLink`CURLHandle[id], url]
	
proxyCredentials[handle_CURLLink`CURLHandle, url_String] :=	
	Module[{result},
		If[$proxyCache === True,
			CURLLink`CURLReset[handle];
			CURLLink`CURLProxyCache[handle];
			Return[True];	
		];
		
		result = proxyDialog[url];
		Which[
			result === $Canceled, False,
			MatchQ[result, List[_String, _String]],
				CURLLink`CURLReset[handle];
				CURLLink`CURLOption[handle, "CURLOPT_PROXYUSERNAME", First[result]];
				CURLLink`CURLOption[handle, "CURLOPT_PROXYPASSWORD", Last[result]];
				$proxyCache = True;
				True
		]
	]
	
(* Old default Wolfram System password dialog *)
If[!ValueQ[$allowDialogs], $allowDialogs = True]
hasFrontEnd[] := ToString[Head[$FrontEnd]] === "FrontEndObject"
$pwdDlgResult;

passwordDialogStandalone[prompt1_, prompt2_, prompt3_] :=
(
	Print[prompt1];
	Print[prompt2];
	Print[prompt3];
	{InputString["username: "], InputString["password (will echo as cleartext): "]}
)

passwordDialogFE[title_, prompt1_, prompt2_, prompt3_] :=
	Module[{cells, uname = "", pwd = "", createDialogResult},
		cells = {
			TextCell[prompt1, NotebookDefault, "DialogStyle", "ControlStyle"],
			TextCell[prompt2, NotebookDefault, "DialogStyle", "ControlStyle"],
			ExpressionCell[Grid[{ {TextCell["Username:  "], InputField[Dynamic[uname], String, ContinuousAction -> True, 
         		ImageSize -> 200, BoxID -> "UserNameField"]}, {TextCell["Password:  "], 
					InputField[Dynamic[pwd], String, ContinuousAction -> True, 
						ImageSize -> 200, FieldMasked -> True]}}], "DialogStyle", "ControlStyle"],
				TextCell[prompt3, NotebookDefault, "DialogStyle", "ControlStyle"],
                
				ExpressionCell[ Row[{DefaultButton[$pwdDlgResult = {uname, pwd}; 
					DialogReturn[], ImageSize -> Dynamic[CurrentValue["DefaultButtonSize"]]], Spacer[{2.5`, 42, 16}],
				CancelButton[$pwdDlgResult = $Canceled; DialogReturn[], 
					ImageSize -> Dynamic[CurrentValue["DefaultButtonSize"]]]}], TextAlignment -> Right] };
			createDialogResult = DialogInput[DialogNotebook[cells], 
				WindowTitle -> title, WindowSize -> {400, FitAll}, Evaluator -> CurrentValue["Evaluator"], 
				LineIndent -> 0, PrivateFontOptions -> {"OperatorSubstitution" -> False} ];
			If[createDialogResult === $Failed,
				Null,
			(* else *)
				MathLink`CallFrontEnd[FrontEnd`BoxReferenceFind[ FE`BoxReference[createDialogResult, {{"UserNameField"}}, 
					FE`BoxOffset -> {FE`BoxChild[1]}]]];
				$pwdDlgResult
			]
	]
	
coreDialog[url_String, prompt2_String] :=
	Module[{title, prompt1, prompt3},
	    title = "Authentication Required";
        Clear[$pwdDlgResult];
        Which[
            !TrueQ[$allowDialogs],
                Null,
            hasFrontEnd[],
                (* Use FE dialog box *)
                prompt1 = Row[{"You are attempting to read from the URL:\n", Hyperlink[url, BaseStyle -> "ControlStyle"]}];
                prompt3 = "(These values are kept for this session only.)";
                passwordDialogFE[title, prompt1, prompt2, prompt3],
            True,
                prompt1 = "You are attempting to read from the URL:\n" <> url;
                prompt3 = "(These values are kept for this session only.)";
                passwordDialogStandalone[prompt1, prompt2, prompt3]
        ]
	]
	
passwordDialog[url_String] := coreDialog[url, "The server is requesting authentication."]
proxyDialog[url_String] := coreDialog[url, "The proxy server is requesting authentication."]


(****************************************************************************)
$AsyncEnum = {
	"Progress" -> 0,
	"Transfer" -> 1	
}

callBackWrapper[obj_, "headers", data_] := {obj, "headers", Cases[StringSplit[StringSplit[FromCharacterCode[First[data]], "\r\n"], ": ", 2], {_, _}]}
callBackWrapper[obj_, "cookies", data_] := 
	{obj, "cookies",      	
		Cases[
			{	"Domain"-> First[#], 
				If[#[[2]] === "FALSE",
					"MachineAccess"-> #[[2]]
				],
				"Path"->#[[3]], 
				"Secure"->#[[4]], 
				"Expires"->DateString[ToExpression[#[[5]]] + AbsoluteTime[{1970, 1, 1, 0, 0, 0}]], 
				"Name"->#[[6]], 
				"Value"->Last[#]
			}, 
			Except[Null]] & /@ StringSplit[StringSplit[FromCharacterCode[First[data]], "\n"], "\t"]
	}
	
callBackWrapper[obj_, "credentials", data_] := 
	Module[{error, credProvider, handleID, url, output},
		Catch[error,
			handleID = data[[1]];
			url = data[[2]];
			credProvider = data[[3]];	
			CURLLink`CURLReset[CURLLink`CURLHandle[handleID]];
			output = ToExpression[credProvider][handleID, url];
			If[MatchQ[output, {_String, _String}],
				CURLLink`CURLOption[CURLLink`CURLHandle[handleID], "CURLOPT_USERNAME", output[[1]]];
				CURLLink`CURLOption[CURLLink`CURLHandle[handleID], "CURLOPT_PASSWORD", output[[2]]];
			];
			CURLLink`CURLSetCheckQ[CURLLink`CURLHandle[handleID], True];
		,CURLLink`Utilities`Exception];
		
		If[error === $Failed,
			{obj, "credentials", {False}}
		(*else*),
			{obj, "credentials", {True}} 
		]
	]
	
callBackWrapper[obj_, name_, data_] := {obj, name, data}



urlSubmitCallbackWrapper[obj_,"headers",data_,opts:OptionsPattern[URLFetchAsynchronous]]:=
Module[{headers},
	headers=impHeaders[Last[StringSplit[FromCharacterCode[First[data]],"\r\n\r\n"]]];
	{obj,"HeadersReceived",headers}
]

urlSubmitCallbackWrapper[obj_,"cookies",data_,opts:OptionsPattern[URLFetchAsynchronous]]:=
Module[
	{cookiesreceived,cookiefunction},
	cookiesreceived=Complement[CURLLink`Cookies`Private`cookiesToAssociation[FromCharacterCode[First[data]]],CURLLink`Cookies`Private`cookiesToAssociation[$LastKnownCookies]];
	cookiefunction=OptionValue[CookieFunction];
	Which[
		cookiefunction===Automatic,
		SetCookies[cookiesreceived];
		,
		cookiefunction===None,
		ClearCookies[cookiesreceived];
		,
		True,
		Map[cookiefunction,cookiesreceived];
	
	];
	{obj,"CookiesReceived",cookiesreceived}
]

urlSubmitCallbackWrapper[obj_, event_, data_,opts:OptionsPattern[URLFetchAsynchronous]] := {obj, event, data}


(****************************************************************************)
Options[URLFetchAsynchronous] = Join[FilterRules[$StandardOptions,Except["DisplayProxyDialog"]], {"DisplayProxyDialog"->False,"Progress"->False, "Transfer"->Automatic, "UserData"->None,"Events"->Automatic}];

URLFetchAsynchronous[urlExp_, func:Except[_Rule|_RuleDelayed|_String], options___?OptionQ] /; deprecatedOptionQ[options] := 
	URLFetchAsynchronous[urlExp, func, deprecatedOptionFix[URLFetchAsynchronous, options]] 

URLFetchAsynchronous[urlExp_/;isURL[urlExp,URLFetchAsynchronous], func:Except[_Rule|_RuleDelayed|_String], opts:OptionsPattern[]] /; InitializeQ[] := 
	Module[{handle, stdOpts, error, oauth, token, args, output,url},
		url=getURL[urlExp];
		If[OptionValue["DisplayProxyDialog"],
			URLFetch[url,{"StatusCode","ContentData"},"Method"->"HEAD"];
		];
		$LastKnownCookies=CURLLink`Cookies`GetKnownCookies[];
		If[OptionValue["OAuthAuthentication"] =!= None,
			oauth = OptionValue["OAuthAuthentication"];
			token = If[Head[oauth] === OAuthSigning`OAuthToken, oauth, OAuthSigning`OAuthAuthentication[oauth]];
			stdOpts = FilterRules[Flatten[{opts}], Except["OAuthAuthentication"]];
			args = OAuthSigning`OAuthSignURL[url, Join[stdOpts, {"CredentialsProvider" -> None, "OAuthAuthentication" -> token}]]; 
			Return[URLFetchAsynchronous @@ {First[args], func, Rest[args]}]
		];
		stdOpts = Flatten[{opts, FilterRules[Options[URLFetchAsynchronous], Except[{opts}]]}];	
		error = Catch[
			(* handle is freed in c code *)
			handle = commonInit[url, URLFetchAsynchronous, stdOpts];
			If[handle === $Failed,
				Return[$Failed]
			];
		
			CURLLink`CURLSetAsync[handle, True];
			setOutput[handle, "String"];
		
			If[OptionValue["StoreCookies"] && (OptionValue["Cookies"] =!= Automatic),
				CURLLink`CURLAsyncCookies[handle, True]
			]; 
		
			(* Set which async events will be raised. *)
			CURLLink`CURLAsyncOption[handle, "Progress" /. $AsyncEnum, OptionValue["Progress"]];
			Switch[OptionValue["Transfer"],
				Automatic, CURLLink`CURLAsyncOption[handle, "Transfer" /. $AsyncEnum, True];,
				"Chunks", CURLLink`CURLAsyncOption[handle, "Transfer" /. $AsyncEnum, False];
			];
		,CURLLink`Utilities`Exception];
		output = If[error === $Failed,
			$Failed
		(*else*),
			Internal`CreateAsynchronousTask[
				CURLLink`Private`curlAsyncObj, {First@handle}, 
				CallbackFunction[func,OptionValue["Events"],#1,#2,#3,opts]&,
				"TaskDetail"->url, 
				"UserData"->OptionValue["UserData"]]
		];
		unsetCURLHandle[handle];
		output
	]
	
CallbackFunction[userfunc_,events_,obj_,event_,data_,opts:OptionsPattern[URLFetchAsynchronous]]:=Module[{},
Which[
	events===Full,
	userfunc[Sequence@@urlSubmitCallbackWrapper[obj,event,data,opts]],
	True,
	userfunc[Sequence@@callBackWrapper[obj,event,data]]
	]
]	

(****************************************************************************)
Options[URLSaveAsynchronous] = Join[FilterRules[$StandardOptions,Except["DisplayProxyDialog"]], {"DisplayProxyDialog"->False,"Progress"->False, BinaryFormat->True, "UserData"->None}]
URLSaveAsynchronous[urlExp_, func:Except[_Rule|_RuleDelayed|_String], options___?OptionQ] := 
	URLSaveAsynchronous[urlExp, Automatic, options]

URLSaveAsynchronous[urlExp_, Automatic|None|Null, rest___] := 
	URLSaveAsynchronous[urlExp, FileNameJoin[{$TemporaryDirectory, CreateUUID[] <> ".tmp"}], rest]

URLSaveAsynchronous[urlExp_, file_, func:Except[_Rule|_RuleDelayed|_String], options___?OptionQ] /; deprecatedOptionQ[options] := 
	URLSaveAsynchronous[urlExp, file, func, deprecatedOptionFix[URLSaveAsynchronous, options]] 

URLSaveAsynchronous[urlExp_/;isURL[urlExp,URLSaveAsynchronous], fileExp_/;isFile[fileExp,URLSaveAsynchronous], func:Except[_Rule|_RuleDelayed|_String], opts:OptionsPattern[]] /; InitializeQ[] := 
	Module[{handle, stdOpts,file, error, oauth, token, args, output,url},
		url=getURL[urlExp];
		file=getFile[fileExp];
		$LastKnownCookies=CURLLink`Cookies`GetKnownCookies[];
		If[OptionValue["DisplayProxyDialog"],
			URLFetch[url,{"StatusCode","ContentData"},"Method"->"HEAD"];
		];
		If[OptionValue["OAuthAuthentication"] =!= None,
			oauth = OptionValue["OAuthAuthentication"];
			token = If[Head[oauth] === OAuthSigning`OAuthToken, oauth, OAuthSigning`OAuthAuthentication[oauth]];
			stdOpts = FilterRules[Flatten[{opts}], Except["OAuthAuthentication"]];
			args = OAuthSigning`OAuthSignURL[url, Join[stdOpts, {"CredentialsProvider" -> None, "OAuthAuthentication" -> token}]]; 
			Return[URLSaveAsynchronous @@ {First[args], file, func, Rest[args]}]
		];
		stdOpts = Flatten[{opts, FilterRules[Options[URLSaveAsynchronous], Except[{opts}]]}];
		error = Catch[
			(* handle is freed in c code *)
			handle = commonInit[url, URLSaveAsynchronous, stdOpts];
			If[handle === $Failed,
				Return[$Failed]
			];
		
			CURLLink`CURLSetAsync[handle, True];
			setOutput[handle, "File", ExpandFileName[file], OptionValue[BinaryFormat]];
		
			If[OptionValue["StoreCookies"] && (OptionValue["Cookies"] =!= Automatic),
				CURLLink`CURLAsyncCookies[handle, True]
			]; 
		
			(* Set which async events will be raised. *)
			CURLLink`CURLAsyncOption[handle, "Progress" /. $AsyncEnum, OptionValue["Progress"]];
		,CURLLink`Utilities`Exception];
		output = If[error === $Failed,
			$Failed
		(*else*),
			Internal`CreateAsynchronousTask[
				CURLLink`Private`curlAsyncObj, {First@handle}, 
				func[Sequence@@callBackWrapper[##]] &, 
				"TaskDetail"->url, 
				"UserData"->OptionValue["UserData"]]
		];
		unsetCURLHandle[handle];
		output
	]
(*Helper Functions*)
getNewHandle[url_,func_,file_,opts:OptionsPattern[URLSave]]:=Module[
	{handle},
	(*initialize multi handle*)
	handle = commonInit[url, func, opts];
				
	(*Throw an error, in case handle cannot be initialized*)
	If[handle === $Failed,Return[$Failed]];
			
	(*output should be held in memory*)
	If[func===URLFetch,setOutput[handle, "String"]];
	(*output should be held in a file*)
	If[func===URLSave,setOutput[handle, "File", ExpandFileName[file],OptionValue[BinaryFormat]];];
	handle
]
getResponseCodes[handle_]:=Module[
	{stream,statusCode,connectCode},

	(*get the stream*)					
	stream=HTTPData[handle,"Stream"];
	(*
	read one byte, this is necessary hack
	to get proper status code
	*)
	Read[stream,Byte];

	(*reset stream position to zero*)
	SetStreamPosition[stream,0];

	(*get status code*)
	statusCode=CURLLink`CURLStatusCode[handle];
	connectCode=CURLLink`CURLHTTPConnectCode[handle];
	
	{stream,statusCode,connectCode,handle["Return"]}
					
	]
retryIfSSLError[ihandle_,url_,func_,file_,proxy_,opts___]:=
Module[{sslConnectError=35,handle=ihandle,SSLVersion=5,noRevoke=2(*CURLSSLOPT_NO_REVOKE*)},
	While[MatchQ[handle["Return"],sslConnectError|56],

			CURLLink`CURLHandleUnload[handle];
			handle=getNewHandle[url,func,None,opts];
			(*CURLLink`CURLOption[handle, "CURLOPT_SSL_OPTIONS", noRevoke];*)
			CURLLink`CURLOption[handle, "CURLOPT_SSLVERSION",SSLVersion];
			If[StringQ[proxy],proxyCredentials[handle, url];CURLLink`CURLOption[handle, "CURLOPT_PROXY", proxy]];
			handle=CURLLink`CURLMultiHandleAdd[handle,{handle}];
			handle["Return"]=CURLLink`CURLPerform[handle];
			If[SSLVersion<=2,Break[]];
			SSLVersion--;
	];
		handle	

]

(****************************************************************************)
Initialize[] := Initialize[] = 
	Catch[	
		CURLLink`CURLInitialize[];
		CURLLink`CURLSetCert[$CACERT];
		System`$CookieStore;
		CURLLink`Cookies`LoadPersistentCookies[System`$CookieStore];
	,CURLLink`Utilities`Exception] =!= $Failed

InitializeQ[] := Initialize[];
	
(****************************************************************************)
(* List of all possible output types *)
$URLFetchElements = {
	"Content",
	"ContentData",
	"Headers",
	"Cookies",
	"StatusCode",
	"Stream",
	"CookiesReceived",
	"HeadersReceived"
}

$FTPFetchElements = {
	"Content",
	"ContentData",
	"StatusCode"
}

$URLSaveElements = {
	"Headers",
	"Cookies",
	"StatusCode",
	"CookiesReceived",
	"HeadersReceived"	
}

$FTPSaveElements = {
	"StatusCode"
};

(****************************************************************************)
errorQ[obj_CURLLink`CURLHandle] := obj["Return"] === 0

(****************************************************************************)
End[] (* End Private Context *)
EndPackage[]
