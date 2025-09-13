from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
    NextPageTemplate, PageBreak, FrameBreak
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import cm

class Author:
    def __init__(self, name: str, organization: str):
        self.name = name
        self.organization = organization

    def __str__(self):
        return f'{self.name}, {self.organization}'

class Reference:
    def __init__(self, author: str, title: str, year: int = None):
        self.author = author
        self.title = title
        self.year = year

    def __str__(self):
        if self.year == None:
            return f'{self.author}, {self.title}.'
        return f'{self.author}, {self.title}, {self.year}.'

class MainText:
    def __init__(self, rank: int, text: str):
        self.rank = rank
        self.text = text

class MyDocTemplate(BaseDocTemplate):

    def __init__(self, filename, **kw):
        self.allowSplitting = 0
        BaseDocTemplate.__init__(self, filename, **kw)
#        template = PageTemplate('normal', [Frame(2.5*cm, 2.5*cm, 15*cm, 25*cm, id='F1')])
#        self.addPageTemplates(template)

    def afterFlowable(self, flowable):
        "Registers TOC entries."
        if flowable.__class__.__name__ == 'Paragraph':
            text = flowable.getPlainText()
            style = flowable.style.name
            if style == 'CapterRank1':
                self.notify('TOCEntry', (0, text, self.page))
            if style == 'CapterRank2':
                self.notify('TOCEntry', (1, text, self.page))
            if style == 'CapterRank3':
                self.notify('TOCEntry', (2, text, self.page))
            if style == 'CapterRank4':
                self.notify('TOCEntry', (3, text, self.page))
            if style == 'CapterRank5':
                self.notify('TOCEntry', (4, text, self.page))
            if style == 'CapterRank6':
                self.notify('TOCEntry', (5, text, self.page))
            if style == 'CapterRank7':
                self.notify('TOCEntry', (6, text, self.page))
            if style == 'CapterRank8':
                self.notify('TOCEntry', (7, text, self.page))

