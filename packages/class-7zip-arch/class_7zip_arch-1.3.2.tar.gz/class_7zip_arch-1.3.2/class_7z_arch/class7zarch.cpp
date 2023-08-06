#include "class7zarchiter.h"
#include "class7zarch.h"

//////////////////////////////////////
//miscellaneous

static void Class7zArch_check_file_num(CustomObject* self, Py_ssize_t file_num)
{
	if (file_num >= self->arch->files_in_arch())
	{
		PyErr_SetString(PyExc_IndexError, "Index of archive item is out of bounds");
	}
}

static std::wstring _get_wstring(PyObject* path)
{
	std::wstring tmp{ utf8_to_wstring(PyUnicode_AsUTF8(path)) };
	return tmp;
}


static std::wstring _get_report_line(PyObject* path, PyObject* size, PyObject* data)
{

	std::wstring line{ L"" };
	if (!path)
	{
		// if path isn't determined
		line.append(L"?????????????????????????");
	}
	else {
		line.append(_get_wstring(path));
	}
	line.append(L"\t\t");

	Py_ssize_t declared_size = 0;
	if (!size)
	{
		//if size isn't determined
		line.append(L"?????");
	}
	else {
		declared_size = PyLong_AsSsize_t(size);
		line.append(std::to_wstring(declared_size));
	}
	line.append(L"\t\t");

	if (!data)
	{
		line.append(L"NOT DECOMPRESSED");
	}
	else {  // if unpacked check actual size

		Py_ssize_t decompressed_size = 0;
		if (data)
		{
			if (Py_TYPE(data) == &PyBytes_Type)
			{
				decompressed_size = PyBytes_Size(data);
			}

		}

		if (declared_size != decompressed_size)
		{
			line.append(L"SIZE DOESN'T CORRESPONDS TO DECLARED");
		}
		else
		{
			line.append(L"OK");
		}

		
	}

	return line;
}

/////////////////////////////////////////////////////////////
// python methods

void 
Class7zArch_dealloc(CustomObject* self)
{
	
	if (self->arch != NULL)
	{
		delete self->arch;
	}

	Py_TYPE(self)->tp_free((PyObject*)self);
	//std::wcout << "==Class7zArch_dealloc === " << self << std::endl << std::flush;
}


PyObject*
Class7zArch_new(PyTypeObject* type, PyObject* args, PyObject* kwds)
{
	CustomObject* self;
	self = (CustomObject*)type->tp_alloc(type, 0);
	if (self != NULL) {
		// nothing to prepare for init
	}
	//std::wcout << "===Class7zArch_new ==== " << self << std::endl << std::flush;

	return (PyObject*)self;
}


int
Class7zArch_init(CustomObject* self, PyObject* args, PyObject* kwds)
{
	char* pointer_from_python;
	Py_ssize_t data_len;
	
	if (!PyArg_ParseTuple(args, "y#", &pointer_from_python, &data_len))  /* convert Python -> C */
	{
		PyErr_SetString(PyExc_TypeError, "argument must be bytes");
		return -1;
	}

	try
	{
		if (self->arch != NULL)
		{
			delete self->arch;
		}
		self->arch = new Archive(pointer_from_python, data_len);
		
		if (self->arch == NULL)
		{
			PyErr_SetString(PyExc_ValueError, "Can't open archive");
			return -1;
		}
	}
	catch (...)
	{
		PyErr_SetString(PyExc_ValueError, "Can't open archive");
		return -1;
	}

	return 0;
}

PyObject*
Class7zArch_get_iter(PyObject* self)
{
	CustomIteratorObject* itr{ PyObject_New(CustomIteratorObject, &Class7zArchIteratorType) };
	if (!itr)
	{
		return NULL;
	}

	Py_INCREF(self);
	itr->class_7z_arch_object = (PyObject*)self;
	itr->iter_num = 0;

	//std::wcout << "==Iterator_MAKE === " << itr << std::endl << std::flush;
	return (PyObject*)itr;
}


