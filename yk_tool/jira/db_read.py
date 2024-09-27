import erlang

r = erlang.binary_to_term(
    bytes(
        [
            131,
            116,
            0,
            0,
            0,
            2,
            100,
            0,
            1,
            99,
            97,
            3,
            100,
            0,
            1,
            116,
            108,
            0,
            0,
            0,
            2,
            97,
            33,
            107,
            0,
            1,
            97,
            106,
        ]
    )
)
print(r, type(r))
