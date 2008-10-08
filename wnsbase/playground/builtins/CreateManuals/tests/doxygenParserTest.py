import unittest
from wnsbase.playground.builtins.CreateManuals import doxygenParser
class ParserTests(unittest.TestCase):

    def setUp(self):
        self.sample = """/**
@page pageTitle This is some test

And is has some content with \ref references.
@section theSection Also it has some Sections
With content, too.

@subsection theSubSection And finally it also has some subsections.
ContentContentContnet

@section theSection2 Also it has some Sections
It is always only about the content.
@page anotherPage Test with no content
@section anotherSection The last page does not have any content
*/"""

        self.p = doxygenParser.Parser()

    def testNumChildren(self):
        self.p.parseString(self.sample)
        
        self.assertEqual(self.p.root.getNumChildren(), 2)

    def testGetChildNames(self):
        self.p.parseString(self.sample)

        self.assertEqual(self.p.root.getChildNames(), ['pageTitle', 'anotherPage'])
    
    def testGetChildByName(self):
        self.p.parseString(self.sample)

        self.assertEqual(self.p.root.getChildByName('pageTitle').title, 'pageTitle')

        self.assertEqual(self.p.root.getChildByName('pageTitle').niceTitle, 'This is some test')

    def testGetChildContent(self):
        self.p.parseString(self.sample)

        self.assertEqual(self.p.root.getNumChildren(), 2)

        pageNode = self.p.root.getChildByName('pageTitle')

        self.assertEqual(pageNode.getNumChildren(), 2)

        self.assertEqual(pageNode.rawContent, """@page pageTitle This is some test

And is has some content with \ref references.
@section theSection Also it has some Sections
With content, too.

@subsection theSubSection And finally it also has some subsections.
ContentContentContnet

@section theSection2 Also it has some Sections
It is always only about the content.""")

        self.assertEqual(pageNode.content, """
And is has some content with \ref references.""")

        sectionNode = pageNode.getChildByName('theSection')

        self.assertEqual(sectionNode.niceTitle, 'Also it has some Sections')

        self.assertEqual(sectionNode.rawContent, """@section theSection Also it has some Sections
With content, too.

@subsection theSubSection And finally it also has some subsections.
ContentContentContnet
""")

        self.assertEqual(sectionNode.content,"""With content, too.
""")

        self.assertEqual(sectionNode.getNumChildren(), 1)

        subsectionNode = sectionNode.getChildByName('theSubSection')

        self.assertEqual(subsectionNode.getNumChildren(), 0)

        self.assertEqual(subsectionNode.niceTitle, 'And finally it also has some subsections.')
                
        self.assertEqual(subsectionNode.rawContent, """@subsection theSubSection And finally it also has some subsections.
ContentContentContnet
""")
        self.assertEqual(subsectionNode.content, """ContentContentContnet
""")

        section2Node = pageNode.getChildByName('theSection2')

        self.assertEqual(section2Node.getNumChildren(), 0)

        self.assertEqual(section2Node.niceTitle, 'Also it has some Sections')
                
        self.assertEqual(section2Node.rawContent, """@section theSection2 Also it has some Sections
It is always only about the content.""")

        self.assertEqual(section2Node.content, """It is always only about the content.""")

        page2Node = self.p.root.getChildByName('anotherPage')

        self.assertEqual(page2Node.getNumChildren(), 1)

        self.assertEqual(page2Node.niceTitle, 'Test with no content')
                
        self.assertEqual(page2Node.rawContent, """@page anotherPage Test with no content
@section anotherSection The last page does not have any content
""")
        
        self.assertEqual(page2Node.content, '')


        section3Node = page2Node.getChildByName('anotherSection')

        self.assertEqual(section3Node.getNumChildren(), 0)

        self.assertEqual(section3Node.niceTitle, 'The last page does not have any content')

        self.assertEqual(section3Node.rawContent, """@section anotherSection The last page does not have any content
""")
        self.assertEqual(section3Node.content, """
""")
