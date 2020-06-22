#!/usr/bin/env python
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from lark import Lark, Transformer, Tree
from collections import namedtuple
import typing
import json

BNF = r'''
OCTALDIGIT: "0..7"
IDENT: ( "_" )* LETTER ( LETTER | DECIMALDIGIT | "_" )*
FULLIDENT: IDENT ( "." IDENT )*
MESSAGENAME: IDENT
ENUMNAME: IDENT
FIELDNAME: IDENT
ONEOFNAME: IDENT
MAPNAME: IDENT
SERVICENAME: IDENT
TAGNAME: IDENT
TAGVALUE: IDENT
RPCNAME: IDENT
MESSAGETYPE: [ "." ] ( IDENT "." )* MESSAGENAME
ENUMTYPE: [ "." ] ( IDENT "." )* ENUMNAME

INTLIT    : DECIMALLIT | OCTALLIT | HEXLIT
DECIMALLIT: ( "1".."9" ) ( DECIMALDIGIT )*
OCTALLIT  : "0" ( OCTALDIGIT )*
HEXLIT    : "0" ( "x" | "X" ) HEXDIGIT ( HEXDIGIT )*

FLOATLIT: ( DECIMALS "." [ DECIMALS ] [ EXPONENT ] | DECIMALS EXPONENT | "."DECIMALS [ EXPONENT ] ) | "inf" | "nan"
DECIMALS : DECIMALDIGIT ( DECIMALDIGIT )*
EXPONENT : ( "e" | "E" ) [ "+" | "-" ] DECIMALS

BOOLLIT: "true" | "false"

STRLIT: ( "'" ( CHARVALUE )* "'" ) |  ( "\"" ( CHARVALUE )* "\"" )
CHARVALUE: HEXESCAPE | OCTESCAPE | CHARESCAPE |  /[^\0\n\\]/
HEXESCAPE: "\\" ( "x" | "X" ) HEXDIGIT HEXDIGIT
OCTESCAPE: "\\" OCTALDIGIT OCTALDIGIT OCTALDIGIT
CHARESCAPE: "\\" ( "a" | "b" | "f" | "n" | "r" | "t" | "v" | "\\" | "'" | "\"" )
QUOTE: "'" | "\""

EMPTYSTATEMENT: ";"

CONSTANT: FULLIDENT | ( [ "-" | "+" ] INTLIT ) | ( [ "-" | "+" ] FLOATLIT ) | STRLIT | BOOLLIT

syntax: "syntax" "=" QUOTE "proto3" QUOTE ";"

import: "import" [ "weak" | "public" ] STRLIT ";"

package: "package" FULLIDENT ";"

option: "option" OPTIONNAME  "=" CONSTANT ";"
OPTIONNAME: ( IDENT | "(" FULLIDENT ")" ) ( "." IDENT )*

TYPE: "double" | "float" | "int32" | "int64" | "uint32" | "uint64" | "sint32" | "sint64" | "fixed32" | "fixed64" | "sfixed32" | "sfixed64" | "bool" | "string" | "bytes" | MESSAGETYPE | ENUMTYPE
FIELDNUMBER: INTLIT

field: [ comments ] TYPE FIELDNAME "=" FIELDNUMBER [ "[" fieldoptions "]" ] ";"
fieldoptions: fieldoption ( ","  fieldoption )*
fieldoption: OPTIONNAME "=" CONSTANT
repeatedfield: [ comments ] "repeated" field

oneof: "oneof" ONEOFNAME "{" ( oneoffield | EMPTYSTATEMENT )* "}"
oneoffield: TYPE FIELDNAME "=" FIELDNUMBER [ "[" fieldoptions "]" ] ";"

mapfield: [ comments ] "map" "<" KEYTYPE "," TYPE ">" MAPNAME "=" FIELDNUMBER [ "[" fieldoptions "]" ] ";"
KEYTYPE: "int32" | "int64" | "uint32" | "uint64" | "sint32" | "sint64" | "fixed32" | "fixed64" | "sfixed32" | "sfixed64" | "bool" | "string"

reserved: "reserved" ( ranges | fieldnames ) ";"
ranges: range ( "," range )*
range:  INTLIT [ "to" ( INTLIT | "max" ) ]
fieldnames: FIELDNAME ( "," FIELDNAME )*

enum: [ comments ] "enum" ENUMNAME enumbody
enumbody: "{" ( enumfield | EMPTYSTATEMENT )* "}"
enumfield: [ COMMENTS ] IDENT "=" INTLIT [ "[" enumvalueoption ( ","  enumvalueoption )* "]" ] ";"
enumvalueoption: OPTIONNAME "=" CONSTANT

message: [ comments ] "message" MESSAGENAME messagebody
messagebody: "{" ( repeatedfield | field | enum | message | option | oneof | mapfield | reserved | EMPTYSTATEMENT )* "}"

googleoption: "option" "(google.api.http)"  "=" "{" [ "post:" CONSTANT [ "body:" CONSTANT ] ] "}" ";"
service: "service" SERVICENAME "{" ( option | rpc | EMPTYSTATEMENT )* "}"
rpc: "rpc" RPCNAME "(" [ "stream" ] MESSAGETYPE ")" "returns" "(" [ "stream" ] MESSAGETYPE ")" ( ( "{" ( googleoption | option | EMPTYSTATEMENT )* "}" ) | ";" )

proto: syntax ( import | package | option | topleveldef | EMPTYSTATEMENT )*
topleveldef: message | enum | service

COMMENT: "//" /.*/ "\n"
comments: COMMENT ( COMMENT )*
COMMENTS: COMMENT ( COMMENT )*

%import common.HEXDIGIT
%import common.DIGIT -> DECIMALDIGIT
%import common.LETTER
%import common.WS
%import common.NEWLINE
%ignore WS
'''

