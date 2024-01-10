#!/usr/bin/python3

from pandocfilters import toJSONFilter, Str, RawBlock, Div, RawInline, Para, Plain, BulletList, DefinitionList
from PIL import Image
import base64
import os
import re

header_count = {"1": 0, "2": 0, "3": 0}
figure_count = 0
inline_images = True

def handleBulletList(value):
    r = []
    r1 = RawBlock('html', '<text:list text:style-name="L1">')
    r.append(r1)
    for v in value:
        r.append(RawBlock('html', '<text:list-item>'))
        for item in v:
            t = item['t']
            p = None
            if t.endswith('BulletList'):
                p = handleBulletList(item['c'])
                for e in p:
                    r.append(e)
            elif t.endswith('OrderedList'):
                p = handleOrderedList(item['c'])
                for e in p:
                    r.append(e)
            else:
                p = Para(item['c'])
                p = makePlainFromPara(p)
                r.append(p)

        r.append(RawBlock('html', '</text:list-item>'))

    r2 = RawBlock('html', '</text:list>')
    r.append(r2)

    return r

def handleOrderedList(value):
    number = value[0][0]
    r = []
    r1 = RawBlock('html', '<text:list text:style-name="L3">')
    r.append(r1)
    for v in value[1]:
        r.append(RawBlock('html', '<text:list-item>'))
        for item in v:
            t = item['t']
            p = None
            if t.endswith('BulletList'):
                p = handleBulletList(item['c'])
                for e in p:
                    r.append(e)
            elif t.endswith('OrderedList'):
                p = handleOrderedList(item['c'])
                for e in p:
                    r.append(e)
            else:
                p = Para(item['c'])
                p = makePlainFromPara(p)
                r.append(p)
        r.append(RawBlock('html', '</text:list-item>'))
    r2 = RawBlock('html', '</text:list>')
    r.append(r2)

    return r


def getTitleAuthorDate(value):
    s = value.split("\n")
    title = s[0]
    authors = s[1]
    date = s[2]
    r = []

    rb1 = RawBlock('html', '<text:p text:style-name="Title"><text:soft-page-break/>' + title + '</text:p>')
    rb2 = RawBlock('html', '<text:p text:style-name="Signature">' + authors + '</text:p>')
    r.append(rb1)
    r.append(rb2)
    return r

def getKeywords(value):
    r = []
    keywords = value.split(",")
    rb1 = RawBlock('html', '<text:p text:style-name="pragma">/// <text:span text:style-name="T1">Mots-clés ///</text:span></text:p>')
    r.append(rb1)
    r.append(RawBlock('html', '<text:p text:style-name="Normal">'))
    i = 0
    for kw in keywords:
        separator = ""
        if i < len(keywords) -1:
            separator = " / "
        rb = RawBlock('html', '<text:span text:style-name="Normal">' + kw + separator + '</text:span>')
        r.append(rb)
        i += 1
    r.append(RawBlock('html', '</text:p>'))
    rb2 = RawBlock('html', '<text:p text:style-name="pragma">/// <text:span text:style-name="T1">Fin Mots-clés ///</text:span></text:p>')
    r.append(rb2)
    return r


def handleCode(value):
    text = value[1]
    r = []
    r.append(RawInline('html', '<text:span text:style-name="code_5f_par">'))
    r.append(Str(text))
    r.append(RawInline('html', '</text:span>'))
    return r

def handleItalic(value):
    v = value[0]
    r = []
    r.append(RawInline('html', '<text:span text:style-name="italic">'))
    r.append(v)
    r.append(RawInline('html', '</text:span>'))
    return r

# code and console blocks
def handleCodeBlock(value):
    t = "code"
    if value[0][0]:
        t = value[0][0]
    r = []
    ## debut hack
    if t == "header": # title, author, date
        return getTitleAuthorDate(value[1])
    elif t == "keywords":
        return getKeywords(value[1])
    ## fin hack
    linenbr = 0
    for s in value[1].split('\n'):
        linenbr = linenbr + 1
        rb1 = RawBlock( 'html', '<text:p text:style-name="' + t + '">')
        r.append(rb1)
        # add line number for code blocks only
        if t == "code":
            linenbrstr = "{:02d}".format(linenbr)
            i = 0
            #while i < len(linenbrstr) and linenbrstr[i] == " ":
            ##lnlspaces = len(linenbrstr) - len(linenbrstr.lstrip(' '))
            ##if lnlspaces > 0:
            #    r.append(RawBlock('html', '<text:s/>'))
            #    i += 1
            r.append(RawBlock('html', linenbrstr))
        # count number of space characters at the beginning of the line
        lspaces = len(s) - len(s.lstrip(' '))
        if lspaces > 0:
            r.append(RawBlock('html', '<text:s text:c="' + str(lspaces) + '"/>'))
        r.append(Plain([Str(s)]))
        rb2 = RawBlock( 'html', '</text:p>')
        r.append(rb2)
    return r


