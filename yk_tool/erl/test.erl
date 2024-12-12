-module(test).
-vsn(1).

%%%=======================DEFINE=======================

%%%=======================EXPORT=======================

%% API
-export([eval/2]).

%%执行字符串
eval(String, Args) ->
    %%	ets_benchmark:eval("B=3,A+B.",[{'A',1}]).
    %%	{value,4,[{'A',1},{'B',3}]}
    {ok, Scan1, _} = erl_scan:string(String),
    {ok, P} = erl_parse:parse_exprs(Scan1),
    erl_eval:exprs(P, Args).
