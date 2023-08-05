# parse-IEX
A collection of parsers for [IEX](https://exchange.iex.io/).

Use the parsers to gather relevant quotes and trades information. 

Currently, only TOPS parsing is supported.

## TOPS Parsing Example

```py
from parse_iex import tops

message = b'\x51\x00\xac\x63\xc0\x20\x96\x86\x6d\x14\x5a\x49\x45\x58\x54\x20\x20\x20\xe4\x25\x00\x00\x24\x1d\x0f\x00\x00\x00\x00\x00\xec\x1d\x0f\x00\x00\x00\x00\x00\xe8\x03\x00\x00'
    
print(tops.decode_message(message))
```

```
best bid: 9700 ZIEXT shares for 99.05 USD; best ask: 1000 ZIEXT shares for 99.07 USD @ 2016-08-23 19:30:32.572716
```

## TODO

- [x] Make a basic parser
- [x] Write documentation
- [ ] Report errors
- [ ] Add a DEEP parser
- [ ] Parse trading breaks