def handleParagraphValue(v):
    vals = []
    t = v['t']
    if t == 'Str':
        s = v['c']
        m = re.search('^(\[.*\])(.?)', s) # with "[test]." group(1) is "[test]" group(2) is "."
        if m and not s.startswith("[...]"):
            rb1 = RawInline( 'html', '<text:span text:style-name="gras">')
            vals.append(rb1)
            vals.append(RawInline('html', m.group(1)))
            rb2 = RawInline( 'html', '</text:span>')
            vals.append(rb2)
            if len(m.group(2)) > 0:
                vals.append(RawInline('html', m.group(2)))
            return vals
        m = re.search('^(http.?://.*)([.,;:]?)', s)
        if m:
            rb1 = RawInline( 'html', '<text:span text:style-name="url"><text:span text:style-name="T8">')
            vals.append(rb1)
            vals.append(RawInline('html', m.group(1)))
            rb2 = RawInline( 'html', '</text:span></text:span>')
            vals.append(rb2)
            if len(m.group(2)) > 0:
                vals.append(RawInline('html', m.group(2)))
            return vals
    vals = [v]
    return vals

def makePlainFromParaValues(values):
    newv = []
    t = values[0]['t']
    if t == 'Image':
        for v in values:
            newv.append(v)
        p = Plain(newv)
        return p

    rb1 = RawInline( 'html', '<text:p text:style-name="Normal">')
    newv.append(rb1)
    for v in values:
        myvals = handleParagraphValue(v)
        for myv in myvals:
            newv.append(myv)
    rb2 = RawInline( 'html', '</text:p>')
    newv.append(rb2)
    p = Plain(newv)
    return p

def makePlainFromPara(para):
    p = makePlainFromParaValues(para["c"])
    return p

def getHeaderNumber(depth):
    k = str(depth)
    header_count[k] = header_count[k] + 1
    ## set previous counters with greater depth than 'k' to zero
    j = depth + 1
    while j <= len(header_count):
        header_count[str(j)] = 0
        j += 1
    ##
    i = 1
    r = ''
    while i <= depth:
        r += str(header_count[str(i)])
        if i < depth:
            r += "."
        i += 1
    return r

def handleHeaders(value):
    depth = value[0]
    text = value[1][0]
    if depth >= 1 and depth <=3:
        r = []
        r.append(RawBlock('html', 
                '<text:h text:style-name="Heading_20_1" text:outline-level="' 
                + str(depth) + '">' + getHeaderNumber(depth)))
        r.append(Plain(value[2]))
        r.append(RawBlock('html', '</text:h>'))
        return r
    else:
        raise Exception("unknown header depth: ", depth)


def formatBase64(str64, charNum):
    split = [str64[i:i+charNum] for i in range(0, len(str64), charNum)]
    return "\n".join(split)

def handleImage(value):
    global figure_count
    global inline_images
    figure_count += 1
    caption = value[1]
    src = value[2][0]
    r = []

    if inline_images:
        im = Image.open(src)
        width, height = im.size
        ratio = height/width
        w = 6.6
        h = 6.6 * ratio
        r.append(RawInline('html', '<text:p>\n'))
        r.append(RawInline('html', '<draw:frame draw:style-name="fr1" draw:name="Image1" text:anchor-type="frame" svg:width="'+str(w)+'in" svg:height="'+str(h)+'in" draw:z-index="0">\n'))
        r.append(RawInline('html', '<draw:image >\n'))
        r.append(RawInline('html', '<office:binary-data>'))

        with open(src, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            r.append(RawInline('html', formatBase64(encoded_string.decode('ascii'), 72)))

        r.append(RawInline('html', '</office:binary-data>\n'))
        r.append(RawInline('html', '</draw:image>\n'))
        r.append(RawInline('html', '</draw:frame>\n'))
        r.append(RawInline('html', '</text:p>\n'))
    else:
        r.append(RawInline('html', '\n<text:p text:style-name="pragma">/// Image : ' + os.path.basename(src) + ' ///</text:p>\n'))
    # insert caption
    r.append(RawInline('html', '<text:p text:style-name="legende"> Fig. ' + str(figure_count) + ': '))
    for e in caption:
        r.append(e)
    r.append(RawInline('html', '</text:p>\n'))
    return r

def caps(key, value, format, meta):

    if key == 'Para':
        p = makePlainFromParaValues(value)
        return p

    elif key == 'Header':
        r = handleHeaders(value)
        return r

    elif key == 'Code': # text between ` and `
        r = handleCode(value)
        return r

    elif key == 'Emph': # Italic
        r = handleItalic(value)
        return r

    elif key == 'BulletList':
        r = handleBulletList(value)
        return r

    if key == 'OrderedList':
        r = handleOrderedList(value)
        return r

    if key == 'CodeBlock':
        r = handleCodeBlock(value)
        return r

    if key == 'Image':
        r = handleImage(value)
        return r

    else:
        return # do nothing

if __name__ == "__main__":

    inline_images = False
    if "SHOW_IMG_FODT" in os.environ:
        inline_images = True

    toJSONFilter(caps)
