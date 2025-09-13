from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer,
    NextPageTemplate, PageBreak, FrameBreak
)
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

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

class PaperGenerator:
    def __init__(self, font='HeiseiMin-W3'):
        self._font = font
        self._title = 'NO TITLE...'
        self._abstract = 'no abstract...'
        self._main_texts = []
        self._refs = []

        # --- 日本語フォント登録 ---

    def set_title(self, title: str):
        self._title = title 

    def set_abstract(self, abstract: str):
        self._abstract = abstract

    def add_sentence(self, sentence: str):
        self._main_texts.append(MainText(-1, sentence))

    def add_chapter(self, chapter: str, chapter_rank = 0):
        self._main_texts.append(MainText(chapter_rank, chapter))

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

        # --- スタイル定義 ---
        title_style = ParagraphStyle(
            'Title', fontName=self._font, fontSize=24, leading=28, alignment=1, spaceAfter=20
        )
        abstract_style = ParagraphStyle(
            'Abstract', fontName=self._font, fontSize=8, leading=10, spaceAfter=20, alignment=1, leftIndent=80, rightIndent=80
        )
        body_style = ParagraphStyle(
            'Body', fontName=self._font, fontSize=10.5, leading=11, spaceAfter=5
        )
        reference_style = ParagraphStyle(
            'Reference', fontName=self._font, fontSize=9, leading=11
        )

        doc = BaseDocTemplate(path, pagesize=A4)

        page_width, page_height = A4
        margin = 40
        gap = 20

        # -----------------------
        # 1ページ目：上部1カラム + 下部2カラム
        # -----------------------
        top_height = 180
        frame_top = Frame(
            margin,
            page_height - margin - top_height,
            page_width - 2*margin,
            top_height,
            id='top'
        )
        bottom_height = page_height - 2*margin - top_height
        frame_width = (page_width - 2*margin - gap) / 2
        frame_left = Frame(margin, margin, frame_width, bottom_height, id='left')
        frame_right = Frame(margin + frame_width + gap, margin, frame_width, bottom_height, id='right')
        template_first = PageTemplate(id='FirstPage',
                                    frames=[frame_top, frame_left, frame_right],
                                    onPage=self.add_page_number)   # ★ ページ番号追加

        # -----------------------
        # 2ページ目以降：2カラム本文
        # -----------------------
        frame_left_all = Frame(margin, margin, frame_width, page_height - 2*margin, id='left_all')
        frame_right_all = Frame(margin + frame_width + gap, margin, frame_width, page_height - 2*margin, id='right_all')
        template_body = PageTemplate(id='BodyPages',
                                    frames=[frame_left_all, frame_right_all],
                                    onPage=self.add_page_number)   # ★ ページ番号追加

        # -----------------------
        # 最終ページ：引用文献
        # -----------------------
        frame_refs = Frame(margin, margin, page_width - 2*margin, page_height - 2*margin, id='refs')
        template_refs = PageTemplate(id='References',
                                    frames=[frame_refs],
                                    onPage=self.add_page_number)   # ★ ページ番号追加

        doc.addPageTemplates([template_first, template_body, template_refs])

        story = []
        # タイトル
        story.append(Paragraph(self._title, title_style))

        story.append(Paragraph(self._abstract, abstract_style))

        # ★ 上部フレームを明示的に終了させる
        story.append(FrameBreak())
        story.append(NextPageTemplate('BodyPages'))
        # 本文（1ページ目下部2段組から開始）
        for main_text in self._main_texts:
            story.append(Paragraph(main_text.text, body_style))

        if len(self._refs) > 0:
            # 最後のページ：引用文献
            story.append(NextPageTemplate('References'))
            story.append(PageBreak())

            for i in range(len(self._refs)):
                story.append(Paragraph(f'{i + 1}. {self._refs[i]}', reference_style))

        doc.build(story)


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
    pg.set_abstract(abstract_text)
    for i in range(40):
        pg.add_sentence(
            f"{i+1}段落目：これは2段組み本文のサンプルテキストです。"
            "論文本文として長い文章が続くことを想定しています。"
            "----------------------------------------------"
            "----------------------------------------------"
            "----------------------------------------------")

    pg.add_ref("Smith J.", "ReportLab Documentation", 2023)
    pg.add_ref("Ogata S.", "Automatic Paper Generation with Python", 2025)
    pg.add_ref("Example Author", "Sample References in ReportLab", 2024)
    pg.run(path)