Comment = typing.NamedTuple('Comment', [('content', str), ('tags', typing.Dict[str, typing.Any])])
Field = typing.NamedTuple('Field', [('comment', 'Comment'), ('type', str), ('key_type', str), ('val_type', str), ('name', str), ('number', int)])
Enum = typing.NamedTuple('Enum', [('comment', 'Comment'), ('name', str), ('fields', typing.Dict[str, 'Field'])])
Message = typing.NamedTuple('Message', [('comment', 'Comment'), ('name', str), ('fields', typing.List['Field']),
                                        ('messages', typing.Dict[str, 'Message']), ('enums', typing.Dict[str, 'Enum'])])
Service = typing.NamedTuple('Service', [('name', str), ('functions', typing.Dict[str, 'RpcFunc'])])
RpcFunc = typing.NamedTuple('RpcFunc', [('name', str), ('in_type', str), ('out_type', str), ('uri', str)])
ProtoFile = typing.NamedTuple('ProtoFile',
                              [('messages', typing.Dict[str, 'Message']), ('enums', typing.Dict[str, 'Enum']),
                               ('services', typing.Dict[str, 'Service']), ('imports', typing.List[str])])


class ProtoTransformer(Transformer):
    '''Converts syntax tree token into more easily usable namedtuple objects'''

    def message(self, tokens):
        '''Returns a Message namedtuple'''
        comment = Comment("", {})
        if len(tokens) < 3:
            name_token, body = tokens
        else:
            comment, name_token, body = tokens
        return Message(comment, name_token.value, *body)

    def messagebody(self, items):
        '''Returns a tuple of message body namedtuples'''
        messages = {}
        enums = {}
        fields = []
        for item in items:
            if isinstance(item, Message):
                messages[item.name] = item
            elif isinstance(item, Enum):
                enums[item.name] = item
            elif isinstance(item, Field):
                fields.append(item)
        return fields, messages, enums

    def field(self, tokens):
        '''Returns a Field namedtuple'''
        comment = Comment("", {})
        if len(tokens) < 4:
            type, fieldname, fieldnumber = tuple(tokens)
        elif isinstance(tokens[3], Tree):
            type, fieldname, fieldnumber, options = tuple(tokens)
        else:
            comment, type, fieldname, fieldnumber = tuple(tokens)
        return Field(comment, type.value, type.value, type.value, fieldname.value, int(fieldnumber.value))

    def repeatedfield(self, tokens):
        '''Returns a Field namedtuple'''
        comment = Comment("", {})
        if len(tokens) < 2:
            field = tokens[0]
        else:
            comment, field = tuple(tokens)
        return Field(comment, 'repeated', field.type, field.type, field.name, field.number)

    def mapfield(self, tokens):
        '''Returns a Field namedtuple'''
        comment = Comment("", {})
        if len(tokens) < 5:
            key_type, val_type, fieldname, fieldnumber = tuple(tokens)
        else:
            comment, key_type, val_type, fieldname, fieldnumber = tuple(tokens)
        return Field(comment, 'map', key_type.value, val_type.value, fieldname.value, int(fieldnumber.value))

    def comments(self, tokens):
        '''Returns a Tag namedtuple'''
        comment = ''
        tags = {}
        for token in tokens:
            comment += token
            if token.find('@') < 0:
                continue
            kvs = token.strip(" /\n").split('@')
            for kv in kvs:
                kv = kv.strip(" /\n")
                if not kv:
                    continue
                tmp = kv.split('=')
                key = tmp[0].strip(" /\n").lower()
                if key.find(" ") >= 0:
                    continue
                if len(tmp) > 1:
                    tags[key] = tmp[1].lower()
                else:
                    tags[key] = True
        return Comment(comment, tags)

    def enum(self, tokens):
        '''Returns an Enum namedtuple'''
        comment = Comment("", {})
        if len(tokens) < 3:
            name, fields = tokens
        else:
            comment, name, fields = tokens
        return Enum(comment, name.value, fields)

    def enumbody(self, tokens):
        '''Returns a sequence of enum identifiers'''
        enumitems = []
        for enumfield in tokens:
            if enumfield.data != 'enumfield':
                continue
            comment = Comment("", {})
            if len(enumfield.children) < 3:
                name, value = enumfield.children
            else:
                comment, name, value = enumfield.children
                comment = self.comments(comment)
            enumitems.append(Field(comment, 'enum', 'enum', 'enum', name.value, value.value))
        return enumitems

    def service(self, tokens):
        '''Returns a Service namedtuple'''
        functions = []
        for i in range(1, len(tokens)):
            functions.append(tokens[i])
        return Service(tokens[0].value, functions)

    def rpc(self, tokens):
        '''Returns a RpcFunc namedtuple'''
        uri = ''
        if len(tokens) < 4:
            name, in_type, out_type = tokens
        else:
            name, in_type, out_type, option_token = tokens
            uri = option_token.children[0].value
        return RpcFunc(name.value, in_type.value, out_type.value, uri.strip('"'))


