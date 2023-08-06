#pragma once
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <iostream>


typedef struct {  //
	PyObject_HEAD
		/* Type-specific fields go here. */

	PyObject* class_7z_arch_object = NULL;
	Py_ssize_t iter_num{ 0 };

} CustomIteratorObject;

void Class7zArchIterator_dealloc(CustomIteratorObject* self);
PyObject* Class7zArchIterator_iternext(PyObject* self);

extern PyTypeObject Class7zArchIteratorType;

