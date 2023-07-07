from pyscript import Plugin
import js
import re

plugin = Plugin("SimpleCodeInput")

# TODO: fix escaping of HTML tags
# TODO: fix untabbing working regardless of empty line
# TODO: fix positioning
 
PAGE_SCRIPT = """
from pyodide.ffi.wrappers import add_event_listener
import js

def sync_text():
    code = js.document.querySelector("#highlighter-content")
    editor = js.document.querySelector("#editor")
    code.innerHTML = editor.value
    if (len(editor.value) != 0) and (editor.value[-1] == "\\n"):
        code.innerHTML += " "
        
    js.hljs.highlightAll()
    
def sync_scroll():
    code = js.document.querySelector("#highlighter-content")
    editor = js.document.querySelector("#editor")
    code.scrollTop = editor.scrollTop
    code.scrollLeft = editor.scrollLeft
    
def overwrite_tab(event):
    code = js.document.querySelector("#editor")
    if (event.key) == "Tab":
        event.preventDefault()
        
        before_tab = code.value[0:code.selectionStart]
        after_tab = code.value[code.selectionEnd:len(code.value)]
        
        cursor_pos = code.selectionEnd + 5 - (code.selectionEnd % 4)
        
        code.value = before_tab + ((5 - (code.selectionEnd % 4)) * " ") + after_tab
        
        code.selectionStart = cursor_pos
        code.selectionEnd = cursor_pos
        
        sync_text()
        
    if ((event.key) == "Backspace") and (code.value[code.selectionStart-4:code.selectionStart] == "    "):
        
        before_tab = code.value[0:code.selectionStart-3]
        after_tab = code.value[code.selectionEnd:len(code.value)]
        
        cursor_pos = code.selectionEnd - 3
        
        code.value = before_tab + after_tab
        
        code.selectionStart = cursor_pos
        code.selectionEnd = cursor_pos
        
        sync_text()
        
        
    
        
add_event_listener(js.document.querySelector("#editor"), "keydown", overwrite_tab)
    
"""

INIT_SCRIPT = """
import js
js.hljs.highlightAll()

"""

CSS = """
#editor, #highlighter-content {
    /* Both elements need the same text and space styling so they are directly on top of each other */
    margin: 10px;
    padding: 10px;
    border: 0;
    width: 500px;
    height: 150px;
    
    position: absolute;
    top: 0;
    left: 0;
    
    overflow: auto;
    
    white-space: pre; /* Allows textarea to scroll horizontally */
}

#editor, #highlighter, #highlighter * {
    /* Also add text styles to highlighting tokens */
    font-size: 15pt;
    font-family: monospace;
    line-height: 20pt;
    tab-size: 2;
}

#editor {
    color: transparent;
    background: transparent;
    caret-color: white; /* Or choose your favorite color */
    z-index: 1;
    resize: none;
}

#highlighter {
    z-index: 0;
}

#highlighter {
    padding: 0px;
    width: 500px;
    height: 150px;
}
"""

@plugin.register_custom_element("simple-code-input")
class SimpleCodeInput:
    def __init__(self, element):
        self.element = element

    def connect(self):
        self.add_highlightjs()
        self.add_css(CSS)
        self.add_script(PAGE_SCRIPT)
        self.create_elements()
        self.add_script(INIT_SCRIPT)
        
    def create_elements(self):
        
        editor = js.document.createElement("textarea")
        editor.id = "editor"
        editor.setAttribute("spellcheck", "false")
        editor.setAttribute("py-input", "sync_text();sync_scroll()")
        editor.setAttribute("py-scroll", "sync_scroll()")
        
        highlighter = js.document.createElement("pre")
        highlighter.id = "highlighter"
        highlighter.setAttribute("aria-hidden", "true")
        
        code = js.document.createElement("code")
        code.setAttribute("class", "language-css")
        code.id = "highlighter-content"
        highlighter.appendChild(code)
        
        self.element.appendChild(editor)
        self.element.appendChild(highlighter)
        
          
    def add_script(self, script: str):
        
        script_element = js.document.createElement("py-script")
        script_element.innerHTML = script
        
        js.document.body.appendChild(script_element)
        
    def add_css(self, css: str):
        style = js.document.createElement("style")
        js.document.head.appendChild(style)
        style.innerHTML = css
        
        
    def add_highlightjs(self):
        # Add The CSS
        link = js.document.createElement("link")
        link.type = "text/css"
        link.rel = "stylesheet"
        js.document.head.appendChild(link)
        link.href = "https://cdn.jsdelivr.net/npm/@highlightjs/cdn-assets@11.8.0/styles/vs2015.min.css"

        # Add the JS file
        script = js.document.createElement("script")
        script.type = "text/javascript"
        script.src = "https://cdn.jsdelivr.net/npm/@highlightjs/cdn-assets@11.8.0/highlight.min.js"
        js.document.head.appendChild(script)