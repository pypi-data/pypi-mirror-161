from IPython.core.magic import (Magics, magics_class, line_magic, cell_magic,
                                line_cell_magic)
from IPython.core.magic_arguments import (argument, magic_arguments,
                                          parse_argstring)
from IPython.display import IFrame, display
from urllib.parse import quote


@magics_class
class TestMyTutor(Magics):
    @magic_arguments()
    @argument('-w',
              '--width',
              type=int,
              default=1100,
              help="The width of the output frame (default: 1100).")
    @argument('-r', '--run', action='store_true', help="Run cell in IPython.")
    @argument('-h',
              '--height',
              type=int,
              default=700,
              help="The height of the output frame (default: 700).")
    @argument('-lang',
              '--language',
              type=str,
              default='3',
              help="The language of the output (default: python3). \n2 = python2 \n3 = python3 \npyanaconda = Anaconda\njava = java")
    # @cell_magic
    # def mytutor(self, line, cell):
    #     opts = parse_argstring(self.mytutor, line)
    #     if opts.run:
    #         result = self.shell.run_cell(cell)
    #     url = "https://e-quiz.cs.cityu.edu.hk/opt/cs1302visualize.html#mode=display&code="+quote(cell, safe='')
    #     display(IFrame(url, width=opts.width, height=opts.height))
    @cell_magic
    def testmytutor(self, line, cell):
        opts = parse_argstring(self.testmytutor, line)
        if opts.run:
            result = self.shell.run_cell(cell)
        url = "https://mytutor.cs.cityu.edu.hk/opt3/cs1302visualize.html#mode=display&py=" + opts.language + "&code=" + quote(cell, safe='')
        display(IFrame(url, width=opts.width, height=opts.height))


def load_ipython_extension(ipython):
    """
    Register the magics with a running IPython so the magics can be loaded via
     `%load_ext testmytutor` or be configured to be autoloaded by IPython at startup time.
    """
    ipython.register_magics(TestMyTutor)