def _recursive_to_dict(obj):
    _dict = {}

    if isinstance(obj, tuple):
        node = obj._asdict()
        for item in node:
            if isinstance(node[item], list):  # Process as a list
                _dict[item] = [_recursive_to_dict(x) for x in (node[item])]
            elif isinstance(node[item], tuple):  # Process as a NamedTuple
                _dict[item] = _recursive_to_dict(node[item])
            elif isinstance(node[item], dict):
                for k in node[item]:
                    if isinstance(node[item][k], tuple):
                        node[item][k] = _recursive_to_dict(node[item][k])
                _dict[item] = node[item]
            else:  # Process as a regular element
                _dict[item] = (node[item])
    return _dict


def parse_from_file(file: str):
    with open(file, 'r') as f:
        data = f.read()
    if data:
        return parse(data)


def parse(data: str):
    parser = Lark(BNF, start='proto', parser='lalr')
    tree = parser.parse(data)
    trans_tree = ProtoTransformer().transform(tree)
    enums = {}
    messages = {}
    services = {}
    imports = []
    import_tree = trans_tree.find_data('import')
    for tree in import_tree:
        for child in tree.children:
            imports.append(child.value.strip('"'))
    top_data = trans_tree.find_data('topleveldef')
    for top_level in top_data:
        for child in top_level.children:
            if isinstance(child, Message):
                messages[child.name] = child
            if isinstance(child, Enum):
                enums[child.name] = child
            if isinstance(child, Service):
                services[child.name] = child
    return ProtoFile(messages, enums, services, imports)


def serialize2json(data):
    return json.dumps(_recursive_to_dict(parse(data)))


def serialize2json_from_file(file: str):
    with open(file, 'r') as f:
        data = f.read()
    if data:
        return json.dumps(_recursive_to_dict(parse(data)))
