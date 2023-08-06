##    threadsnake. A tiny experimental server-side express-like library.
##    Copyright (C) 2022  Erick Fernando Mora Ramirez
##
##    This program is free software: you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation, either version 3 of the License, or
##    (at your option) any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program.  If not, see <https://www.gnu.org/licenses/>.
##
##    mailto:erickfernandomoraramirez@gmail.com

import base64
import json
import os
import re
from hashlib import md5
from typing import Dict

def get_absolute_path(fileName):
    return os.sep.join([os.sep.join(__file__.split(os.sep)[:-1]), fileName])

def encode_base_64(data:str, encoding:str = 'latin1'):
    return base64.b64encode(data.encode(encoding)).decode(encoding)

def decode_base_64(data:str, encoding:str = 'latin1'):
    return base64.b64decode(data.encode(encoding)).decode(encoding)

def load_data(markdownJsonName:str):
    filename = os.sep.join(['markdown_data', markdownJsonName])
    filename = get_absolute_path(filename)
    with open(filename, 'r', encoding='latin1') as f:
        return json.loads(f.read())



commonExpressions = load_data('general.txt')#json.loads(decode_base_64('ewogICAgIiZndDsgKFtcXHdcXFddKj8pKFxcclxcblxcclxcbnxcXHJcXHJ8XFxuXFxuKSI6ICI8YmxvY2txdW90ZT5cXDE8L2Jsb2NrcXVvdGU+XFwyIiwKICAgICIoXFxyXFxufFxccnxcXG4pezIsfSI6ICJcclxuPGJyLz5cclxuIiwKICAgICJfKFteX10rPylfIjogIjxpPlxcMTwvaT4iLAogICAgIlxcKlxcKihbXFx3XFxXXSs/KVxcKlxcKiI6ICI8Yj5cXDE8L2I+IiwKICAgICIjIyMjIyNbXFxzXSooW15cXHJcXG5dKykiOiAiPGg2PlxcMTwvaDY+IiwKICAgICIjIyMjI1tcXHNdKihbXlxcclxcbl0rKSI6ICI8aDU+XFwxPC9oNT4iLAogICAgIiMjIyNbXFxzXSooW15cXHJcXG5dKykiOiAiPGg0PlxcMTwvaDQ+IiwKICAgICIjIyNbXFxzXSooW15cXHJcXG5dKykiOiAiPGgzPlxcMTwvaDM+IiwKICAgICIjI1tcXHNdKihbXlxcclxcbl0rKSI6ICI8aDI+XFwxPC9oMj4iLAogICAgIiNbXFxzXSooW15cXHJcXG5dKykiOiAiPGgxPlxcMTwvaDE+PGhyLz4iLAogICAgIiFcXFsoW15cXF1dKz8pXFxdXFxzKlxcKChbXlxcKV0rPylcXCkiOiAiPGltZyBocmVmPVwiXFwyXCIgYWx0PVwiXFwxXCIvPiIsCiAgICAiXFxbKFteXFxdXSs/KVxcXVxccypcXCgoW15cXCldKz8pXFwpIjogIjxhIGhyZWY9XCJcXDJcIj5cXDE8L2E+IiwKICAgICJgYGAoW1xcd1xcV10rPylgYGAiOiAiPGRpdiBzdHlsZT1cImJhY2tncm91bmQtY29sb3I6IzAwMDc7IHBhZGRpbmc6MC4zZW0gMmVtO1wiPlxcMTwvZGl2PiIsCiAgICAiKChbXFxkXStcXC5bXlxcclxcbl0rW1xcclxcbl0rKSspIjogewogICAgICAgICJyZXAiOiAiPG9sPlxcMTwvb2w+IiwKICAgICAgICAiaW5uZXIiOiB7CiAgICAgICAgICAgICJbXFxkXStcXC4oW15cXHJcXG5dKykiOiAiPGxpPlxcMTwvbGk+IgogICAgICAgIH0KICAgIH0sCiAgICAiKChcXCpbXlxcclxcbl0rW1xcclxcbl0rKSspIjogewogICAgICAgICJyZXAiOiAiPHVsPlxcMTwvdWw+IiwKICAgICAgICAiaW5uZXIiOiB7CiAgICAgICAgICAgICJcXCooW15cXHJcXG5dKykiOiAiPGxpPlxcMTwvbGk+IgogICAgICAgIH0KICAgIH0KfQ=='))
pythonExpressions = load_data('python.txt')#json.loads(decode_base_64('ewogICAgImBgYHB5dGhvbihbXFx3XFxXXSs/KWBgYCI6IHsKICAgICAgICAicmVwIjogIjxkaXYgc3R5bGU9XCJwYWRkaW5nOjBlbSAxZW07IGNvbG9yOiNCQ0Y7IGJhY2tncm91bmQ6YmxhY2s7IGZvbnQtZmFtaWx5OmNhbmRhcmE7XCI+XFwxPC9kaXY+IiwKICAgICAgICAiaW5uZXIiOiB7CiAgICAgICAgICAgICIoXFxyXFxufFxccnxcXG4pIjogIlxyXG48YnIvPlxyXG4iLAogICAgICAgICAgICAiKCAgICB8XHQpIjogIiZuYnNwOyZuYnNwOyZuYnNwOyZuYnNwOyIsCiAgICAgICAgICAgICIoJycnW1xcd1xcV10qPycnJ3wnW1xcd1xcV10qPycpIjogewogICAgICAgICAgICAgICAgInJlcCI6ICI8c3BhbiBzdHlsZT1cImNvbG9yOiNGOTQ7XCI+XFwxPC9zcGFuPiIsCiAgICAgICAgICAgICAgICAiaW5uZXIiOiB7CiAgICAgICAgICAgICAgICAgICAgIihbe31dKSI6ICI8c3BhbiBzdHlsZT1cImNvbG9yOmJsdWU7XCI+XFwxPC9zcGFuPiIKICAgICAgICAgICAgICAgIH0KICAgICAgICAgICAgfSwKICAgICAgICAgICAgIihbXFx3XFxkX10rKVxcKCI6ICI8c3BhbiBzdHlsZT1cImNvbG9yOiNGRjY7XCI+XFwxPC9zcGFuPigiLAogICAgICAgICAgICAiKFtcXFddKShhc3xhc3NlcnR8YnJlYWt8Y29udGludWV8ZGVsfGVsaWZ8ZWxzZXxleGNlcHR8ZmluYWxseXxmb3J8ZnJvbXxpZnxpbXBvcnR8cGFzc3xyYWlzZXxyZXR1cm58dHJ5fHdoaWxlfHdpdGh8eWllbGQpKFtcXFddKSI6ICJcXDE8c3BhbiBzdHlsZT1cImNvbG9yOiNGNEY7XCI+XFwyPC9zcGFuPlxcMyIsCiAgICAgICAgICAgICIoW1xcV10pKGFuZHxjbGFzc3xkZWZ8RmFsc2V8Z2xvYmFsfGlufGlzfGxhbWJkYXxOb25lfG5vbmxvY2FsfG5vdHxvcnxUcnVlKShbXFxXXSkiOiAiXFwxPHNwYW4gc3R5bGU9XCJjb2xvcjojNjZGO1wiPlxcMjwvc3Bhbj5cXDMiLAogICAgICAgICAgICAiKFt7fVxcW1xcXVxcKFxcKV0rKSI6ICI8c3BhbiBzdHlsZT1cImNvbG9yOndoaXRlO1wiPlxcMTwvc3Bhbj4iLAogICAgICAgICAgICAiKFxcQCkiOiAiPHNwYW4gc3R5bGU9XCJjb2xvcjpncmVlbjtcIj5cXDE8L3NwYW4+IgogICAgICAgIH0KICAgIH0KfQ=='))

