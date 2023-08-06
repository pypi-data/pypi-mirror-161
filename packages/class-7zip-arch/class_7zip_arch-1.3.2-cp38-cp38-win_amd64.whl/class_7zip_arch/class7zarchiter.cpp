#include "class7zarchiter.h"
#include "class7zarch.h"

/////////////////////////////////////////////////////////////
// python methods
void
Class7zArchIterator_dealloc(CustomIteratorObject* self)
{
	Py_XDECREF(self->class_7z_arch_object);

	
	Py_TYPE(self)->tp_free((PyObject*)self);         
	//std::wcout << "==Iterator_dealloc === " << self << "\n" << std::flush;
}


PyObject*
Class7zArchIterator_iternext(PyObject* self)
{
	CustomIteratorObject* iterator = (CustomIteratorObject*)self;
	if (iterator->class_7z_arch_object == NULL)
	{
		PyErr_SetString(PyExc_RuntimeError, "Iterator isn't linked to archive");
		return NULL;
	}

	CustomObject* iterated_7z_arch_object = (CustomObject*)iterator->class_7z_arch_object;

	Py_ssize_t n = iterated_7z_arch_object->arch->files_in_arch();

	if (iterator->iter_num >= n)
	{
		/* Raising of standard StopIteration exception with empty value. */
		PyErr_SetNone(PyExc_StopIteration);
		return NULL;
	}
	
	PyObject* path = Class7zArch_file_path_(iterated_7z_arch_object, iterator->iter_num);
	PyObject* size = Class7zArch_file_size_(iterated_7z_arch_object, iterator->iter_num);
	PyObject* data = Class7zArch_extract_(iterated_7z_arch_object, iterator->iter_num);

	PyObject* tmp = Py_BuildValue("NNN", path, size, data);    // "NNN" don't increments reference count to path and data objects
	(iterator->iter_num)++;   

	return tmp;
}


/////////////////////////////////////////////////////////////
// register class type

PyTypeObject Class7zArchIteratorType{
	PyVarObject_HEAD_INIT(NULL, 0)
	"class_7z_arch.Class7zArchIterator",	//.tp_name =
	sizeof(CustomIteratorObject), 0,		// tp_basicsize, tp_itemsize
	(destructor)Class7zArchIterator_dealloc,		// .tp_dealloc=

	0, NULL, NULL, NULL,
	NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,

	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,				//.tp_flags = 
	"7z archive objects",			//.tp_doc = 

	NULL, NULL, NULL, NULL,

	NULL,                  //.tp_iter=   __iter__() method 

	Class7zArchIterator_iternext,             //.tp_iternext=    next() method 

	NULL,		//.tp_methods=
	NULL,       //.tp_members=

	NULL, NULL, NULL, NULL, NULL, NULL,

	NULL, // (initproc)Class7zArchIterator_init, //.tp_init=

	NULL,

	NULL, //				//.tp_new = 
	// 
};

/* !!!!!!!!!!!!
Any iterator object should implement both tp_iter and tp_iternext. An iterator’s tp_iter handler should return a new reference to the iterator.
*/

