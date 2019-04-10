import mistune
from mistune import _block_tag, _pure_pattern, _valid_attr
import re


class BordeauxMarkdownBlockGrammar(object):
    """Grammars for block level tokens."""
    def_links = re.compile(
        r'^ *\[([^^\]]+)\]: *'  # [key]:
        r'<?([^\s>]+)>?'  # <link> or link
        r'(?: +["(]([^\n]+)[")])? *(?:\n+|$)'
    )
    def_footnotes = re.compile(
        r'^\[\^([^\]]+)\]: *('
        r'[^\n]*(?:\n+|$)'  # [^key]:
        r'(?: {1,}[^\n]*(?:\n+|$))*'
        r')'
    )

    newline = re.compile(r'^\n+')
    block_code = re.compile(r'^( {4}[^\n]+\n*)+')
    fences = re.compile(
        r'^ *(`{3,}|~{3,}) *([^`\s]+)? *\n'  # ```lang
        r'([\s\S]+?)\s*'
        r'\1 *(?:\n+|$)'  # ```
    )
    hrule = re.compile(r'^ {0,3}[-*_](?: *[-*_]){2,} *(?:\n+|$)')
    heading = re.compile(r'^ *(#{1,6}) *([^\n]+?) *#* *(?:\n+|$)')
    block_quote = re.compile(r'^( *>[^\n]+([^\n]+)*)+')
    list_block = re.compile(
        r'^( *)(?=[*+-]|\d+\.)(([*+-])?(?:\d+\.)?) [\s\S]+?'
        r'(?:'
        r'\n+(?=\1?(?:[-*_] *){3,}(?:\n+|$))'  # hrule
        r'|\n+(?=%s)'  # def links
        r'|\n+(?=%s)'  # def footnotes\
        r'|\n+(?=\1(?(3)\d+\.|[*+-]) )'   # heterogeneous bullet
        r'|\n{2,}'
        r'(?! )'
        r'(?!\1(?:[*+-]|\d+\.) )\n*'
        r'|'
        r'\s*$)' % (
            _pure_pattern(def_links),
            _pure_pattern(def_footnotes),
        )
    )
    list_item = re.compile(
        r'^(( *)(?:[*+-]|\d+\.) [^\n]*'
        r'(?:\n(?!\2(?:[*+-]|\d+\.) )[^\n]*)*)',
        flags=re.M
    )
    list_bullet = re.compile(r'^ *(?:[*+-]|\d+\.) +')
    paragraph = re.compile(
        r'^((?:[^\n]+(?!'
        r'%s|%s|%s|%s|%s|%s|%s|%s'
        r'))+)\n*' % (
            _pure_pattern(fences).replace(r'\2', r'\3').replace(r'\1', r'\2'),
            _pure_pattern(list_block).replace(r'\1', r'\3'),
            _pure_pattern(hrule),
            _pure_pattern(heading),
            _pure_pattern(block_quote),
            _pure_pattern(def_links),
            _pure_pattern(def_footnotes),
            '<' + _block_tag,
        )
    )
    block_html = re.compile(
        r'^ *(?:%s|%s|%s) *(?:\n{2,}|\s*$)' % (
            r'<!--[\s\S]*?-->',
            r'<(%s)((?:%s)*?)>([\s\S]*?)<\/\1>' % (_block_tag, _valid_attr),
            r'<%s(?:%s)*?\s*\/?>' % (_block_tag, _valid_attr),
        )
    )
    text = re.compile(r'^[^\n]+')


class BordeauxMarkdownBlockLexer(mistune.BlockLexer):
    grammar_class = BordeauxMarkdownBlockGrammar

    default_rules = [
        'newline', 'hrule', 'block_code', 'fences', 'heading',
        'block_quote',
        'list_block', 'block_html', 'def_links',
        'def_footnotes', 'paragraph', 'text'
    ]

    list_rules = (
        'newline', 'block_code', 'fences', 'hrule',
        'block_quote', 'list_block', 'block_html', 'text',
    )

    footnote_rules = (
        'newline', 'block_code', 'fences', 'heading',
        'nptable', 'hrule', 'block_quote',
        'list_block', 'block_html', 'table', 'paragraph', 'text'
    )

