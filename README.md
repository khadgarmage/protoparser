# Protoparser
A package for parsing proto3 files
## Introduction
The purpose of this package is to parse the .proto file (version 3) into a Python data structure.
We use it for code generation or other operations.
## How to Use
```
pip install proto-parser
```
Output format is as following:
```json

{
  "messages": {
    "MessageItem": {
      "comment": {
        "content": "",
        "tags": {}
      },
      "name": "MessageItem",
      "fields": [
        {
          "comment": {
            "content": "",
            "tags": {}
          },
          "type": "string",
          "key_type": "string",
          "val_type": "string",
          "name": "Title",
          "number": 1
        }
      ],
      "messages": {},
      "enums": {}
    },
    "Player": {
      "comment": {
        "content": "//@entry\n//@schema\n",
        "tags": {
          "entry": true,
          "schema": true
        }
      },
      "name": "Player",
      "fields": [
        {
          "comment": {
            "content": "//@fmt=date\n//@desc=Player's birthday\n",
            "tags": {
              "fmt": "date",
              "desc": "Player's birthday"
            }
          },
          "type": "string",
          "key_type": "string",
          "val_type": "string",
          "name": "Birthday",
          "number": 5
        },
        {
          "comment": {
            "content": "//@required\n",
            "tags": {
              "required": true
            }
          },
          "type": "PlayerType",
          "key_type": "PlayerType",
          "val_type": "PlayerType",
          "name": "Type",
          "number": 6
        },
        {
          "comment": {
            "content": "// @title App version history\n",
            "tags": {}
          },
          "type": "repeated",
          "key_type": "string",
          "val_type": "string",
          "name": "AppVerHistory",
          "number": 7
        },
        {
          "comment": {
            "content": "",
            "tags": {}
          },
          "type": "repeated",
          "key_type": "MessageItem",
          "val_type": "MessageItem",
          "name": "MessageBox",
          "number": 8
        },
        {
          "comment": {
            "content": "//@ title =Warehouse\n",
            "tags": {
              "title": "Warehouse"
            }
          },
          "type": "map",
          "key_type": "uint64",
          "val_type": "StoreItem",
          "name": "Storage",
          "number": 9
        },
        {
          "comment": {
            "content": "//@pattern=^(https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]$\n",
            "tags": {
              "pattern": "^(https?|ftp|file)://[-A-Za-z0-9+&",
              "#/%?": "~_|!:,.;]+[-A-Za-z0-9+&",
              "#/%": "~_|]$"
            }
          },
          "type": "string",
          "key_type": "string",
          "val_type": "string",
          "name": "HomePage",
          "number": 11
        }
      ],
      "messages": {
        "StoreItem": {
          "comment": {
            "content": "",
            "tags": {}
          },
          "name": "StoreItem",
          "fields": [
            {
              "comment": {
                "content": "",
                "tags": {}
              },
              "type": "uint32",
              "key_type": "uint32",
              "val_type": "uint32",
              "name": "Num",
              "number": 1
            }
          ],
          "messages": {},
          "enums": {}
        }
      },
      "enums": {
        "InnerType": {
          "comment": {
            "content": "",
            "tags": {}
          },
          "name": "InnerType",
          "fields": [
            {
              "comment": {
                "content": "",
                "tags": {}
              },
              "type": "enum",
              "key_type": "enum",
              "val_type": "enum",
              "name": "TEST",
              "number": "0"
            }
          ]
        }
      }
    }
  },
  "enums": {
    "PlayerType": {
      "comment": {
        "content": "",
        "tags": {}
      },
      "name": "PlayerType",
      "fields": [
        {
          "comment": {
            "content": "//normal player\n",
            "tags": {}
          },
          "type": "enum",
          "key_type": "enum",
          "val_type": "enum",
          "name": "NORMAL",
          "number": "0"
        },
        {
          "comment": {
            "content": "//cheater\n",
            "tags": {}
          },
          "type": "enum",
          "key_type": "enum",
          "val_type": "enum",
          "name": "CHEATER",
          "number": "1"
        }
      ]
    }
  },
  "services": {
    "JobFileService": {
      "name": "JobFileService",
      "functions": [
        {
          "name": "GDriveFileList",
          "in_type": "msg.GDriveFileListReq",
          "out_type": "msg.FileListRep",
          "uri": "/api/files/gdrive"
        }
      ]
    }
  }
}
```
## Bug Reports and Patches
If you think you have found a bug, please visit the Protoparser Github page at https://github.com/khadgarmage/protoparser 
to report an issue, or fix it to push a pull request, thanks.
