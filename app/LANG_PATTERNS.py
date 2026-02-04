# Паттерны языков
LANG_PATTERNS = {
    "python": [
        r"\bdef\s+\w+\s*\(", r"\bclass\s+\w+(?:\(.*\))?:", r"\bimport\s+[\w\.]+", r"\bfrom\s+[\w\.]+\s+import\b",
        r"\bprint\s*\(", r"@[\w\.]+", r"\bself\b", r"\bif\s+__name__\s*==\s*['\"]__main__['\"]:", r"\byield\b"
    ],
    "javascript": [
        r"\bfunction(?:\s+\w+)?\s*\(", r"\bvar\b", r"\blet\b", r"\bconst\b", r"=>", r"\bconsole\.(?:log|error|warn)\b",
        r"\bmodule\.exports\b", r"\brequire\s*\(", r"\bexport\s+default\b", r"\btemplate\s+strings\s+`[^`]*`"
    ],
    "typescript": [
        r"\binterface\s+\w+", r"\btype\s+\w+\s*=", r":\s*(?:string|number|boolean|any|void)\b", r"\benum\s+\w+",
        r"\bimplements\s+\w+", r"\bnamespace\s+\w+", r"\bas\s+\w+", r"\breadonly\b", r"\bprivate\s+constructor\b"
    ],
    "java": [
        r"\bpublic\s+class\s+\w+", r"\bpublic\s+static\s+void\s+main\b", r"import\s+java\.", r"System\.out\.print(?:f|ln)?",
        r"@Override", r"\bpackage\s+[\w\.]+", r"\bextends\s+\w+", r"\bthrows\s+\w+", r"\binterface\s+\w+"
    ],
    "c": [
        r"#include\s*<[\w\.]+>", r"\bprintf\s*\(", r"\bscanf\s*\(", r"int\s+main\s*\((?:int\s+argc)?",
        r"\bmalloc\s*\(", r"\bfree\s*\(", r"struct\s+\w+", r"typedef\s+struct\b"
    ],
    "cpp": [
        r"#include\s*<[\w\.]+>", r"\bstd::[\w\.]+", r"using\s+namespace\s+std\b", r"\bcout\s*<<", r"\bcin\s*>>",
        r"\btemplate\s*<.*>", r"\bclass\s+\w+\s*(?::\s*(?:public|private|protected)\s+\w+)?\s*\{", r"\bvirtual\b"
    ],
    "go": [
        r"\bpackage\s+[\w\.]+", r"\bfunc\b\s+(?:\(.*\)\s+)?\w+\s*\(", r"\bimport\s+\(", r"fmt\.Print(?:f|ln)?",
        r":=\s*", r"\bgo\s+func\b", r"\bselect\s+\{", r"\bchan\b", r"\btype\s+\w+\s+struct\b"
    ],
    "ruby": [
        r"\bdef\s+\w+", r"\bend\b", r"\bclass\s+\w+(?:\s*<\s*\w+)?", r"\bmodule\s+\w+", r"\battr_(?:reader|writer|accessor)\b",
        r"@{1,2}\w+", r"\byield\b", r"\brequire\s*['\"][\w\./]+['\"]", r"\bputs\b"
    ],
    "php": [
        r"<\?(?:php|=)", r"\$[a-zA-Z_]\w*", r"\bfunction\s+[a-zA-Z_]\w*\s*\(", r"\becho\s", r"\bnamespace\s+[\w\\]+",
        r"->", r"::", r"\bclass\s+\w+", r"\bpublic\s+\$this\b"
    ],
    "csharp": [
        r"\busing\s+System\b", r"\bnamespace\s+[\w\.]+", r"\bpublic\s+class\s+\w+", r"Console\.Write(?:Line)?",
        r"\[(?:HttpGet|HttpPost)\]", r"\bget;\s*set;", r"\bvar\s+\w+\s*=", r"\bevent\s+EventHandler\b"
    ],
    "scala": [
        r"\bobject\s+\w+", r"\bextends\s+\w+", r"\btrait\s+\w+", r"\bval\b", r"println\s*\(",
        r"\bdef\s+\w+\s*(?:\[.*\])?\s*\(", r"\bmany\s+=>\b", r"implicit\s+val\b"
    ],
    "kotlin": [
        r"\bfun\s+\w+\s*\(", r"\bval\s+\w+", r"\bvar\s+\w+", r"\bdata\s+class\b", r"\bcompanion\s+object\b",
        r"\?\.let\s*\{", r"\w+\?\.run\s*\{", r"println\s*\("
    ],
    "rust": [
        r"\bfn\s+\w+\s*\(", r"\blet\s+(?:mut\s+)?\w+", r"\bpub\b", r"println!\s*\(", r"\buse\s+std::",
        r"\bstruct\s+\w+", r"\bimpl\s+\w+", r"\bmatch\s+\w+\s*\{", r"\bunwrap\s*\("
    ],
    "swift": [
        r"\bfunc\s+\w+\s*\(", r"import\s+Swift\b", r"\blet\s+\w+", r"\bvar\s+\w+", r"\bguard\s+\b",
        r"\bif\s+let\b", r"print\s*\(", r"\bstruct\s+\w+", r"@objc\b"
    ],
    "lua": [
        r"function\s*\(", r"\blocal\s+\w+", r"\bend\b", r"--\[\[", r"print\s*\(", r"\bdo\s+\b", r"\brepeat\b"
    ],
    "ocaml": [
        r"\blet\s+\w+", r"\bin\b", r"\bmatch\b", r"\bstruct\b", r"\bsig\b", r"module\s+\w+", r"->", r";;"
    ],
    "terraform": [
        r"\bresource\s+['\"]\w+['\"]\s*['\"]\w+['\"]", r"\bprovider\s+['\"]\w+['\"]", r"\bvariable\s+['\"]\w+['\"]",
        r"\bterraform\s*\{", r"\bmodule\s+['\"]\w+['\"]", r"\boutput\s+['\"]\w+['\"]"
    ],
    "bash": [
        r"^\s*#\!\s*/bin/(?:ba)?sh", r"^\s*echo\b", r"\bfi\b", r"\bcase\s+\w+\s+in\b", r"\bdone\b", r"\bset\s+-e\b"
    ],
    "apex": [
        r"\btrigger\s+\w+\s+on\s+\w+\b", r"@IsTest", r"Database\.\w+", r"\bpublic\s+with\s+sharing\s+class\b"
    ],
    "clojure": [
        r"\(defn\s+\w+", r"\(let\s+\[", r"\(ns\s+\w+", r"\(def\b", r"\bdefproject\b"
    ],
    "dart": [
        r"void\s+main\s*\(", r"\bimport\s+['\"]dart:", r"\basync\b", r"\bawait\b", r"\bWidget\s+build\b"
    ],
    "elixir": [
        r"\bdefmodule\s+\w+", r"\bdef\s+\w+", r"\|\>", r"\%\{\w+\s*=>", r"\bquote\s+do\b"
    ],
    "jsx": [
        r"<[A-Z]\w*\b[^>]*>", r"React\.", r"\bimport\s+React\b", r"\bexport\s+default\s+function\s+[A-Z]\w*\b",
        r"className="
    ],
    "julia": [
        r"\bfunction\s+\w+\s*\(", r"\bend\b", r"println\s*\(", r"\busing\s+\w+", r"\bimport\s+\w+", r"\bmodule\s+\w+"
    ],
    "jsonnet": [
        r"\blocal\s+\w+\s*=", r"std\.\w+", r"function\s*\(\w+\)", r"self\.\w+", r"super\.\w+"
    ],
    "lisp": [
        r"\(defun\s+\w+", r"\(setq\b", r"\(lambda\b", r"\(defparameter\b", r"\(cond\b"
    ],
    "r": [
        r"<-\s*", r"library\s*\(", r"ggplot2", r"data\.frame\s*\(", r"summary\s*\("
    ],
    "scheme": [
        r"\(define\s+\w+", r"\(lambda\s*\(", r"\(cond\s*\(", r"\(car\b", r"\(cdr\b"
    ],
    "solidity": [
        r"pragma\s+solidity", r"\bcontract\s+\w+", r"\bevent\s+\w+", r"\bmapping\s*\(", r"msg\.sender", r"payable"
    ],
    "tsx": [
        r"<[A-Z]\w*\b[^>]*>", r":\s*(?:string|number|boolean)", r"\binterface\s+\w+", r"className=", r"as\s+\w+"
    ],
    "xml": [
        r"^<\?xml\b", r"<[a-zA-Z0-9_\-:]+\b[^>]*\/?>", r"<\/?[a-zA-Z0-9_\-:]+>"
    ],
    "yaml": [
        r"^\s*---\s*", r"^\s*[\w\-]+\s*:.*", r"^\s*-\s+[\w\-]+\s*:", r"apiVersion:\s*[\w/\.]+"
    ],
    "json": [
        r"^\s*[\{\[]", r"\"\w+\"\s*:\s*(?:\"[^\"]*\"|\d+|true|false|null)"
    ],
    "dockerfile": [
        r"^FROM\s+[\w\.:/-]+", r"^(?:RUN|COPY|ADD|WORKDIR|ENTRYPOINT|CMD)\s+", r"^EXPOSE\s+\d+"
    ],
    "html": [
        r"<![Dd][Oo][Cc][Tt][Yy][Pp][Ee]\b", r"<html\b", r"<head\b", r"<body\b", r"<script\b", r"<link\b"
    ],
    "cairo": [
        r"\bfunc\s+[a-z_]\w*\s*\(", r"\bimplicit\s+args\b", r"\bfelt\b", r"\breturn\s+\b", r"%[a-z_]\w*"
    ],
    "circom": [
        r"\btemplate\s+\w+\s*\(", r"\bsignal\s+(?:input|output)\b", r"component\s+\w+", r"==>", r"<=="
    ],
    "hack": [
        r"<\?hh", r"\bfunction\s+[a-z_]\w*\s*\(", r":\s*void\b", r"<<\w+>>", r"Vector\s*<"
    ],
    "move": [
        r"\bmodule\s+\w+::\w+", r"\bpublic\s+fun\s+\w+", r"\bstruct\s+\w+", r"\bacquire\b", r"move_to\b"
    ]
}