class PaperGenerator:
    def __init__(self, font='HeiseiMin-W3'):
        self._font = font
        self._title = 'NO TITLE...'
        self._sub_title = None
        self._authors = []
        self._abstract = 'no abstract...'
        self._main_texts = []
        self._refs = []
        self._double_colmuns = False
        self._chapter_numbers = [0, 0, 0, 0, 0, 0, 0, 0]

        # --- 日本語フォント登録 ---

    def set_double_column(self, mode: bool):
        self._double_colmuns = mode

    def set_title(self, title: str):
        self._title = title 

    def set_sub_title(self, sub_title : str):
        self._sub_title = sub_title 

    def add_author(self, name: str, organization: str):
        self._authors.append(Author(name, organization))

    def set_abstract(self, abstract: str):
        self._abstract = abstract

    def add_sentence(self, sentence: str):
        self._main_texts.append(MainText(-1, sentence))

    def add_chapter(self, chapter: str, chapter_rank = 0):
        self._chapter_numbers[chapter_rank] += 1
        self._main_texts.append(MainText(chapter_rank, f'{self._get_chapter_number(chapter_rank)}. {chapter}'))
        for i in range(chapter_rank+1, len(self._chapter_numbers)):
            self._chapter_numbers[i] = 0
    
    def _get_chapter_number(self, chapter_rank):
        return '.'.join([str(d) for d in self._chapter_numbers[:chapter_rank + 1]])
        

    def add_ref(self, author: str, title: str, year: int = None):
        self._refs.append(Reference(author, title, year))

    # --- ページ番号を描画する関数 ---
    def add_page_number(self, canvas, doc):
        """
        各ページ下部中央にページ番号を描画
        """
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.setFont(self._font, 9)
        # 下部中央に配置
        canvas.drawCentredString(A4[0] / 2.0, 15, text)

    def run(self, path: str):
        pdfmetrics.registerFont(UnicodeCIDFont(self._font))

        doc = MyDocTemplate(path, pagesize=A4)

        doc = self._setup_template(doc)

        story = []

        story = self._add_title(story)

        story.append(NextPageTemplate('TableOfContents'))
        story.append(PageBreak())
        story = self._add_table_of_contents(story)

        if self._double_colmuns:
            story.append(NextPageTemplate('BodyPagesInDoubleColumn'))
        else:
            story.append(NextPageTemplate('BodyPagesInSingleColumn'))

        story.append(PageBreak())

        story = self._add_body(story)

        story.append(NextPageTemplate('References'))
        story.append(PageBreak())

        story = self._add_reference(story)

        doc.multiBuild(story)

    def _add_table_of_contents(self, story):
        style_toc = ParagraphStyle(name='TOCTitle', fontName=self._font,
                          fontSize=18, alignment=TA_CENTER, spaceAfter=20)

        story.append(Paragraph("目次", style_toc))
        toc = TableOfContents()
        # TOCのスタイルをカスタマイズ
        toc.levelStyles = [
            ParagraphStyle('toc_level1', fontName=self._font, fontSize=12, leftIndent=20, firstLineIndent=-20, spaceBefore=5),
            ParagraphStyle('toc_level2', fontName=self._font, fontSize=10, leftIndent=40, firstLineIndent=-20, spaceBefore=2),
            ParagraphStyle('toc_level3', fontName=self._font, fontSize=10, leftIndent=40, firstLineIndent=-20, spaceBefore=2),
            ParagraphStyle('toc_level4', fontName=self._font, fontSize=10, leftIndent=40, firstLineIndent=-20, spaceBefore=2),
            ParagraphStyle('toc_level5', fontName=self._font, fontSize=10, leftIndent=40, firstLineIndent=-20, spaceBefore=2),
            ParagraphStyle('toc_level6', fontName=self._font, fontSize=10, leftIndent=40, firstLineIndent=-20, spaceBefore=2),
            ParagraphStyle('toc_level7', fontName=self._font, fontSize=10, leftIndent=40, firstLineIndent=-20, spaceBefore=2),
            ParagraphStyle('toc_level8', fontName=self._font, fontSize=10, leftIndent=40, firstLineIndent=-20, spaceBefore=2),
        ]

        story.append(toc)
        return story

    def _add_reference(self, story):
        reference_style = ParagraphStyle(
            'Reference', fontName=self._font, fontSize=9, leading=11
        )

        # 最後のページ：引用文献
        if len(self._refs) > 0:
            for i in range(len(self._refs)):
                story.append(Paragraph(f'{i + 1}. {self._refs[i]}', reference_style))
        return story

    def _add_body(self, story):
        body_style = ParagraphStyle(
            'Body', fontName=self._font, fontSize=10.5, leading=11, spaceAfter=5
        )

        chapter_styles = [
            ParagraphStyle('CapterRank1', fontName=self._font, fontSize=15, leading=17, spaceBefore=10, spaceAfter=5, leftIndent=10, outlineLevel=0), 
            ParagraphStyle('CapterRank2', fontName=self._font, fontSize=14, leading=16, spaceBefore=9, spaceAfter=5, leftIndent=10, outlineLevel=1), 
            ParagraphStyle('CapterRank3', fontName=self._font, fontSize=13, leading=15, spaceBefore=8, spaceAfter=5, leftIndent=10, outlineLevel=2), 
            ParagraphStyle('CapterRank4', fontName=self._font, fontSize=12, leading=14, spaceBefore=7, spaceAfter=5, leftIndent=10, outlineLevel=3), 
            ParagraphStyle('CapterRank5', fontName=self._font, fontSize=11, leading=13, spaceBefore=6, spaceAfter=5, leftIndent=10, outlineLevel=4), 
            ParagraphStyle('CapterRank6', fontName=self._font, fontSize=11, leading=13, spaceBefore=6, spaceAfter=5, leftIndent=10, outlineLevel=5), 
            ParagraphStyle('CapterRank7', fontName=self._font, fontSize=11, leading=13, spaceBefore=6, spaceAfter=5, leftIndent=10, outlineLevel=6), 
            ParagraphStyle('CapterRank8', fontName=self._font, fontSize=11, leading=13, spaceBefore=6, spaceAfter=5, leftIndent=10, outlineLevel=7), 
        ]

        # 本文（1ページ目下部2段組から開始）
        for main_text in self._main_texts:
            if main_text.rank < 0 or main_text.rank >= len(chapter_styles):
                story.append(Paragraph(main_text.text, body_style))
            else:
                story.append(Paragraph(main_text.text, chapter_styles[main_text.rank]))
        return story

    def _setup_template(self, doc):
        page_width, page_height = A4
        margin = 40
        gap = 20

        # -----------------------
        # 表紙
        # -----------------------
        top_ypos = A4[1] * 0.2
        top_height = A4[1] * 0.3
        frame_title = Frame(
            margin,
            page_height - margin - top_height - top_ypos,
            page_width - 2*margin,
            top_height,
            id='top'
        )
        abstract_ypos = 100
        abstract_height = 200
        frame_abstract = Frame(margin, abstract_ypos, page_width - 2*margin, abstract_height, id='abstract')
        template_title = PageTemplate(id='FirstPage',
                                    frames=[frame_title, frame_abstract])



        # -----------------------
        # 目次
        # -----------------------
        frame_width_in_toc = (page_width - 2*margin - gap)
        frame_all_in_toc = Frame(margin, margin, frame_width_in_toc, page_height - 2*margin, id='table_of_contents')
        template_body_in_toc = PageTemplate(id='TableOfContents',
                                    frames=[frame_all_in_toc],
                                    onPage=self.add_page_number)   # ★ ページ番号追加

        # -----------------------
        # 2ページ目以降：1カラム本文
        # -----------------------
        frame_width_in_single = (page_width - 2*margin - gap)
        frame_all_in_single = Frame(margin, margin, frame_width_in_single, page_height - 2*margin, id='all_in_single')
        template_body_in_single = PageTemplate(id='BodyPagesInSingleColumn',
                                    frames=[frame_all_in_single],
                                    onPage=self.add_page_number)   # ★ ページ番号追加

        # -----------------------
        # 2ページ目以降：2カラム本文
        # -----------------------
        frame_width_in_double = (page_width - 2*margin - gap) / 2
        frame_left_all_in_double = Frame(margin, margin, frame_width_in_double, page_height - 2*margin, id='left_all')
        frame_right_all_in_double = Frame(margin + frame_width_in_double + gap, margin, frame_width_in_double, page_height - 2*margin, id='right_all')
        template_body_in_double = PageTemplate(id='BodyPagesInDoubleColumn',
                                    frames=[frame_left_all_in_double, frame_right_all_in_double],
                                    onPage=self.add_page_number)   # ★ ページ番号追加

        # -----------------------
        # 最終ページ：引用文献
        # -----------------------
        frame_refs = Frame(margin, margin, page_width - 2*margin, page_height - 2*margin, id='refs')
        template_refs = PageTemplate(id='References',
                                    frames=[frame_refs],
                                    onPage=self.add_page_number)   # ★ ページ番号追加

        doc.addPageTemplates([template_title, template_body_in_toc, template_body_in_single, template_body_in_double, template_refs])
        return doc


    def _add_title(self, story):
        # タイトル
        # --- スタイル定義 ---
        title_style = ParagraphStyle(
            'Title', fontName=self._font, fontSize=24, leading=28, alignment=1, spaceAfter=20
        )
        sub_title_style = ParagraphStyle(
            'SubTitle', fontName=self._font, fontSize=20, leading=28, alignment=1, spaceAfter=20
        )

        authors_style = ParagraphStyle(
            'Authors', fontName=self._font, fontSize=12, leading=14, alignment=1, spaceAfter=5
        )


        abstract_title_style = ParagraphStyle(
            'Abstract', fontName=self._font, fontSize=14, leading=16, spaceAfter=20, alignment=1, leftIndent=80, rightIndent=80
        )
        abstract_body_style = ParagraphStyle(
            'Abstract', fontName=self._font, fontSize=10, leading=12, alignment=1, leftIndent=80, rightIndent=80
        )

        story.append(NextPageTemplate('FirstPage'))

        story.append(Paragraph(self._title, title_style))
        if self._sub_title:
            story.append(Paragraph(f' - {self._sub_title} - ', sub_title_style))

        for author in self._authors:
            story.append(Paragraph(str(author), authors_style))

        story.append(FrameBreak())
        
        story.append(Paragraph('要旨', abstract_title_style))
        story.append(Paragraph(self._abstract, abstract_body_style))
        return story


