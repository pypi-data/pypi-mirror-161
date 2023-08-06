# kvh

KVH format is a lightweight key-value hierarchy format for storing nested structures.
It uses only 3 control characters:

 - \<tab\> for separating key from value and indenting nested keys;
 - \<newline\> for separating key-value records from each other;
 - \<backslash\> for escaping previous 2 characters and itself.
 
 For example, the following file introduces salutations in English and French:
 
 ```
 salutation
	en	Hello World!
	fr	Salut, le Monde !
 ```
 
The world `salutation` is a key without value. The indented keys `en` and `fr` are sub-keys of `salutation`. As `salutation` has sub-keys, it cannot have its own value. That's why it is immediately followed by a \<newline\> and not \<tab\>. The text `Hello World!` is a value of `en`. Note the absence of quotes, double quotes and alike.

Let suppose that this content is saved in a file `salut.kvh`
Then we can read it in Python3

```python
import kvh.kvh as kv

# prepare salut.kvh
with open("salut.kvh", "w") as fp:
	print("salutation\n\ten\tHello World!\n\tfr\tSalut, le Monde !", file=fp)

res=kv.kvh_read("salut.kvh")
print(res)

# sometimes, a dict() can be a more tractable structure to hold the content
d=kv.kvh2dict("salut.kvh")
print(d)
```
