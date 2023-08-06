import pandas as pd
import re

def render_new(html,key = 'Fail'):
  '''
   :param html: It shouldn't include special characters, like "*".
   :param key: Will hilgt the line who has "key" word
   :return:
  '''
  prettyHtml = html

  newhtml=''
  remain= re.search(r'(<html>.*?<tbody>).*?(</tbody>.*</table></body>)', html,re.S)
  pat =re.compile(r'<tr>.*?<td>.*?</td>.*?</tr>',re.S)
  newpat = '''<tr style="color:red;font-weight: bold;">'''
  lst = re.findall(pat,prettyHtml)
  for i in lst:
    if key in i:
      pat = re.compile('<tr>', re.S)
      i = re.sub(pat,newpat,i)
    newhtml+=i
  return remain.group(1)+ newhtml+remain.group(2)

def html_build(data,title,href=None,index=True):
    '''
    :param data:{"a":[1,2,34,5****/**Fail],"b":[2,4,5,6]}
    :param href:
    :param title:
    :return:
    '''
    lines = list(range(1, len(data[list(data.keys())[0]])+1))
    df = pd.DataFrame(data, index=lines)
    pd.set_option('max_colwidth', 200)
    table = df.to_html(index = index)
    css = '''<html>
    <head>
        <style media="all" type="text/css">
            body {
                font-family: Helvetica, sans-serif;
                font-size: 0.8em;
                color: black;
                background: white;
            }

             h1 {
                text-align: center;
             }

            /* dataframe table */
            .dataframe {
                width: 90%;
                border-collapse: collapse;
                empty-cells: show;
                margin-bottom: 0.2em;
            }

            .dataframe tr:hover {
                background: #ECECF7;
                cursor: pointer;
            }
            .dataframe th, .dataframe td {
                border: 1px solid;

            }
            .dataframe th {
                background-color: #DCDCF0;

            }
            .dataframe td {
                vertical-align: middle;
            }

        </style>
    </head>
<body>'''

    Title = "<h1>{}</h1> </br>".format(title)
    if href:
        tail = '</br> </br> <a href="{}">ALERT PAGE</a>'.format(href)
    else:
        tail = ''

    body = table.replace('<tr style="text-align: right;">',
                         '<tr style="text-align: left;background :#C0C0C0">').replace('\\n', '</br>') \
           + tail
    html = css + Title+ body + '</body>'

    return html

if __name__ == '__main__':
    a=   {"a":[1,2,34,'5** /*& % **\**Fail'],"b":[2,4,5,6]}
    print(render_new(html_build(a,'test',index=False)))