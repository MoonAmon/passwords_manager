#!/usr/bin/env python
# encoding: utf-8

import npyscreen


def simple_function(*args):
    form = npyscreen.Form(name='simple form!')
    form.edit()

if __name__ == '__main__':
    npyscreen.wrapper_basic(simple_function)
