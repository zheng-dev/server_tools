%%%-------------------------------------------------------------------
%%% @author "zzc,zhengzhichun@youkia.net" 
%%% @copyright (C)  2022, <youkia, 'www.youkia.net'>
%%% @doc
%%%
%%% @end
%%% Created : 07. 4月 2022 13:13
%%%-------------------------------------------------------------------
%%%
%%%
%%% create date 2022/4/7
-module(sync).
-copyright({youkia, 'www.youkia.net'}).
-author("zzc,zhengzhichun@youkia.net").
-vsn(1).


%%%=======================DEFINE=======================
-include_lib("kernel/include/file.hrl").
-define(INDEX_HAND, 'index').
-define(INDEX_FILE_NAME, ".index").
-define(CODE_VSN, 1).
-define(STATISTICS, '$STATISTICS').
%统计
-record(statistics, {
    key=?STATISTICS,%用作key
    cp_ok_num=0,
    cp_err_num=0
}).

-record(index, {
    file_name,
    modify_time,
    code_version,
    is_dir=false,
    last_iterate_ref%检查是否被删除
}).
%%%=======================EXPORT=======================

%% API
-export([main/1]).
%%%1.对src目录建立索引
%%%2.确定变化了的文件
%%%3.将变化了的文件操作到目标目录(复制或删除)


%%[源str,目标str|_]
main([Src, Desc, ExtendFileAtom | _]) ->
    ExtendFileL = string:tokens(erlang:atom_to_list(ExtendFileAtom), ","),
    io:format("~n===sync args:~p ~n", [{Src, Desc, ExtendFileL}]),
    T1 = erlang:monotonic_time(),
    
    sync(erlang:atom_to_list(Src), erlang:atom_to_list(Desc), ExtendFileL),
    
    T2 = erlang:monotonic_time(),
    Time = erlang:convert_time_unit(T2 - T1, native, millisecond),
    io:format("~n===use ~p millisecond ~n", [Time]),
    ok;
main(ArgL) ->
    io:format("~nzzc log:~p,args:~p ~n", [{?MODULE, ?FUNCTION_NAME, ?LINE}, ArgL]),
    ok.