replacements = {
    '0':'B', '1':'C', '2':'D', '3':'F',
    '4':'G', '5':'H', '6':'J', '7':'K',
    '8':'L', '9':'M', 'a':'N', 'b':'P',
    'c':'Q', 'd':'R', 'e':'S', 'f':'T',
    }
def get_hash(content:str):
    res = md5(content.encode('latin1')).hexdigest()
    for r in replacements:
        res = res.replace(r, replacements[r]) 
    return res

class MarkdownToHtmlParser:
    def __init__(self) -> None:
        self.expressions = {i:i for i in []}

    def use(self, expressionSet:Dict[str, str]):
        self.expressions.update(expressionSet)
        return self
    
    def use_common(self):
        return self.use(commonExpressions)

    def use_python(self):
        return self.use(pythonExpressions)

    def apply_regex_set(self, data:str, regexset:Dict):
        replacements = {}
        styles = {}
        for r in regexset:
            rep = regexset[r]
            if isinstance(rep, str):
                data = re.sub(r, rep, data)
                #while re.search(r, data):
                #    match = re.search(r, data).group()
                #    match = re.sub(r, rep, match, 1)
                #    hash = get_hash(match)
                #    replacements[hash] = match
                #    data = re.sub(r, hash, data, 1)
            elif 'inner' in rep and 'rep' in rep:
                if 'styles' in rep:
                    styles[get_hash(rep['styles'])] = rep['styles']
                while re.search(r, data):
                    match = re.search(r, data).group()
                    match = re.sub(r, rep['rep'], match, 1)
                    match, reps, styl = self.apply_regex_set(match, rep['inner'])
                    replacements.update(reps)
                    styles.update(styl)
                    hash = get_hash(match)
                    replacements[hash] = match
                    data = re.sub(r, hash, data, 1)
        return data, replacements, styles
    
    def convert(self, fileName:str, output:str):
        def tag(name:str, content:str):
            return f'<{name}>{content}</{name}>'
        data, style = self.parse_file(fileName)
        html = tag('html', tag('head', tag('style', style)) + tag('body', data))
        with open(output, 'w', encoding='latin1') as w:
            w.write(html)
    
    def parse_file(self, fileName:str):
        with open(fileName, 'r', encoding='latin1') as r:
            return self.parse_str(r.read())
            
    def parse_str(self, data:str):
        data = data.replace('>','&gt;').replace('<', '&lt;')
        data, replacements, styles = self.apply_regex_set(data, self.expressions)
        while len([i for i in replacements if i in data]) > 0:
            for r in replacements:
                data = data.replace(r, replacements[r])
        stylesString = '\r\n'.join([styles[i] for i in styles])
        return data, stylesString

def create_python_markdown_parser():
    return MarkdownToHtmlParser().use_python().use_common()
