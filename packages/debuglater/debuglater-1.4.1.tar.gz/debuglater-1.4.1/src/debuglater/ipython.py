# *****************************************************************************
# Copyright (C) 2001 Nathaniel Gray <n8gray@caltech.edu>
# Copyright (C) 2001-2004 Fernando Perez <fperez@colorado.edu>
# Copyright (C) 2022 Eduardo Blancas <eduardo@ploomber.io>
#
# Distributed under the terms of the BSD License.  The full license is in
# the file COPYING, distributed as part of this software.
# *****************************************************************************
import sys
import types
from functools import partial

from debuglater.pydump import save_dump


def _dump_message(path_to_dump):
    return (f'Serializing traceback to: {path_to_dump}\n'
            f'To debug: dltr {path_to_dump}')


# NOTE: this is based on the IPython implementation
def debugger(self, force: bool = False, path_to_dump: str = 'jupyter.dump'):
    # IPython is an optional depdendency
    from IPython.core.display_trap import DisplayTrap

    if force or self.call_pdb:
        if self.pdb is None:
            self.pdb = self.debugger_cls()
        # the system displayhook may have changed, restore the original
        # for pdb
        display_trap = DisplayTrap(hook=sys.__displayhook__)
        with display_trap:
            self.pdb.reset()
            # Find the right frame so we don't pop up inside ipython itself
            if hasattr(self, 'tb') and self.tb is not None:
                etb = self.tb
            else:
                etb = self.tb = sys.last_traceback
            while self.tb is not None and self.tb.tb_next is not None:
                assert self.tb.tb_next is not None
                self.tb = self.tb.tb_next
            if etb and etb.tb_next:
                etb = etb.tb_next
            self.pdb.botframe = etb.tb_frame

            save_dump(path_to_dump, etb)
            # self.pdb.interaction(None, etb)

        if hasattr(self, 'tb'):
            del self.tb


# taken from IPython interactive shell
def _showtraceback_ipython(self,
                           etype,
                           evalue,
                           stb: str,
                           path_to_dump: str = 'jupyter.dump'):

    val = self.InteractiveTB.stb2text(stb) + '\n' + _dump_message(path_to_dump)

    try:
        print(val)
    except UnicodeEncodeError:
        print(val.encode("utf-8", "backslashreplace").decode())


# taken from ipykernel
# https://github.com/ipython/ipykernel/blob/51a613d501a86073ea1cdbd8023a168646644c6a/ipykernel/zmqshell.py#L530
def _showtraceback_jupyter(self, etype, evalue, stb, path_to_dump):
    from ipykernel.jsonutil import json_clean

    # try to preserve ordering of tracebacks and print statements
    sys.stdout.flush()
    sys.stderr.flush()

    stb = stb + [_dump_message(path_to_dump)]

    exc_content = {
        "traceback": stb,
        "ename": str(etype.__name__),
        "evalue": str(evalue),
    }

    dh = self.displayhook
    # Send exception info over pub socket for other clients than the caller
    # to pick up
    topic = None
    if dh.topic:
        topic = dh.topic.replace(b"execute_result", b"error")

    dh.session.send(
        dh.pub_socket,
        "error",
        json_clean(exc_content),
        dh.parent_header,
        ident=topic,
    )

    # FIXME - Once we rely on Python 3, the traceback is stored on the
    # exception object, so we shouldn't need to store it here.
    self._last_traceback = stb


def patch_ipython(path_to_dump='jupyter.dump'):
    # optional dependency
    import IPython
    term = IPython.get_ipython()
    term.run_line_magic('pdb', 'on')
    debugger_ = partial(debugger, path_to_dump=path_to_dump)
    term.InteractiveTB.debugger = types.MethodType(debugger_,
                                                   term.InteractiveTB)

    _showtraceback_ = partial(_showtraceback_jupyter if hasattr(
        term, '_last_traceback') else _showtraceback_ipython,
                              path_to_dump=path_to_dump)
    term._showtraceback = types.MethodType(_showtraceback_, term)
