%%%-------------------------------------------------------------------
%%% @author "zzc,zhengzhichun@youkia.net" 
%%% @copyright (C)  2022, <youkia, 'www.youkia.net'>
%%% @doc
%%%
%%% @end
%%% Created : 20. 4月 2022 11:15
%%%-------------------------------------------------------------------
%%%
%%%
%%% create date 2022/4/20
-module(cmd_tool).
-copyright({youkia, 'www.youkia.net'}).
-author("zzc,zhengzhichun@youkia.net").
-vsn(1).


%%%=======================DEFINE=======================
-include_lib("kernel/include/file.hrl").

%%%=======================EXPORT=======================

%% API
-export([main/1]).
main([url_ok, IntervalSecondAtom, UrlAtom, TextAtom | _]) ->
    IntervalSecond = list_to_integer(erlang:atom_to_list(IntervalSecondAtom)),
    Url = erlang:atom_to_list(UrlAtom),
    Text = erlang:atom_to_list(TextAtom),
    io:format("~n===url_ok IntervalSecond:~p,Url:~p, Text:~p~n", [IntervalSecond, Url, Text]),
    T1 = erlang:monotonic_time(),
    loop_url(Url, IntervalSecond, Text),
    
    T2 = erlang:monotonic_time(),
    Time = erlang:convert_time_unit(T2 - T1, native, millisecond),
    io:format("~n===use ~p millisecond ~n", [Time]),
    ok;
main([del_log | PathL]) ->
    PathStrL = [erlang:atom_to_list(P) || P <- PathL],
    io:format("~n===del_log path_l:~p~n", [PathStrL]),
    T1 = erlang:monotonic_time(),
    
    {Hour, M, _S} = erlang:time(),
    {_, _, Day} = erlang:date(),
    BorderStr = if
                    Hour =:= 12 andalso M > 3 -> "00";
                    Hour > 12 -> "00";
                    true -> "12"
                end,
    del_log(PathL, lists:reverse(erlang:integer_to_list(Day)), BorderStr),
    
    T2 = erlang:monotonic_time(),
    Time = erlang:convert_time_unit(T2 - T1, native, millisecond),
    io:format("~n===use ~p millisecond ~n", [Time]),
    ok;
main([cmd | CmdAtomL]) ->
%%    io:format("zzc log:~p,args:~p ~n", [{?MODULE, ?FUNCTION_NAME, ?LINE}, CmdAtomL]),
    CmdStr = lists:foldl(fun
                             (CmdAtom, AccL) ->
                                 AccL ++ " " ++ erlang:atom_to_list(CmdAtom)
                         end, "", CmdAtomL),
    T1 = erlang:monotonic_time(),
    
    Ret = os:cmd(CmdStr),
    RetEncode =
    case os:type() of
        {'win32', _} ->%bat用的gbk编译
            Ret;
        _ ->
            Ret
    end,
    
    io:format("~ts ret: ~ts", [CmdStr, RetEncode]),
    T2 = erlang:monotonic_time(),
    Time = erlang:convert_time_unit(T2 - T1, native, millisecond),
    io:format("~n===use ~p millisecond ~n", [Time]),
    ok;
main([export_record | PathL]) ->
    [PathStr | _T] = [erlang:atom_to_list(P) || P <- PathL],
    io:format("zzc log:~p,args:~p ~n", [{?MODULE, ?FUNCTION_NAME, ?LINE}, PathStr]),
    export_record(PathStr),
    
    ok;
main(ArgL) ->
    io:format("~nzzc log:~p,args:~p ~n", [{?MODULE, ?FUNCTION_NAME, ?LINE}, ArgL]),
    ok.

export_record(PathStr) ->
    Name = "record.js",
    file:delete(Name),
    {ok, FPid} = file:open(Name, [write]),
    file:write(FPid, xmerl_ucs:to_utf8("//todo 此文件由工具生成，请勿修改\r\n")),
    case file:list_dir(PathStr) of
        {ok, FS} ->
            [begin
                 L = record_beam(PathStr ++ "/" ++ F),
                 [begin
                      [_ | Line] = lists:foldl(fun
                                                   (Item1, Acc) when is_atom(Item1) ->
                                                       Acc ++ "," ++ erlang:atom_to_list(Item1);
                                                   (Item1, Acc) ->
                                                       io:format("err:~p==~p~n", [K, Item1]),
                                                       Acc
                                               end, "", [K | Fields]),
                      case
                          case get({repeat, Line}) of
                              undefined ->
                                  put({repeat, Line}, true),
                                  true;
                              _ ->
                                  false
                          end
                      of
                          true ->
                              Str = xmerl_ucs:to_utf8(io_lib:format("localStorage.setItem('~ts','~ts')~n", [K, Line])),
                              _R1 = file:write(FPid, Str),
                              ok;
                          _ ->
                              skip
                      end,
                      ok
                  end || {K, Fields} <- L]
             end || F <- FS],
            ok;
        _ ->
            skip
    end,
    file:close(FPid),
    ok.
