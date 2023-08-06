#pragma once
#define _SILENCE_CXX17_CODECVT_HEADER_DEPRECATION_WARNING
#include <codecvt>
#include <Windows.h>

std::string wstring_to_utf8(const std::wstring& str);
std::wstring utf8_to_wstring(const std::string& str);
HMODULE GetCurrentModule();