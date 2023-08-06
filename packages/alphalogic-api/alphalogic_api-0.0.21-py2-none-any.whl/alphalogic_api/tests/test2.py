# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from alphalogic_api.objects import Root, Object
from alphalogic_api.decorators import command
from alphalogic_api import init


class MyRoot(Root):

    def handle_get_available_children(self):
        return [
            (TreeChecker, 'TreeChecker')
        ]


def uint64_to_int64(i):
    _MAX = (1 << 63) - 1
    return -(i - _MAX) if i > _MAX else i


class TreeChecker(Object):

    @command(result_type=long)
    def get_root_id(self):
        return self.root().id

    @command(result_type=int)
    def get_child_num(self):
        return len(self.children())

    @command(result_type=long)
    def get_child_id(self, index=0):
        id = self.children()[index].id
        return uint64_to_int64(id)

    @command(result_type=long)
    def get_root_id(self):
        id = self.root().id
        return uint64_to_int64(id)

    def handle_get_available_children(self):
        return [
            (TreeChecker, 'TreeChecker')
        ]


if __name__ == '__main__':
    # python loop
    root = MyRoot()
    root.join()