if __name__ == '__main__':
    path="sample_paper_with_pagenum.pdf"
    pg = PaperGenerator()
    # Abstract
    abstract_text = (
        "ここに論文の概要(Abstract)を記載します。"
        "この部分は1段組みで小さな文字サイズです。"
        "ReportLabを用いてタイトルページから本文、引用文献まで自動生成する手法を示します。"
    )
    pg.set_title('論文タイトル：PythonによるPDF論文自動生成')
    pg.set_sub_title('サブタイトル')
    pg.set_abstract(abstract_text)
    pg.add_chapter("チャプターA", 0)
    for i in range(10):
        pg.add_sentence(
            f"{i+1}段落目：これは2段組み本文のサンプルテキストです。"
            "論文本文として長い文章が続くことを想定しています。"
            "----------------------------------------------"
            "----------------------------------------------"
            "----------------------------------------------")

    pg.add_chapter("チャプターB", 0)
    pg.add_chapter("チャプターBA", 1)
    for i in range(10):
        pg.add_sentence(
            f"{i+1}段落目：これは2段組み本文のサンプルテキストです。"
            "論文本文として長い文章が続くことを想定しています。"
            "----------------------------------------------"
            "----------------------------------------------"
            "----------------------------------------------")

    pg.add_chapter("チャプターBB", 1)
    for i in range(10):
        pg.add_sentence(
            f"{i+1}段落目：これは2段組み本文のサンプルテキストです。"
            "論文本文として長い文章が続くことを想定しています。"
            "----------------------------------------------"
            "----------------------------------------------"
            "----------------------------------------------")

    pg.add_chapter("チャプターBBA", 2)
    for i in range(10):
        pg.add_sentence(
            f"{i+1}段落目：これは2段組み本文のサンプルテキストです。"
            "論文本文として長い文章が続くことを想定しています。"
            "----------------------------------------------"
            "----------------------------------------------"
            "----------------------------------------------")

    pg.add_chapter("チャプターBC", 2)
    pg.add_chapter("チャプターBCA", 3)
    pg.add_chapter("チャプターBCAA", 4)
    pg.add_chapter("チャプターBCAAA", 5)
    pg.add_chapter("チャプターBCAAAA", 6)
    for i in range(10):
        pg.add_sentence(
            f"{i+1}段落目：これは2段組み本文のサンプルテキストです。"
            "論文本文として長い文章が続くことを想定しています。"
            "----------------------------------------------"
            "----------------------------------------------"
            "----------------------------------------------")

    pg.add_chapter("チャプターC", 1)
    pg.add_chapter("チャプターCA", 2)
    pg.add_chapter("チャプターCAA", 3)
    pg.add_chapter("チャプターCB", 2)
    pg.add_chapter("チャプターCBA", 3)
    pg.add_chapter("チャプターCBAA", 4)


    pg.add_ref("Smith J.", "ReportLab Documentation", 2023)
    pg.add_ref("Ogata S.", "Automatic Paper Generation with Python", 2025)
    pg.add_ref("Example Author", "Sample References in ReportLab", 2024)

    pg.add_author('azarashin', 'pit-creation')
    pg.add_author('azarashinX', 'pnc')

    pg.set_double_column(True)

    pg.run(path)


