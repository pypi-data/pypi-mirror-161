(* Mathematica Package *)

BeginPackage["CURLLink`",{"PacletManager`"}]

(* Exported symbols added here with SymbolName::usage *)  
CURLMultiHandleInit
CURLMultiHandleAdd
CURLMultiHandleRemove
CURLHTTPConnectCodes
CURLInitialize::usage = "CURLInitialize[size] initializes internal hashtables of size size."
CURLStatusCodes
CURLHandleLoad::usage = "CURLHandleLoad	create a new CURLHandle."
CURLReset::usage = "CURLReset reset a CURLHandle."
CURLHandle::usage = "CURLHandle	"
CURLMultiHandle::usage = "Adds an easy handle to multi handle"
CURLMultiPerform::usage = "Adds an easy handle to multi handle"
CURLSetURL::usage = "CURLSetURL[hdl, url] set the actual URL used for the connection."
CURLSetBaseURL::usage = "CURLSetBaseURL[hdl, url] set the base URL used for the connection."
CURLCredentialsProvider::usage = "CURLCredentialsProvider[hdl, url] set the callback function for credentials."
CURLStore::usage = "CURLStore[hdl, session] store session information."
CURLSessionCache::usage = "CURLSessionCache[hdl, url] check cache for session information."
CURLProxyCache::usage = "CURLProxyCache[hdl] use cached proxy information for a handle."
CURLSetCheckQ::usage = "CURLSetCheckQ[hdl, True|False] flag if credentials have been set."

CURLCookies::usage = "CURLCookies[hdl] get a list of cookies used by a handle."
CURLCerts::usage = "CURLCerts[hdl] get certificate information from a handle."
CURLSetCert::usage = "CURLSetCert[cert] store the cerficite file in global memory, for use by the stream handler."
CURLSetProxies::usage = "CURLSetProxies[hdl, proxies] set a list of proxies to be used by streams and async handles."
CURLGetProxies::usage = "CURLGetProxies[url] get valie proxies for OS."
CURLAutoCookies::usage = "CURLAutoCookies[hdl] if called, cookies will be shared/handled automatically."
CURLFileInfo::usage = "CURLFileInfo[hdl, name] store filename to be used to store contents of connection."
CURLWriteInfo::usage = "CURLWriteInfo[hdl, name] store function name to be used for user defined write function."

CURLHandleUnload::usage = "CURLHandleUnload[handle]	free a CURLHandle from memory"

CURLHeaderData::usage = "CURLHeaderData[handle] get headers after CURLPerform that is stored in memory (proper CURLOptions must be set)."
CURLStatusCode::usage = "CURLStatusCode[handle] get the status code after the connection has competed."
CURLHTTPConnectCode::usage = "CURLHTTPConnectCode[handle] get the  HTTP proxy response code to a CONNECT request"
CURLRawContentData::usage = "CURLRawContentData[handle] get raw data as an array of bytes."

CURLOption::usage = "CURLOption[handle, option, value] set a handle option to value."

CURLEscape::usage = "CURLEscape[handle, url] url encodes a string."
CURLUnescape::usage = "CURLUnescape[handle, url] url decodes a string."

CURLPerform::usage = "CURLPerform[handle] perform actions with a CURLHandle."
CURLPerformNoBlock::usage = "CURLPerform[handle] perform actions with a CURLHandle."
CURLForm::usage = "CURLForm[...] set multi-form POST data."
CURLError::usage = "CURLError[cc] get error string for given CURLcode cc."

CURLAddHeader::usage = "CURLAddHeader[handle, header] add a custom header to an CURLHandle."
CURLSetAsync::usage = "CURLSetAsync[handle, value] set if a CURLHandle is to be asynchronous. "
CURLAsyncOption::usage = "CURLAsyncOpiton[handle, opt, val] set async events to be rasied."
CURLAsyncCookies::usage = "CURLAsyncCookies[handle, val] set a flag to inform the async connection to manually store cookies."

CURLLink`$CURLOptions::usage = "$CURLOptions list containing all available options for CURLOption."
CURLLink`CURLOptionQ::usage = "CURLOptionQ[opt] returns True if a valid CURL option."


(*HTTP*)

(*FTP*)
CURLLink`FTPObject::usage=""
CURLLink`FTPConnect::usage=""
CURLLink`FTPExecute::usage=""
CURLLink`FTPExecuteAsynchronous::usage=""