%%确认源 文件并操作到 目标目录
sync(SrcStr, DescStr, ExtendFileL) ->
    dets:open_file(?INDEX_HAND, [{auto_save, 'infinity'}, {ram_file, true}, %这里确保close才能落地
                                 {file, ?INDEX_FILE_NAME}, {keypos, 2}]),
    dets:insert(?INDEX_HAND, #statistics{}),
    Ref = erlang:make_ref(),%作删除逻辑用
    SP = path_format_unix(ensure_path_end(SrcStr)),
    DP = path_format_unix(ensure_path_end(DescStr)),
    
    %1 读src目录确认修改、新增
    {ok, FileL} = file:list_dir(SrcStr),
    sync1_(FileL, "", SP, DP, ExtendFileL, ?INDEX_HAND, Ref),
    
    % 2src目录的del动作
    sync2_del_(SP, DP, ?INDEX_HAND, Ref),
    
    [#statistics{cp_ok_num=OkNum, cp_err_num=ErrNum}] = dets:lookup(?INDEX_HAND, ?STATISTICS),
    io:format("~n===cp ok_num:~p,err_num:~p ~n", [OkNum, ErrNum]),
    dets:delete(?INDEX_HAND, ?STATISTICS),
    %关闭保存
    dets:close(?INDEX_HAND),
    ok.

sync1_([F | T], Path, Src, Desc, ExtendFL, IndexHand, Ref) ->
    case is_extend_str(F, ExtendFL) of
        false ->
            FName = Path ++ "/" ++ F,
            SrcF = Src ++ FName,
            {ok, #file_info{mtime=ModifyTime, size=_S, type=Type}} = file:read_file_info(SrcF),
            if
                directory == Type ->
                    %递归子目录
                    filelib:ensure_dir(Desc ++ FName ++ "/"),
                    {ok, SubDirFileL} = file:list_dir(SrcF),
                    sync1_(SubDirFileL, FName, Src, Desc, ExtendFL, IndexHand, Ref),
                    
                    dets:insert(IndexHand, #index{file_name=FName ++ "/", code_version=?CODE_VSN,
                                                  is_dir   =true, last_iterate_ref=Ref}),%作 未删除标记
                    
                    %继续同层目录
                    sync1_(T, Path, Src, Desc, ExtendFL, IndexHand, Ref);
                true ->
                    case dets:lookup(IndexHand, FName) of
                        [#index{modify_time=LastTime, code_version=?CODE_VSN} = I | _] when LastTime =:= ModifyTime ->
                            dets:insert(IndexHand, I#index{last_iterate_ref=Ref}),%%作 未删除标记
                            sync1_(T, Path, Src, Desc, ExtendFL, IndexHand, Ref);
                        _ ->
                            R = file:copy(SrcF, Desc ++ FName),
                            
                            [St] = dets:lookup(IndexHand, ?STATISTICS),
                            case R of
                                {ok, _} ->
                                    dets:insert(IndexHand, St#statistics{cp_ok_num=1 + St#statistics.cp_ok_num});
                                _ ->
                                    dets:insert(IndexHand, St#statistics{cp_err_num=1 + St#statistics.cp_err_num})
                            end,
                            io:format("cp ~ts ~ts ret:~p~n", [SrcF, Desc ++ FName, R]),
                            %索引修正
                            dets:insert(IndexHand, #index{file_name  =FName, code_version=?CODE_VSN,
                                                          modify_time=ModifyTime, last_iterate_ref=Ref}),
                            sync1_(T, Path, Src, Desc, ExtendFL, IndexHand, Ref)
                    end
            end;
        _ ->%排除 特征
            sync1_(T, Path, Src, Desc, ExtendFL, IndexHand, Ref)
    end;
sync1_(_, _, _, _, _, _, _) -> ok.

%%删除动作 同步
sync2_del_(_Src, Desc, IndexHand, Ref) ->
    IterF =
    fun
        (#index{file_name=File1, last_iterate_ref=Ref1}, _Acc) when Ref =/= Ref1 ->
            File = case File1 of
                       [$/ | T] ->
                           T;
                       F ->
                           F
                   end,
            FilePath = file_name(Desc ++ File),
            R =
            try
                del_dir_r(FilePath)
            catch
                E:E ->
                    {E, E}
            end,
            case R of
                {error, enoent} ->%目标文件已经不存在
                    dets:delete(IndexHand, File1);
                ok ->%del 成功
                    dets:delete(IndexHand, File1);
                _ ->
                    skip
            end,
            io:format("del  ~ts ret:~p~n", [FilePath, R]),
            1;
        (_, Acc) ->
            Acc
    end,
    dets:foldl(IterF, 0, IndexHand),
    ok.

%%是否要排除的 str
is_extend_str(F, ExtendFL) ->
    lists:any(fun(EF) -> string:str(F, EF) > 0 end, ExtendFL).
%%路径末尾确保/
ensure_path_end(Path) when is_list(Path) ->
    case lists:reverse(Path) of
        [$/ | _T] ->
            Path;
        [$\  | _T] ->
            Path;
        _ ->
            Path ++ "/"
    end.

path_format_unix(Path) ->
    path_format_unix_(Path, []).
path_format_unix_([$\\, $\\ | T], Ret) ->
    path_format_unix_(T, [$/ | Ret]);
path_format_unix_([$/, $/ | T], Ret) ->
    path_format_unix_(T, [$/ | Ret]);
path_format_unix_([$\\ | T], Ret) ->
    path_format_unix_(T, [$/ | Ret]);
path_format_unix_([H | T], Ret) ->
    path_format_unix_(T, [H | Ret]);
path_format_unix_(_, Ret) ->
    lists:reverse(Ret).


%%复制file.erl-------------------------
%otp 10.7没有
del_dir_r(File) -> % rm -rf File
    case file:read_link_info(File) of
        {ok, #file_info{type=directory}} ->
            case file:list_dir_all(File) of
                {ok, Names} ->
                    lists:foreach(fun(Name) ->
                        del_dir_r(filename:join(File, Name))
                                  end, Names);
                {error, _Reason} -> ok
            end,
            file:del_dir(File);
        {ok, _FileInfo} -> file:delete(File);
        {error, _Reason} = Error -> Error
    end.
%%file.erl没export
file_name(N) when is_binary(N) ->
    N;
file_name(N) ->
    try
        file_name_1(N, file:native_name_encoding())
    catch Reason ->
        {error, Reason}
    end.
file_name_1([C | T], latin1) when is_integer(C), C < 256 ->
    [C | file_name_1(T, latin1)];
file_name_1([C | T], utf8) when is_integer(C) ->
    [C | file_name_1(T, utf8)];
file_name_1([H | T], E) ->
    file_name_1(H, E) ++ file_name_1(T, E);
file_name_1([], _) ->
    [];
file_name_1(N, _) when is_atom(N) ->
    atom_to_list(N);
file_name_1(_, _) ->
    throw(badarg).