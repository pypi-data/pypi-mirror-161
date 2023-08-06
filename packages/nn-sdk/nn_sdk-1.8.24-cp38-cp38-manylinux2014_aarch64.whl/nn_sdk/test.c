#include <stdio.h>
#include "nn_sdk.h"

int main(){
    if (0 != sdk_init_cc()) {
		return -1;
	}
    printf("配置参考 python.........\n");
	const char* json_data = "{\n\
    \"model_dir\": \"/root/model.ckpt\",\n\
    \"log_level\":8, \n\
     \"device_id\":0, \n\
    \"tf\":{ \n\
         \"ConfigProto\": {\n\
            \"log_device_placement\":0,\n\
            \"allow_soft_placement\":1,\n\
            \"gpu_options\":{\"allow_growth\": 1}\n\
        },\n\
        \"engine_version\": 1,\n\
        \"model_type\":1 ,\n\
    },\n\
    \"graph\": [\n\
        {\n\
            \"input\": [{\"node\":\"input_ids:0\", \"data_type\":\"float\", \"shape\":[1, 10]}],\n\
            \"output\" : [{\"node\":\"pred_ids:0\", \"data_type\":\"float\", \"shape\":[1, 10]}]\n\
        }\n\
    ]\n\
}";
	printf("%s\n", json_data);
	auto handle = sdk_new_cc(json_data);
	const int INPUT_NUM = 1;
	const int OUTPUT_NUM = 1;
	const int M = 1;
	const int N = 10;
	int *input[INPUT_NUM] = { 0 };
	float* result[OUTPUT_NUM] = { 0 };
	int element_input_size = sizeof(int);
	int element_output_size = sizeof(float);
	for (int i = 0; i < OUTPUT_NUM; ++i) {
		result[i] = (float*)malloc(M * N * element_output_size);
		memset(result[i], 0, M * N * element_output_size);
	}
	for(int i =0;i<INPUT_NUM;++i){
		input[i] = (int*)malloc(M * N * element_input_size);
		memset(input[i], 0, M * N * element_input_size);
		for (int j = 0; j < N; ++j) {
			input[i][j] = i;
		}
	}

    int batch_size = 1;
	int code = sdk_process_cc(handle,  0 , batch_size, (void**)input,(void**)result);
	if (code == 0) {
		printf("result\n");
		for (int i = 0; i < N; ++i) {
			printf("%f ", result[0][i]);
		}
		printf("\n");
	}
	for (int i = 0; i < INPUT_NUM; ++i) {
		free(input[i]);
	}
	for (int i = 0; i < OUTPUT_NUM; ++i) {
		free(result[i]);
	}
	sdk_delete_cc(handle);
	sdk_uninit_cc();
	return 0;
}