(*IMAP*)
CURLLink`IMAPbject::usage=""
CURLLink`IMAPConnect::usage=""
CURLLink`IMAPExecute::usage=""
CURLLink`IMAPExecuteAsynchronous::usage=""


Begin["`Private`"] (* Begin Private Context *) 


(****************************************************************************)

(* Supported option types that may be sent to LibraryLink functions *)
$CURLOptionTypes = {
	"Integer",
	"String",
	"CallbackPointer",	
	"FilePointer",
	"MemoryPointer",
	"Tensor"
}

(* Enumerate the option types to match the LibraryLink enum values *)
Do[
	opTypes[$CURLOptionTypes[[ii]]] = ii - 1,
	{ii, Length[$CURLOptionTypes]}
]

(* Different types of callback functions that HTTPClient supports *)
$CURLCallbacks = {
	"WRITE_MEMORY",
	"WRITE_FILE",
	"WRITE_USER"
}

(* Enumerate the callback functions to match LibraryLink enum values *)
Do[
	callbackEnum[$CURLCallbacks[[ii]]] = ii - 1;
	curlCallbackQ[$CURLCallbacks[[ii]]] := True,
	{ii, Length[$CURLCallbacks]}
]

curlCallbackQ[_] := False

(****************************************************************************)
(* Load the required dynamic libraries *)

