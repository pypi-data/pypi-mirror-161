
#define PY_SSIZE_T_CLEAN
#define _SILENCE_CXX17_CODECVT_HEADER_DEPRECATION_WARNING

//#define Py_LIMITED_API // Define this macro before including Python.h to opt in to only use the Limited API, and to select the Limited API version.

#include <Python.h>
#include "class7zarch.h"
#include "class7zarchIter.h"


static PyModuleDef class_7z_archmodule = {
	PyModuleDef_HEAD_INIT,
	"class_7z_arch",											// m_name = 
	"Example module that implements 7z archive class.",			// m_doc = 
	-1															// m_size = 
};

PyMODINIT_FUNC
PyInit_class_7zip_arch(void)
{

	std::wcout << L"class_7zip_arch module: Initializing" << std::endl << std::flush;

	PyObject* m;
	if (PyType_Ready(&Class7zArchType) < 0)
	{
		return NULL;
	}

	if (PyType_Ready(&Class7zArchIteratorType) < 0)
	{
		return NULL;
	}

	m = PyModule_Create(&class_7z_archmodule);
	if (m == NULL)
	{
		return NULL;
	}

	Py_INCREF(&Class7zArchType);
	if (PyModule_AddObject(m, "Class7zArch", (PyObject*)& Class7zArchType) < 0) {
		Py_DECREF(&Class7zArchType);
		Py_DECREF(m);
		return NULL;
	}

	Py_INCREF(&Class7zArchIteratorType);
	if (PyModule_AddObject(m, "Class7zArchIterator", (PyObject*)& Class7zArchIteratorType) < 0) {
		Py_DECREF(&Class7zArchType);
		Py_DECREF(&Class7zArchIteratorType);
		Py_DECREF(m);
		return NULL;
	}

	std::wcout << L"class_7zip_arch module: pass module to python interpreter" << std::endl << std::flush;
	return m;
}