BRD = '((([0-9a-z]){1,2})|((([0-9a-z][0-9a-wy-z])|([1-9a-z][0-9a-z]))[0-9a-z]{1,2}))'
TRD = '((([0-9][a-wy-z])|([1-9][a-z])|([a-z]{2})|([0-9]{2}))[0-9a-z]{2})'
PST = '(0x[0-9a-f]+)'

class BordeauxMarkdownInlineGrammar(mistune.InlineGrammar):
    brdx_brd_trd_pst_link = re.compile(r'^{}:{}:{}'.format(BRD, TRD, PST))
    brdx_trd_pst_link = re.compile(r'^:?{}:{}'.format(TRD, PST))
    brdx_brd_trd_link = re.compile(r'^{}:{}'.format(BRD, TRD))
    brdx_trd_link = re.compile(r'^:{}'.format(TRD))
    brdx_pst_link = re.compile(r'^:{}'.format(PST))
    text = re.compile(r'^[\s\S]+?(?=[\\<!\[_*`~]|{}|{}|{}|{}|{}|https?://| {{2,}}\n|$)'.format(
        '({}:{}:{})'.format(BRD, TRD, PST),
        '(:?{}:{})'.format(TRD, PST),
        '({}:{})'.format(BRD, TRD),
        '(:{})'.format(TRD),
        '(:{})'.format(PST)
    ))


class BordeauxMarkdownInlineLexer(mistune.InlineLexer):
    grammar_class = BordeauxMarkdownInlineGrammar

    default_rules = [
        'escape', 'inline_html', 'autolink', 'url',
        'footnote', 'link', 'reflink', 'nolink',
        'double_emphasis', 'emphasis', 'code',
        'linebreak', 'strikethrough',
        'brdx_brd_trd_pst_link',
        'brdx_trd_pst_link',
        'brdx_brd_trd_link',
        'brdx_trd_link',
        'brdx_pst_link',
        'text',
    ]

    def output_brdx_brd_trd_pst_link(self, m):
        return '<a href="/{0}/{1}#{2}" class="brdx-link brd-trd-pst" data-board="{0}" data-thread="{1}" data-post="{2}">{0}<span>:</span>{1}<span>:</span>{2}</a>'.format(m.group(1), m.group(8), m.group(13))
    def output_brdx_trd_pst_link(self, m):
        return '<a href="/---/{0}#{1}" class="brdx-link trd-pst" data-thread="{0}" data-post="{1}"><span>:</span>{0}<span>:</span>{1}</a>'.format(m.group(1), m.group(5))
    def output_brdx_brd_trd_link(self, m):
        return '<a href="/{0}/{1}" class="brdx-link brd-trd" data-board="{0}" data-thread="{1}">{0}<span>:</span>{1}</a>'.format(m.group(1), m.group(8))
    def output_brdx_trd_link(self, m):
        return '<a href="/---/{0}" class="brdx-link trd" data-thread="{0}"><span>:</span>{0}</a>'.format(m.group(1))
    def output_brdx_pst_link(self, m):
        return '<a href="#{0}" class="brdx-link pst" data-post="{0}"><span>:</span>{0}</a>'.format(m.group(1))


class BordeauxMarkdownRenderer(mistune.Renderer):
    def block_quote(self, text):
        return '<div class="quote"><span>></span>%s</div>\n' % text.rstrip('\n')
    def paragraph(self, text):
        # Ugly hack for Firefox to avoid copying unwanted spaces and newlines
        return '<div class="p">%s</div>\n' % text.strip(' ')


render_markdown = mistune.Markdown(
    renderer=BordeauxMarkdownRenderer(),
    block=BordeauxMarkdownBlockLexer(),
    inline=BordeauxMarkdownInlineLexer(BordeauxMarkdownRenderer())
)