record_beam(BeamFileStr) ->
    case beam_lib:chunks(BeamFileStr, [abstract_code, "CInf"]) of
        {ok, {_Mod, [{abstract_code, {Version, Forms}}, {"CInf", CB}]}} ->
            case record_attrs(Forms) of
                [] when Version =:= raw_abstract_v1 ->
                    [];
                [] ->
                    %% If the version is raw_X, then this test
                    %% is unnecessary.
%%                    try_source(File, CB),
                    ok;
                Records ->
                    Records
            end;
        {ok, {_Mod, [{abstract_code, no_abstract_code}, {"CInf", CB}]}} ->
%%            try_source(File, CB),
            ok;
        Error ->
            %% Could be that the "Abst" chunk is missing (pre R6).
            Error
    end.

record_attrs(Forms) ->
    [{RecName, record_attrs1_h(FieldList)} || {attribute, _, record, {RecName, FieldList}} <- Forms].
record_attrs1_h(L) ->
    NewL = [begin
                case element(1, Item) of
                    'record_field' ->
                        KName = element(3, Item),
                        KNameStr = element(3, KName),
                        {element(2, Item), KNameStr};
                    _ ->
                        %{record_field,42,{atom,42,attrs}},
                        Item1 = element(2, Item),
                        KName = element(3, Item1),
                        KNameStr = element(3, KName),
                        {element(2, Item1), KNameStr}
        
                end
            end || Item <- L],
    record_attrs1_(lists:keysort(1, NewL), []).
record_attrs1_([{_, KNameStr} | FieldList], Acc) ->
    record_attrs1_(FieldList, [KNameStr | Acc]);
record_attrs1_(_, Acc) -> lists:reverse(Acc).

%%循环url
loop_url(Url, IntervalSecond, Text) ->
    inets:start(),
    case httpc:request(Url) of
        {ok, {_StatusLine, _Headers, Body}} ->
            case string:str(Body, Text) > 0 of
                true ->
                    ok;
                _ ->
                    io:format("url ret body un_match,Url:~p,subText:~p ~n", [Url, Text]),
                    timer:sleep(IntervalSecond),
                    loop_url(Url, IntervalSecond, Text)
            end;
        _ ->
            timer:sleep(IntervalSecond),
            loop_url(Url, IntervalSecond, Text)
    end.
%%yk日志清理
del_log([LogP | T], ReverseDay, Border) ->
    case file:list_dir(LogP) of
        {ok, FL} ->
            [begin
                 [Date, Time | _] = string:tokens(F, "_"),
                 IsSameDay =
                 case {lists:reverse(Date), ReverseDay} of
                     {[H, H2 | _], [DH, DH2]} when H =:= DH, H2 =:= DH2 ->
                         false;
                     {[H | _], [DH]} when H =:= DH ->
                         false;
                     _ ->
                         true
                 end,
                 case string:str(Time, Border) =:= 1 orelse IsSameDay of
                     true ->
                         FileName = lists:concat([LogP, "/", F]),
                         R = file:delete(FileName),
                         io:format("del ~ts,ret:~p ~n", [FileName, R]),
                         ok;
                     _ ->
                         skip
                 end
             end || F <- FL],
            ok;
        _ ->
            skip
    end,
    del_log(T, ReverseDay, Border);
del_log(_, _, _) -> ok.

%%删除指定目录下N秒没修改的文件
%%del_file(ParentPath, Path, ConditionL) ->
%%    Expire = 1,
%%    erlang:integer_to_list(1, 1),
%%    iterate_do_(ParentPath ++ Path, fun del_file1_/3),
%%    ok.
%%del_file1_(File, file, MTime) ->
%%    file:delete(File);
%%del_file1_(File, dir, _) ->
%%    iterate_do_(File, fun del_file1_/3),
%%    ok.
%%%%
%%iterate_do_(Path, Fun) ->
%%    case file:list_dir(Path) of
%%        {ok, FineL} ->
%%            [iterate_do_1_(Path ++ F, Fun) || F <- FineL];
%%        _ ->
%%            skip
%%    end.
%%iterate_do_1_(File, Fun) ->
%%    case file:read_file_info(File) of
%%        {ok, #file_info{type=directory, mtime=MTime}} ->
%%            Fun(File, dir, MTime);
%%        {ok, #file_info{mtime=MTime}} ->
%%            Fun(File, file, MTime)
%%    end.