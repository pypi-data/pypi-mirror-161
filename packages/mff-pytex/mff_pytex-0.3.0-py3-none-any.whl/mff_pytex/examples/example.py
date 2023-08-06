from mff_pytex.structure import TexFile

tex = TexFile('foo')
tex.preamble.author = 'Ondra'
tex.preamble.title = 'Example'

tex.document.math("\\frac{1}{2}")
tex.document.newpage()

tex.create()
