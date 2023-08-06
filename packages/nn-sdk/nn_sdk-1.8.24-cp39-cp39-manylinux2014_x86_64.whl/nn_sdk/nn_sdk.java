package nn_sdk;

//输入缓冲区 自定义 可自定义改
class nn_buffer_batch{
	  //输入 输出内存节点，名字跟图配置一样，根据图对象修改。
	public float [] input_ids = null;//推理图的输入,
	public float[] pred_ids =   null;//推理的结果保存

	public int batch_size = 1;
	public nn_buffer_batch(int batch_size_){
		this.input_ids = new float[batch_size_ * 10];
		this.pred_ids =  new float[batch_size_ * 10];
		this.batch_size = batch_size_;
		for(int i =0;i<1 * 10;i++) {
			this.input_ids[i] = 1;
			this.pred_ids[i] = 0;
		}
	}
}


//包名必须是nn_sdk
public class nn_sdk {
	//推理函数
	public native static int  sdk_init_cc();
	public native static int  sdk_uninit_cc();
	public native static long sdk_new_cc(String json);
	public native static int  sdk_delete_cc(long handle);
	//nn_buffer_batch 类
	public native static int sdk_process_cc(long handle, int net_state,int batch_size, nn_buffer_batch buffer);

	static {
		//动态库的绝对路径windows是engine_csdk.pyd , linux是 engine_csdk.so
		System.load("engine_csdk.pyd");
	}

	public static void main(String[] args){
		System.out.println("java main...........");

	   nn_sdk instance = new nn_sdk();

	   nn_buffer_batch buf = new nn_buffer_batch(2);
	   sdk_init_cc();

	   String json = "{\r\n"
	   + "    \"model_dir\": r'model.ckpt',\r\n"
	   + "    \"aes\":{\r\n"
	   + "        \"use\":False,\r\n"
	   + "        \"key\":bytes([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]),\r\n"
	   + "        \"iv\":bytes([0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]),\r\n"
	   + "    },\r\n"
	   + "    \"log_level\": 4,# fatal 1 , error 2 , info 4 , debug 8\r\n"
	   + "    'engine':0, # 0 tensorflow,  1 onnx , 2  tensorrt , 3 fasttext\r\n"
	   + "    \"device_id\": 0,\r\n"
	   + "    'tf':{\r\n"
	   + "        #tensorflow2 ConfigProto无效\r\n"
	   + "        \"ConfigProto\": {\r\n"
	   + "            \"log_device_placement\": False,\r\n"
	   + "            \"allow_soft_placement\": True,\r\n"
	   + "            \"gpu_options\": {\r\n"
	   + "                \"allow_growth\": True\r\n"
	   + "            },\r\n"
	   + "            \"graph_options\":{\r\n"
	   + "                \"optimizer_options\":{\r\n"
	   + "                    \"global_jit_level\": 1\r\n"
	   + "                }\r\n"
	   + "            },\r\n"
	   + "        },\r\n"
	   + "        \"engine_version\": 1, # tensorflow版本\r\n"
	   + "        \"model_type\": 1,# 0 pb , 1 ckpt\r\n"
	   + "        \"saved_model\":{ # 当model_type为pb模型有效, 普通pb use=False ， 如果是saved_model冻结模型 , 则需启用use并且配置tags\r\n"
	   + "            'use': False, # 是否启用saved_model\r\n"
	   + "            'tags': ['serve'],\r\n"
	   + "            'signature_key': 'serving_default',\r\n"
	   + "        },\r\n"
	   + "        \"fastertransformer\":{\r\n"
	   + "            \"use\": False,\r\n"
	   + "            \"cuda_version\":\"11.3\", #当前依赖 tf2pb,支持10.2 11.3 ,\r\n"
	   + "        }\r\n"
	   + "    },\r\n"
	   + "    'onnx':{\r\n"
	   + "        \"engine_version\": 1,# onnxruntime 版本\r\n"
	   + "    },\r\n"
	   + "    'trt':{\r\n"
	   + "        \"engine_version\": 8,# tensorrt 版本\r\n"
	   + "        \"enable_graph\": 0,\r\n"
	   + "    },\r\n"
	   + "    'fasttext': {\r\n"
	   + "        \"engine_version\": 0,# fasttext主版本\r\n"
	   + "        \"threshold\":0, # 预测k个标签的阈值\r\n"
	   + "        \"k\":1, # 预测k个标签\r\n"
	   + "        \"dump_label\": 1, #输出内部标签，用于上层解码\r\n"
	   + "        \"predict_label\": 1, #获取预测标签 1  , 获取向量  0\r\n"
	   + "    },\r\n"
	   + "    \"graph\": [\r\n"
	   + "        {\r\n"
	   + "            # 对于Bert模型 shape [max_batch_size,max_seq_lenth],\r\n"
	   + "            # 其中max_batch_size 用于c++ java开辟输入输出缓存,输入不得超过max_batch_size，对于python没有作用，取决于上层用户真实输入\r\n"
	   + "            # python限制max_batch_size 在上层用户输入做\r\n"
	   + "            # 对于fasttext node 对应name可以任意写，但不能少\r\n"
	   + "            \"input\": [\r\n"
	   + "                {\"node\":\"input_ids:0\", \"data_type\":\"float\", \"shape\":[1, 10]},\r\n"
	   + "            ],\r\n"
	   + "            \"output\": [\r\n"
	   + "                {\"node\":\"pred_ids:0\", \"data_type\":\"float\", \"shape\":[1, 10]},\r\n"
	   + "            ],\r\n"
	   + "        }\r\n"
	   + "    ]}";



	  System.out.println(json);

	  long handle = sdk_new_cc(json);
	  System.out.printf("handle: %d\n",handle);

	  int code = sdk_process_cc(handle,0,buf.batch_size,buf);
	  System.out.printf("sdk_process_cc %d \n" ,code);
	  if(code == 0) {
		  for(int i = 0;i<20 ; i++) {
			  System.out.printf("%f ",buf.pred_ids[i]);
		  }
		  System.out.println();
	  }
	  sdk_delete_cc(handle);
	   sdk_uninit_cc();
	   System.out.println("end");
	}
}
