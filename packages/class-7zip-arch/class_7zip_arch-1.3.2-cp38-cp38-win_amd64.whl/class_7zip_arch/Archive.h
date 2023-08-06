#pragma once
#define BIT7Z_AUTO_FORMAT  // !!!!!!!!!! 

#include <iostream>
#include <vector>
#include <fstream>
#include "libs7z\include\bitmemextractor.hpp"
#include "libs7z\include\bitarchiveinfo.hpp"
#include "misc.h"

//typedef std::map< bit7z::wstring, std::vector<bit7z::byte_t>> extracting_rezult;
typedef std::vector<bit7z::byte_t> bytes_vector;

bytes_vector bytes_to_vector(const char* bytes_pointer, long long int size);

class Archive
{
	bytes_vector arch_vector;
	std::size_t arch_raw_len;
	bit7z::BitArchiveInfo arch_informator;
	std::map<bit7z::BitProperty, bit7z::BitPropVariant> arch_properties;

	std::vector< bit7z::BitArchiveItem > files;
	std::size_t files_count;

public:
	Archive() = delete;
	Archive(bytes_vector bv);
	Archive(char* data, std::size_t len);
	std::wstring filepath(int num);
	std::size_t filesize(int num);
	bytes_vector extract_filedata(int num);
	std::size_t save_to_file(int num, const std::wstring& path);
	std::size_t files_in_arch();
	bit7z::BitArchiveInfo& arch_info();
	~Archive();
};