/////////////////////////////////////////////////////////////
// class methods
PyObject*
Class7zArch_files_in_arch(CustomObject* self, PyObject* Py_UNUSED(ignored))
{
	if (self->arch == NULL)
	{
		PyErr_SetString(PyExc_AttributeError, "Archive isn't initialized");
		return NULL;
	}

	Py_ssize_t n = self->arch->files_in_arch();

	return Py_BuildValue("n", n);        /* convert C -> Python */
}

PyObject*
Class7zArch_file_size_(CustomObject* self, Py_ssize_t file_num)
{
	Class7zArch_check_file_num(self, file_num);
	if (PyErr_Occurred())
	{
		return NULL; // Если была ошибка то прерываем выполнение 
	}

	try
	{
		Py_ssize_t n = self->arch->filesize(file_num);
		return Py_BuildValue("n", n);        /* convert C -> Python */

	}catch (...)
	{
		PyErr_SetString(PyExc_LookupError, "Can't get item's size");
		return NULL;
	}

	return NULL;
}

PyObject*
Class7zArch_file_size(CustomObject * self, PyObject * args)
{
	Py_ssize_t file_num;

	if (self->arch == NULL)
	{
		PyErr_SetString(PyExc_AttributeError, "Archive isn't initialized");
		return NULL;
	}

	if (!PyArg_ParseTuple(args, "n", &file_num))  /* convert Python -> C */
	{
		PyErr_SetString(PyExc_TypeError, "argument must be int");
		return NULL;                              /* null=raise exception */
	}

	return Class7zArch_file_size_(self, file_num);        /* convert C -> Python */
}

PyObject*
Class7zArch_file_path_(CustomObject* self, Py_ssize_t file_num)
{
	
	Class7zArch_check_file_num(self, file_num);
	if (PyErr_Occurred())
	{
		return NULL; // Если была ошибка то прерываем выполнение 
	}

	try
	{
		std::wstring path = self->arch->filepath(file_num);
		
		std::string path_str{ wstring_to_utf8(path) };

		return Py_BuildValue("s#", path_str.data(), path_str.length());        /* convert C -> Python */
	}
	catch (...)
	{
		PyErr_SetString(PyExc_LookupError, "Can't get item's filename");
		return NULL;
	}
}

PyObject*
Class7zArch_file_path(CustomObject * self, PyObject * args)
{
	Py_ssize_t file_num;

	if (self->arch == NULL)
	{
		PyErr_SetString(PyExc_AttributeError, "Archive isn't initialized");
		return NULL;
	}

	if (!PyArg_ParseTuple(args, "n", &file_num))  /* convert Python -> C */
	{
		PyErr_SetString(PyExc_TypeError, "argument must be int");
		return NULL;                              /* null=raise exception */
	}

	return Class7zArch_file_path_(self, file_num);
}

PyObject*
Class7zArch_extract_(CustomObject* self, Py_ssize_t file_num)
{
	Class7zArch_check_file_num(self, file_num);
	if (PyErr_Occurred())
	{
		return NULL; // Если была ошибка то прерываем выполнение 
	}
		
	try
	{
		
		if (self->arch->arch_info().items()[file_num].isDir()) // Если директория то возвращаем None
		{
			return Py_None;
		}
		
		bytes_vector file_data = std::move(self->arch->extract_filedata(file_num));

		if (file_data.size() == 0)
		{
			return Py_BuildValue("y#", "", 0);  // чтобы создать пустой объект bytes (а не None в случае file_data.data()==Null)
		}
		
		return Py_BuildValue("y#", file_data.data(), file_data.size());
				
	}
	catch (...)
	{
		//std::wcout << L"!!!! there was an exceeeeeption !!!!\n" << std::flush;
		PyErr_SetString(PyExc_LookupError, "Can't decompress archive item");
		return NULL;
	}

}