$LibraryResourcesPath =
	FileNameJoin[{
		If[TrueQ[Developer`$ProtectedMode] && $VersionNumber < 10.2,
		    (* This branch is a fix for bug 294005. *)
		    FileNameJoin[{$InstallationDirectory, "SystemFiles", "Links", "CURLLink"}],
		(* else *)
            DirectoryName[System`Private`$InputFileName]
		],
		"LibraryResources",
		$SystemID
	}]

If[FreeQ[$LibraryPath, $LibraryResourcesPath],
	PrependTo[$LibraryPath, $LibraryResourcesPath]
]

newPath={FileNameJoin[Most[FileNameSplit[$InputFileName]]~Join~{"LibraryResources"}~Join~{$SystemID}],FileNameJoin[{$InstallationDirectory,"SystemFiles","Libraries",$SystemID}]};
Block[{$LibraryPath = newPath},
 		If[ValueQ[$librariesLoadedQ]===False || $librariesLoadedQ===False,
 			Check[
 				(*expr*)
 				$CURLLinkLibrary=FindLibrary["libcurllink"];
 				Which[
					$OperatingSystem === "Windows",
						LibraryLoad[FindLibrary["libeay32"]];
						LibraryLoad[FindLibrary["ssleay32"]];
						LibraryLoad[FindLibrary["libssh2"]];
						LibraryLoad[FindLibrary["libcurl"]];
						$librariesLoadedQ=True;,
					True,								
						$librariesLoadedQ=True;
					 ];
				 ,
				(*failure expr*)
				$librariesLoadedQ=False;
				 ]
 			]
		]

(****************************************************************************)
(* Load all the functions required by HTTPClient *)
initialize[] := initialize[] =
(
	If[!StringQ[$CURLLinkLibrary] || !FileExistsQ[$CURLLinkLibrary],
		Throw[$Failed,CURLLink`Utilities`Exception]
	];
	
	If[$VersionNumber < 9,
		Throw[$Failed,CURLLink`Utilities`Exception]
	];
	
	Check[	
		

		curlInitialize = LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_initialize", {_Integer}, "Void"];
		handleLoad = LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_createHandle", {}, _Integer];
		handleReset = LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_resetHandle", {_Integer}, _Integer];
		getCookies = LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_getCookies", {_Integer}, "UTF8String"];
		handleUnload = LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_cleanup", {_Integer}, "Void"];
		getHeaders = LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_getHeaders", {_Integer}, "UTF8String"];
		getStatusCode = LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_getStatusCode", {_Integer}, _Integer];
		getHTTPConnectCode = LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_getHTTPConnectCode", {_Integer}, _Integer];
		getRawContent = LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_getRawContent", {_Integer}, {_Integer, 1, "Automatic"}];
		curlOptionString = LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_optionString", {_Integer, _Integer, "UTF8String"}, _Integer];
		curlOptionTensor = LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_optionTensor", {_Integer, _Integer, {_Integer, 1, "Shared"}}, _Integer];
		curlOptionInteger = LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_optionInteger", {_Integer,_Integer, _Integer, _Integer}, _Integer];
		curlEscape = LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_escape", {"UTF8String"}, "UTF8String"];
		curlUnescape = LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_unescape", {"UTF8String"}, "UTF8String"];
		curlPerformnoblock = LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_perform_noblock", {_Integer}, _Integer];
		curlPerform = LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_perform", {_Integer}, _Integer];
		curlMultiPerform=LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_multiperform", {_Integer}, _Integer];
		curlMultiPerformNoBlock=LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_multiperform_noblock", {_Integer}, _Integer];
		curlMultiAdd=LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_multiadd", {_Integer,_Integer}, _Integer];
		curlMultiRemove=LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_multiremove", {_Integer,_Integer}, _Integer];
		curlAddHeader = LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_addHeader", {_Integer, "UTF8String"}, _Integer];
		curlMultiForm = LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_multiPartForm", {_Integer, "UTF8String", "UTF8String","UTF8String","UTF8String", {_Integer, 1, "Shared"}, _Integer, "UTF8String"}, _Integer];
		curlError = LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_errorStr", {_Integer}, "UTF8String"];
		curlGetProxies = LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_getProxies", {"UTF8String"}, "UTF8String"];
		curlSetProxies = LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_setProxies", {_Integer, "UTF8String"}, "Void"];
		curlSetURL = LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_setURL", {_Integer, "UTF8String"}, "Void"];
		curlSetBaseURL = LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_setBaseURL", {_Integer, "UTF8String"}, "Void"];
		curlCredentialsProvider = LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_setCredentialsProvider", {_Integer, "UTF8String"}, "Void"];
		curlSessionStore = LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_sessionStore", {_Integer, "UTF8String", "UTF8String", "UTF8String"}, "Void"];
		curlSessionCache = LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_sessionCache", {_Integer, "UTF8String"}, "Void"];
		curlProxyCache = LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_proxyCache", {_Integer}, "Void"];
		curlSetCheckQ = LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_curlSetCheckQ", {_Integer, True|False}, "Void"];
		curlSetCert = LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_setCert", {"UTF8String"}, "Void"];
		curlAutoCookies = LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_autoCookies", {_Integer}, _Integer];
		curlFileInfo = LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_setFileInfo", {_Integer, "UTF8String", True|False}, "Void"];
		curlWriteInfo = LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_setWriteFunction", {_Integer, "UTF8String"}, "Void"];
		curlSetAsync = LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_setAsync", {_Integer, True|False}, "Void"];
		curlAsyncObj = LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_async_perform", {_Integer}, _Integer];
		curlAsyncOption = LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_setAsyncOption", {_Integer, _Integer, True|False}, "Void"];
		curlAsyncCookies = LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_asyncCookies", {_Integer, True|False}, "Void"];
				(*ftp functions*)

		curlGetTaskData				 = LibraryFunctionLoad[$CURLLinkLibrary, "wl_getTaskData", {_Integer,_Integer},{_Integer, 1, "Automatic"}];
		curlWaitOnAllTasks			 = LibraryFunctionLoad[$CURLLinkLibrary, "wl_waitOnAllTasks", {_Integer},_Integer];
		curlPushTask				 = LibraryFunctionLoad[$CURLLinkLibrary, "wl_pushTask", {_Integer,_Integer,"UTF8String","UTF8String",{_Integer, 1, "Shared"},True|False},_Integer];
		curlftpConnect				 = LibraryFunctionLoad[$CURLLinkLibrary,"wl_ftpConnect",{_Integer,"UTF8String","UTF8String","UTF8String",_Integer,"UTF8String"},Integer];
		curlftpDisconnect			 = LibraryFunctionLoad[$CURLLinkLibrary,"wl_ftpDisconnect",{_Integer},_Integer];
		curlTaskCompleteQ			 = LibraryFunctionLoad[$CURLLinkLibrary,"wl_taskCompleteQ",{_Integer,_Integer},True|False];
		
		cSuccessQ = LibraryFunctionLoad[$CURLLinkLibrary, "curlLink_successQ", {}, True|False],
		
		Throw[$Failed,CURLLink`Utilities`Exception]
	]
)

initializedQ := Catch[initialize[]] =!= $Failed

successQ := cSuccessQ[]
Developer`RegisterInputStream["HTTPStreamElement", StringMatchQ[#, "HTTPStreamElement"] &,Null];

(****************************************************************************)

(* 
	CURLInitialize[] sets up the LibraryLink data structures needed to use
	HTTPClient.
*)   
CURLInitialize[] := CURLInitialize[5] (* this should be plenty for the average user (famous last words) *)

CURLInitialize[hashSize_Integer] /; initializedQ :=
	(
		curlInitialize[hashSize];
		If[!successQ, Throw[$Failed,CURLLink`Utilities`Exception]]
	)
	
(****************************************************************************)
(* Add a curlHandle_t to the HTTPClient hash table *)
CURLHandleLoad[] /; initializedQ :=
	Module[{id},
		id = handleLoad[];
		If[successQ, CURLHandle[id], Throw[$Failed,CURLLink`Utilities`Exception]]
	]
	
CURLHandle /: Format[CURLHandle[id_Integer], StandardForm] :=
	CURLHandle["<" <> ToString[id] <> ">"] 
   
(****************************************************************************)
(* 
	Remove a curlHandle_t from HTTPClient hash table, and free
	all memory associated with the handle.
*)
CURLHandleUnload[easyhandles_List] /; initializedQ :=
	Map[CURLHandleUnload[#]&,easyhandles]
CURLHandleUnload[CURLHandle[id_Integer]] /; initializedQ :=
	(
		handleUnload[id];	
		If[!successQ, Throw[$Failed,CURLLink`Utilities`Exception]]
	)
	
(****************************************************************************)
(* 
	Set the final URL used for the connection.
*)
CURLSetURL[CURLHandle[id_Integer], url_String] /; initializedQ :=
	(
		curlSetURL[id, url];	
		If[!successQ, Throw[$Failed,CURLLink`Utilities`Exception]]
	)
	
(****************************************************************************)
(* 
	Set the base URL used for the connection.
*)
CURLSetBaseURL[CURLHandle[id_Integer], url_String] /; initializedQ :=
	(
		curlSetBaseURL[id, url];	
		If[!successQ, Throw[$Failed,CURLLink`Utilities`Exception]]
	)
	
(****************************************************************************)
(* 
	Set callback function for providing credentials.
*)
CURLCredentialsProvider[CURLHandle[id_Integer], credentials_String] /; initializedQ :=
	(
		curlCredentialsProvider[id, credentials];	
		If[!successQ, Throw[$Failed,CURLLink`Utilities`Exception]]
	)
	
(****************************************************************************)
(* 
	Store session information.
*)

CURLStore[CURLHandle[id_Integer], url_String, user_String, pass_String] /; initializedQ :=
	(
		curlSessionStore[id, url, user, pass];
		If[!successQ, Throw[$Failed,CURLLink`Utilities`Exception]]
	)
	
(****************************************************************************)
(* 
	Check cache for session	information.
*)
CURLSessionCache[CURLHandle[id_Integer], url_String] /; initializedQ :=
	(
		curlSessionCache[id, url];
		If[!successQ, Throw[$Failed,CURLLink`Utilities`Exception]]
	)
	
(****************************************************************************)
(* 
	Check cache for proxy information.
*)
CURLProxyCache[CURLHandle[id_Integer]] /; initializedQ :=
	(
		curlProxyCache[id];
		If[!successQ, Throw[$Failed,CURLLink`Utilities`Exception]]
	)
	
(****************************************************************************)
(* 
	Set credentials flag.
*)
CURLSetCheckQ[CURLHandle[id_Integer], flag:(True|False)] /; initializedQ :=
	(
		curlSetCheckQ[id, flag];
		If[!successQ, Throw[$Failed,CURLLink`Utilities`Exception]]
	)
	
(****************************************************************************)
(* 
	Get the cookies received from a CURLHandl]e, the cookies will
	be returned as a single string with '\n' seperating the cookies.
*)
CURLCookies[CURLHandle[id_Integer]] /; initializedQ :=
	Module[{str},
		str = getCookies[id];
		If[successQ, str, Throw[$Failed,CURLLink`Utilities`Exception]]	
	]
	
(****************************************************************************)
(* 
	Get the contents of the headers received from a CURLHandle,
	note that this will include the HTTP status code as well.
*)
CURLHeaderData[CURLHandle[id_Integer]] /; initializedQ :=
	Module[{str},
		str = getHeaders[id];
		If[successQ, str, Throw[$Failed,CURLLink`Utilities`Exception]]	
	]
	
(****************************************************************************)
(* 
	Reset a CURLHandle to its default state.
*)
CURLReset[CURLHandle[id_Integer]] /; initializedQ :=
	Module[{},
		handleReset[id];
		If[!successQ, Throw[$Failed,CURLLink`Utilities`Exception]]	
	]

(****************************************************************************)
(* 
	Get the status code returned from the CURLHandle,
*)
CURLStatusCode[CURLHandle[id_Integer]] /; initializedQ :=
	Module[{code},
		code = getStatusCode[id];
		If[successQ, code, Throw[$Failed,CURLLink`Utilities`Exception]]	
	]
CURLStatusCodes[easyhandles_List]:=Map[#->CURLStatusCode[#]&,easyhandles]
(****************************************************************************)
(* 
	Get the HTTP Connect Code returned from the CURLHandle,
*)
CURLHTTPConnectCode[CURLHandle[id_Integer]] /; initializedQ :=
	Module[{code},
		code = getHTTPConnectCode[id];
		If[successQ, code, Throw[$Failed,CURLLink`Utilities`Exception]]	
	]
CURLHTTPConnectCodes[easyhandles_List]:=Map[#->CURLHTTPConnectCode[#]&,easyhandles]
(****************************************************************************)
(* Returns the content of CURLHandle as a list of bytes. *)
CURLRawContentData[CURLHandle[id_Integer]] /; initializedQ :=
	Module[{lst},
		lst = getRawContent[id];
		If[successQ, lst, Throw[$Failed,CURLLink`Utilities`Exception]]	
	]

(****************************************************************************)
(* Connect to an HTTP server and gather content/headers *)
Options[CURLPerform]={"Blocking"->True}
CURLPerform[CURLHandle[id_Integer],opts:OptionsPattern[]] /; initializedQ :=
	Module[{cc},
		
		If[OptionValue["Blocking"],cc = curlPerform[id],cc = curlPerformnoblock[id]];
		
		If[successQ, cc, Throw[$Failed,CURLLink`Utilities`Exception]]
	]

(******************************************************************************)
(*curl-retry*)
(*
This function is a work around, for a bug in windows schannel see bug#308724 for details.
When TLSv1.2 gives ssl connect error, we set a lower ssl version, and keep trying.
SSLVersions:CURL_SSLVERSION_TLSv1_1 (5),CURL_SSLVERSION_TLSv1_0 (4),CURL_SSLVERSION_SSLv3 (3),CURL_SSLVERSION_SSLv2 (2)
*)
CURLRetry[CURLHandle[id_Integer]] /; initializedQ :=
	Module[
		{cc,SSLVersion=5,noError=0,noRevoke=2(*CURLSSLOPT_NO_REVOKE*)},
		CURLLink`CURLOption[CURLHandle[id], "CURLOPT_SSL_OPTIONS", noRevoke];
		While[SSLVersion >= 2,
		CURLLink`CURLOption[CURLHandle[id], "CURLOPT_SSLVERSION",SSLVersion];
		cc=curlPerform[id];
		If[cc==noError,
			(*then*)
			Break[]
			];
		SSLVersion--;
	];
	cc
	]
(******************************************************************************)
(*
	This will get a list of possible proxies valid for a url.
*)
CURLGetProxies[url_String] /; initializedQ :=
	Module[{str},
		str = curlGetProxies[url];
		If[successQ, str, Throw[$Failed,CURLLink`Utilities`Exception]]
	]

(******************************************************************************)
(*
	This will set an internal list of possible proxies, for streams and async handles..
*)
CURLSetProxies[CURLHandle[id_Integer], proxies_String] /; initializedQ :=
	Module[{},
		curlSetProxies[id, proxies];
		If[!successQ, Throw[$Failed,CURLLink`Utilities`Exception]]
	]

(******************************************************************************)
(* 
	Use Global Cookie share.
*)
CURLAutoCookies[CURLHandle[id_Integer]] /; initializedQ :=
	Module[{cc},
		cc = curlAutoCookies[id];
		If[successQ, cc, Throw[$Failed,CURLLink`Utilities`Exception]]
	]
	
(******************************************************************************)
(*
	If output is to be saved to a file, this function must be used to specify 
	the filename, as well as cause some triggers to tell libcurlLink what is 
	going on.
*)
CURLFileInfo[CURLHandle[id_Integer], fileName_String, format:(True|False)] /; initializedQ :=
	(
		curlFileInfo[id, fileName, format];
		If[!successQ, Throw[$Failed,CURLLink`Utilities`Exception]]
	)
(******************************************************************************)
CURLWriteInfo[CURLHandle[id_Integer], function_String] /; initializedQ :=
	(
		curlWriteInfo[id, function];
		If[!successQ, Throw[$Failed,CURLLink`Utilities`Exception]]
	)

(******************************************************************************)

CURLSetCert[cert_String] /; initializedQ :=
	(
		curlSetCert[cert];
		If[!successQ, Throw[$Failed,CURLLink`Utilities`Exception]];
	)
(****************************************************************************)
(* 
	upload multi-form post data.
*)

 CURLForm[CURLHandle[id_Integer], name_String, type:(_String|Automatic),fln:(_String|Automatic), udata:(_List|File[_String]), ln_Integer, headers_String] /; initializedQ :=
	Module[
{cc,mimetype,filepath,filename,data,length},
           Which[
                 fln===Automatic,
                 filename="Automatic";
                 ,
                 fln==="",
                 filename="";
                 ,
                 True,
                 filename=fln
                 
                 ];
           If[Head[udata]===File,
              
              filepath=udata[[1]];
              data={0};
              length=0;
              ,
              filepath="";
              data=udata;
              length=ln;
              ];
           
           If[!StringQ[type],mimetype="",mimetype=type];

           cc = curlMultiForm[id, name, mimetype,filename,filepath, Developer`ToPackedArray[data], length, headers];

              
		If[successQ, cc, Throw[$Failed,CURLLink`Utilities`Exception]]
	]
	
(****************************************************************************)
(* 
	Get a human readable error message from libcurl indicating 
	what went wrong during the connection (if anything).
*)
CURLError[cc_Integer] /; initializedQ :=
	Module[{str}, str = curlError[cc];	If[successQ, str, Throw[$Failed,CURLLink`Utilities`Exception]]]

(****************************************************************************)

(* URL Encode a String *)
CURLEscape[url_String] /; initializedQ :=
	Module[{str},
		str = curlEscape[url];	
		If[successQ, str, Throw[$Failed,CURLLink`Utilities`Exception]]
	]
	
(****************************************************************************)

(* URL Decode a String *)
CURLUnescape[url_String] /; initializedQ :=
	Module[{str},
		str = curlUnescape[url];	
		If[successQ, str, Throw[$Failed,CURLLink`Utilities`Exception]]
	]

(****************************************************************************)
(* 
	The following functions pass different options to curl_easy_setopt().  
	Since curl_easy_setopt is a macro designed to take several different 
	types of parameters, including kinds that are not easily passed from 
	Mathematica to a LibraryLink function (function pointers) care must 
	be taken to ensure HTTPClient's c code can interpert these properly.
	
	Note: the order in which these are defined is important.
*)

(* Most basic type of option.  To be used when the option takes an integer value *)

CURLOption[CURLHandle[id_Integer], option_?CURLLink`CURLOptionQ, param_Integer] /; initializedQ :=
	Module[{cc},
		cc = curlOptionInteger[id, Replace[option, CURLLink`$CURLOptions], opTypes["Integer"], param];
		If[cc =!= 0 || !successQ, 
			Throw[$Failed,CURLLink`Utilities`Exception]
		];
	]
	
(* Option to set the address where the data downloaded is to be stored. *)
CURLOption[CURLHandle[id_Integer], option:("CURLOPT_WRITEDATA"|"CURLOPT_WRITEHEADER"), opType_String] /; initializedQ := 
	Module[{cc},
		cc = curlOptionInteger[id, Replace[option, CURLLink`$CURLOptions], opTypes[opType], 0];
		If[cc =!= 0 || !successQ, 
			Throw[$Failed,CURLLink`Utilities`Exception]
		];
	]

(* Set various callback functions for libcurl *)
CURLOption[CURLHandle[id_Integer], option_?CURLLink`CURLOptionQ, param_?curlCallbackQ] /; initializedQ :=
	Module[{cc},
		cc = curlOptionInteger[id, Replace[option, CURLLink`$CURLOptions], opTypes["CallbackPointer"], callbackEnum[param]];
		If[cc =!= 0 || !successQ, 
			Throw[$Failed,CURLLink`Utilities`Exception]
		];
	]
	
(* Set any option that requires a String as the parameter, such as setting the URL *)
CURLOption[CURLHandle[id_Integer], option_?CURLLink`CURLOptionQ, param_String] /; initializedQ :=
	Module[{cc}, 
		cc = curlOptionString[id, Replace[option, CURLLink`$CURLOptions], param];
		If[cc =!= 0 || !successQ,
			Throw[$Failed,CURLLink`Utilities`Exception]
		];
	]
	
(* Set options where the parameter consist of a list of bytes. *)  
CURLOption[CURLHandle[id_Integer], option_?CURLLink`CURLOptionQ, param_List] /; initializedQ :=
	Module[{cc}, 
		cc = curlOptionTensor[id, Replace[option, CURLLink`$CURLOptions], Developer`ToPackedArray[param]]; 
		If[cc =!= 0 || !successQ,
			Throw[$Failed,CURLLink`Utilities`Exception]
		];
	]

(* Set True/False Options *)
CURLOption[handle_CURLHandle, option_?CURLLink`CURLOptionQ, param:(True|False)] /; initializedQ :=
	CURLOption[handle, option, Boole[param]]
	
(****************************************************************************)
(* Supply a custom header to be sent when doing CURLPerform *)
CURLAddHeader[CURLHandle[id_Integer], header_String] /; initializedQ :=
	Module[{cc}, 
		cc = curlAddHeader[id, header];
		If[successQ, cc, Throw[$Failed,CURLLink`Utilities`Exception]]
	]

(****************************************************************************)
(* Change the default behavior of events raised by asynchronous connections. *)
CURLAsyncOption[CURLHandle[id_Integer], option_Integer, val:(True|False)] /; initializedQ :=
	Module[{}, 
		curlAsyncOption[id, option, val];
		If[!successQ, Throw[$Failed,CURLLink`Utilities`Exception]]
	]
	
(****************************************************************************)
(* Inform the Async handle to store its cookies when finished. *)
CURLAsyncCookies[CURLHandle[id_Integer], val:(True|False)] /; initializedQ :=
	Module[{}, 
		curlAsyncCookies[id, val];
		If[!successQ, Throw[$Failed,CURLLink`Utilities`Exception]]
	]
	
(****************************************************************************)
(* Change the default behavior of a handle to be asynchronous. *)
CURLSetAsync[CURLHandle[id_Integer], val:(True|False)] /; initializedQ :=
	Module[{}, 
		curlSetAsync[id, val];
		If[!successQ, Throw[$Failed,CURLLink`Utilities`Exception]]
	]
(*
	Add handles to a multihandle
*)

getIDs[CURLHandle[id_Integer]]:=id
CURLMultiHandleInit[] /; initializedQ :=CURLHandleLoad[]

CURLMultiHandleAdd[multihandle_CURLHandle,easyhandles_List]/; initializedQ:=
Module[{mID,easyIDs},
		mID = getIDs[multihandle];
		easyIDs=Map[getIDs[#]&,easyhandles];
		Map[curlMultiAdd[mID, #]&,easyIDs];
		If[successQ, multihandle,Throw[$Failed,CURLLink`Utilities`Exception]]
	]
	
CURLMultiHandleRemove[multihandle_CURLHandle,easyhandles_List]/; initializedQ:=
Module[{mID,easyIDs},
		mID = getIDs[multihandle];
		easyIDs=Map[getIDs[#]&,easyhandles];
		Map[curlMultiRemove[mID, #]&,easyIDs];
		If[successQ, multihandle,Throw[$Failed,CURLLink`Utilities`Exception]]
	]
(******************************************************************************)
(*
	Add handles to a multihandle
*)
Options[CURLMultiPerform]={"IsBlocking"->True}
CURLMultiPerform[CURLHandle[id1_Integer],opts:OptionsPattern[]] /; initializedQ :=
	Module[{code},
		If[OptionValue["IsBlocking"],code=curlMultiPerform[id1],code=curlMultiPerformNoBlock[id1]];
		If[!successQ, Throw[$Failed,CURLLink`Utilities`Exception],code]
	]

End[] (* End Private Context *)

EndPackage[]
