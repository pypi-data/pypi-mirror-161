#pragma once
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include "Archive.h"
#include "misc.h"
#include <string>


/////////////////////////////////////////////////////////////
// register class structure
typedef struct {  
	PyObject_HEAD
		/* Type-specific fields go here. */

		Archive* arch = NULL;
	//Py_ssize_t iter_num{ 0 };

} CustomObject;

void Class7zArch_dealloc(CustomObject* self);
PyObject* Class7zArch_new(PyTypeObject* type, PyObject* args, PyObject* kwds);
int Class7zArch_init(CustomObject* self, PyObject* args, PyObject* kwds);

PyObject* Class7zArch_get_iter(PyObject* self);

PyObject* Class7zArch_files_in_arch(CustomObject* self, PyObject* Py_UNUSED(ignored));

PyObject* Class7zArch_file_size_(CustomObject* self, Py_ssize_t file_num);
PyObject* Class7zArch_file_size(CustomObject* self, PyObject* args);

PyObject* Class7zArch_file_path_(CustomObject* self, Py_ssize_t file_num);
PyObject* Class7zArch_file_path(CustomObject* self, PyObject* args);

PyObject* Class7zArch_extract_(CustomObject* self, Py_ssize_t file_num);
PyObject* Class7zArch_extract(CustomObject* self, PyObject* args);

PyObject* Class7zArch_extract_all(CustomObject* self, PyObject* Py_UNUSED(ignored));

extern PyMethodDef Class7zArch_methods[];
extern PyTypeObject Class7zArchType;

