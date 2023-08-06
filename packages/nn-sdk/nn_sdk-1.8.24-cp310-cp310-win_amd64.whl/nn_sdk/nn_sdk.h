#ifndef __CC_SDK_H__
#define __CC_SDK_H__

#include <stdio.h>


#ifdef _WIN32
#ifdef SDK_CC_EXPORT_
#define SDK_CC_EXPORT _declspec( dllexport )
#else
#define SDK_CC_EXPORT _declspec(dllimport)
#endif
#else
#define SDK_CC_EXPORT
#endif // _WIN32



#ifdef __cplusplus
extern "C" {
#endif

	typedef long long SDK_HANDLE_CC;

	SDK_CC_EXPORT int sdk_init_cc();

	SDK_CC_EXPORT int sdk_uninit_cc();

	SDK_CC_EXPORT SDK_HANDLE_CC sdk_new_cc(const char* json);

	SDK_CC_EXPORT int sdk_delete_cc(SDK_HANDLE_CC handle);
	
	//input_buffer_list N 个一维数组, final_result N个一维数组
	SDK_CC_EXPORT int sdk_process_cc(SDK_HANDLE_CC handle, int net_stage, int batch_size,void** input_buffer_list, void** final_result);

#ifdef __cplusplus
}
#endif


#endif