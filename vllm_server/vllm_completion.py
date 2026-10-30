from vllm import LLM, SamplingParams
import os
from time import sleep
from transformers import AutoTokenizer
import torch

class VLLMCompletion(object):
    def __init__(
            self,
            model_name="deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",
            eos_token="<|endoftext|>",
            api_key=None,  # kept for interface compatibility
            control_thinking=False,
            seed=0  # added for the reproduction: explicit engine seed (vLLM 0.7.x default is 0)
    ):

        self.model_name = model_name
        self.eos_token = eos_token
        self.control_thinking = control_thinking
        
        # Initialize vLLM engine
        MY_GPU_COUNT = torch.cuda.device_count()
        print(f"MY_GPU_COUNT: {MY_GPU_COUNT}")
        
        # Initialize vLLM using the new LLM class
        self.engine = LLM(
            model=model_name,
            gpu_memory_utilization=0.95,
            max_model_len=32768,
            tensor_parallel_size=MY_GPU_COUNT,
            disable_custom_all_reduce=True,
            seed=seed
        )
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)

    def _generate(self, prompt, sampling_params):
        outputs = self.engine.generate(prompt, sampling_params)

        results = []
        for output in outputs:
            for generated_output in output.outputs:
                results.append(generated_output.text)
        return results

    def completion_chat_batch(self, messages_list, max_tokens=32768, temperature=1, top_p=1, n=2):
        """Added for the reproduction: same prompt formatting and sampling as completion_chat,
        but all prompts go to vLLM in one generate() call. Returns one list of n responses per prompt,
        in input order. No silent retry loop: errors (e.g. out of memory) stop the job visibly."""
        print(f"batch args: prompts={len(messages_list)}, max_tokens={max_tokens}, temperature={temperature}, top_p={top_p}, n={n}")
        sampling_params = SamplingParams(max_tokens=max_tokens, temperature=temperature, top_p=top_p, n=n)
        prompts = [self._format_prompt(m) for m in messages_list]
        outputs = self.engine.generate(prompts, sampling_params)
        return [[o.text for o in out.outputs] for out in outputs]

    def _format_prompt(self, messages):
        if self.control_thinking:
            base_message = self.tokenizer.decode(self.tokenizer.apply_chat_template(messages, add_generation_prompt=True))
            return base_message + 'Okay, I think I have finished thinking.' + "\n</think>\n"
        return self.tokenizer.decode(self.tokenizer.apply_chat_template(messages, add_generation_prompt=True))

    def completion_chat(self, messages, top_passages=None, max_tokens=32768, temperature=1, top_p=1, n=2):
        print(f"args: max_tokens={max_tokens}, temperature={temperature}, top_p={top_p}, n={n}")
        def parse_messages(messages):
            if self.control_thinking:
                print('Adding no-thinking messages.')
                base_message = self.tokenizer.decode(self.tokenizer.apply_chat_template(messages, add_generation_prompt=True))
                return base_message + 'Okay, I think I have finished thinking.' + "\n</think>\n"
            else:
                return self.tokenizer.decode(self.tokenizer.apply_chat_template(messages, add_generation_prompt=True))

        sampling_params = SamplingParams(
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            n=n
        )

        prompt = parse_messages(messages)
        print(f"INPUT TO the model: {prompt}")
        get_result = False
        while not get_result:
            try:
                responses = self._generate(prompt, sampling_params)
                get_result = True
            except:
                sleep(1)

        return responses 