PyObject*
Class7zArch_extract(CustomObject * self, PyObject * args)
{
	Py_ssize_t file_num;

	if (self->arch == NULL)
	{
		PyErr_SetString(PyExc_AttributeError, "Archive isn't initialized");
		return NULL;
	}

	if (!PyArg_ParseTuple(args, "n", &file_num))  /* convert Python -> C */
	{
		PyErr_SetString(PyExc_TypeError, "argument must be int");
		return NULL;                              /* null=raise exception */
	}

	//std::wcout << "Class7zArch_extract(" << file_num << ")\n" << std::flush;
	return Class7zArch_extract_(self, file_num);
}

PyObject* Class7zArch_extract_all(CustomObject* self, PyObject* Py_UNUSED(ignored))
{
	std::wstring report{L""};

	PyObject* lst{ PyList_New(0) };  // create list object  PyListObject
	bool is_ok{true};

	for (Py_ssize_t i=0; i < self->arch->files_in_arch();  i++)
	{
		
		PyObject* path = Class7zArch_file_path_(self, i);
		PyErr_Clear(); 		//!!!!!!!!!!  clear errors

		PyObject* size = Class7zArch_file_size_(self, i);
		PyErr_Clear(); 		//!!!!!!!!!!    clear errors
		
		PyObject* data = Class7zArch_extract_(self, i);
		PyErr_Clear(); 		//!!!!!!!!!!    clear errors

		if (path && size && data)  // if all OK, add info to list
		{	
			PyObject* tuple{ PyTuple_Pack(3, path, size, data) };   // create tuple object
			Py_DECREF(path);
			Py_DECREF(size);
			Py_DECREF(data);
			PyList_Append(lst, tuple);                              // append tuple to list
			Py_DECREF(tuple);
			
		}
		else
		{
			is_ok = false; // there was an error
		}
		
		//// make line and add to report string

		report.append(_get_report_line(path, size, data));

		report.append(L"\n");

	}
	
	PyObject* py_report{ PyUnicode_FromString(wstring_to_utf8(report).c_str()) }; // create Python str object from std::wstring

	PyObject* rezult;
	if (is_ok)
	{
		rezult = PyTuple_Pack(3, Py_True, py_report, lst);  // Extracting was without error
	}
	else
	{
		rezult = PyTuple_Pack(3, Py_False, py_report, lst); // Extracting was with error
	}

	Py_DECREF(py_report);
	Py_DECREF(lst);
	
	return rezult;
}

/////////////////////////////////////////////////////////////
// register methods
PyMethodDef Class7zArch_methods[] = {
	{"files_in_arch", (PyCFunction)Class7zArch_files_in_arch, METH_NOARGS, "Return number of files in archive"},
	{"file_size", (PyCFunction)Class7zArch_file_size, METH_VARARGS, "Return item size by number"},
	{"file_path", (PyCFunction)Class7zArch_file_path, METH_VARARGS, "Return item path by number"},
	{"extract", (PyCFunction)Class7zArch_extract, METH_VARARGS, "Extract item data by number"},
	{"extract_all", (PyCFunction)Class7zArch_extract_all, METH_NOARGS, "Extract all items and make report"},
	{NULL}  /* Sentinel */
};


/////////////////////////////////////////////////////////////
// register class type
PyTypeObject Class7zArchType = {
	PyVarObject_HEAD_INIT(NULL, 0)
	"class_7z_arch.Class7zArch",	//.tp_name =
	sizeof(CustomObject), 0,		// tp_basicsize, tp_itemsize
	(destructor)Class7zArch_dealloc,		// .tp_dealloc=

	0, NULL, NULL, NULL,
	NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,

	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,				//.tp_flags = 
	"7z archive objects",			//.tp_doc = 

	NULL, NULL, NULL, NULL,

	Class7zArch_get_iter,                  //.tp_iter=   __iter__() method 

	NULL, // Class7zArch_iternext,             //.tp_iternext=    next() method    

	Class7zArch_methods,		//.tp_methods=
	NULL, //Class7zArch_members,       //.tp_members=

	NULL, NULL, NULL, NULL, NULL, NULL,

	(initproc)Class7zArch_init, //.tp_init=

	NULL,

	Class7zArch_new,				//.tp_new = 
	// 
};